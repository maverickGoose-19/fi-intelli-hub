from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any
from urllib.error import HTTPError
from zoneinfo import ZoneInfo

from app.config import settings
from app.seed import load_seed_data
from app.services.clustering import cluster_documents_by_hint, deduplicate_documents
from app.services.dashboard import build_dashboard_payload
from app.services.editorial import apply_summary_patch
from app.services.predictions import RaceWinnerPredictionService
from app.services.articles import ArticleSyncService
from app.services.openf1 import OpenF1SyncService
from app.services.summarization import generate_cluster_summary


class SeedRepository:
    def __init__(self) -> None:
        self.openf1_sync = OpenF1SyncService()
        self.article_sync = ArticleSyncService()
        self.prediction_service = RaceWinnerPredictionService()
        self.data = self._load_initial_data()
        self.data.setdefault(
            "sync",
            {
                "source": "seed",
                "last_attempt_at": None,
                "last_success_at": None,
                "status": "idle",
                "message": "No OpenF1 sync has run yet.",
            },
        )

    def _load_initial_data(self) -> dict[str, Any]:
        seed_data = load_seed_data()
        cache_path = settings.runtime_cache_path
        if cache_path.exists():
            with cache_path.open("r", encoding="utf-8") as handle:
                cached_data = json.load(handle)
            return self._repair_cached_schedule(cached_data, seed_data)
        return seed_data

    def _repair_cached_schedule(
        self,
        cached_data: dict[str, Any],
        seed_data: dict[str, Any],
    ) -> dict[str, Any]:
        repaired = deepcopy(cached_data)
        seed_sessions = deepcopy(seed_data.get("season", {}).get("next_race_sessions", []))
        seed_next_race_name = seed_data.get("season", {}).get("next_race_name")
        if not seed_sessions or not seed_next_race_name:
            return repaired

        next_race = repaired.get("season", {}).get("next_race")
        if isinstance(next_race, dict) and next_race.get("name") == seed_next_race_name:
            if self._needs_schedule_repair(next_race.get("sessions")):
                next_race["sessions"] = deepcopy(seed_sessions)

        season_payload = repaired.get("season", {})
        if self._needs_schedule_repair(season_payload.get("next_race_sessions")):
            season_payload["next_race_sessions"] = deepcopy(seed_sessions)

        for weekend in repaired.get("weekends", []):
            if weekend.get("current") and weekend.get("name") == seed_next_race_name:
                if self._needs_schedule_repair(weekend.get("next_sessions")):
                    weekend["next_sessions"] = deepcopy(seed_sessions)

        return repaired

    def _needs_schedule_repair(self, sessions: Any) -> bool:
        if not isinstance(sessions, list) or not sessions:
            return True
        timezone_labels = (" PDT", " PST", " EDT", " EST", " CDT", " CST", " MDT", " MST", " UTC", " GMT")
        return any(not str(session.get("time_local", "")).endswith(timezone_labels) for session in sessions)

    def _persist_data(self) -> None:
        cache_path = settings.runtime_cache_path
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("w", encoding="utf-8") as handle:
            json.dump(self.data, handle, ensure_ascii=True, indent=2)

    def _now_local(self) -> datetime:
        return datetime.now(ZoneInfo(settings.local_timezone))

    def _update_sync_status(self, **updates: Any) -> None:
        self.data.setdefault("sync", {})
        self.data["sync"].update(updates)
        self._persist_data()

    def _should_auto_sync_today(self) -> bool:
        now = self._now_local()
        if now.weekday() not in settings.auto_sync_days:
            return False
        if not (settings.auto_sync_start_hour <= now.hour < settings.auto_sync_end_hour):
            return False
        last_success_at = self.data.get("sync", {}).get("last_success_at")
        if not last_success_at:
            return True
        return str(last_success_at)[:10] != now.date().isoformat()

    def _maybe_auto_sync(self) -> None:
        if not self._should_auto_sync_today():
            return
        self.sync_openf1(force=False, reason="scheduled_friday")

    def sync_openf1(
        self,
        force: bool = False,
        reason: str = "manual",
        include_articles: bool = True,
    ) -> dict[str, Any]:
        now = self._now_local().isoformat()
        mode = "full" if include_articles else "data_only"
        self._update_sync_status(
            source="openf1",
            last_attempt_at=now,
            status="running",
            message=f"OpenF1 {mode.replace('_', ' ')} sync started ({reason}).",
        )
        try:
            updated = self.openf1_sync.sync(self.data, now=self._now_local())
            current_weekend = next((weekend for weekend in updated["weekends"] if weekend.get("current")), None)
            if include_articles and current_weekend:
                article_documents = self.article_sync.sync_articles(current_weekend["id"])
                updated["documents"] = self._merge_documents(updated["documents"], article_documents)
            updated["sync"] = {
                "source": "openf1",
                "last_attempt_at": now,
                "last_success_at": self._now_local().isoformat(),
                "status": "success",
                "message": (
                    "Manual OpenF1 sync completed successfully."
                    if reason == "manual" and include_articles
                    else "Manual OpenF1 quick sync completed successfully."
                    if reason == "manual"
                    else "Scheduled weekend-morning OpenF1 sync completed successfully."
                ),
            }
            self.data = updated
            if include_articles:
                self._refresh_editorial_assets()
            self._persist_data()
            return deepcopy(self.data["sync"])
        except Exception as error:  # noqa: BLE001
            if self._is_known_sync_fallback(error):
                self._update_sync_status(
                    source="openf1",
                    status="degraded",
                    message=self._fallback_sync_message(error),
                )
                return deepcopy(self.data["sync"])
            self._update_sync_status(
                source="openf1",
                status="error",
                message=f"OpenF1 sync failed: {error}",
            )
            if force:
                raise
            return deepcopy(self.data["sync"])

    def get_sync_status(self) -> dict[str, Any]:
        return deepcopy(self.data.get("sync", {}))

    def _is_known_sync_fallback(self, error: Exception) -> bool:
        if isinstance(error, HTTPError) and error.code in {404, 429}:
            return True
        return isinstance(error, ValueError)

    def _fallback_sync_message(self, error: Exception) -> str:
        if isinstance(error, HTTPError) and error.code == 404:
            return (
                "OpenF1 did not return one of the requested endpoints right now. "
                "The dashboard kept the current cached data instead of failing."
            )
        if isinstance(error, HTTPError) and error.code == 429:
            return (
                "OpenF1 rate-limited the sync request. "
                "The dashboard kept the latest cached snapshot instead of failing."
            )
        return (
            "OpenF1 did not return enough data for a full refresh. "
            "The dashboard kept the current cached snapshot."
        )

    def _index_by_id(self, collection_name: str) -> dict[str, dict[str, Any]]:
        return {item["id"]: item for item in self.data[collection_name]}

    def _weekend_lookup(self) -> dict[str, dict[str, Any]]:
        return {item["id"]: item for item in self.data["weekends"]}

    def _merge_documents(
        self, existing_documents: list[dict[str, Any]], new_documents: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        merged = {document["url"]: deepcopy(document) for document in existing_documents}
        for document in new_documents:
            merged.setdefault(document["url"], deepcopy(document))
        return sorted(merged.values(), key=lambda item: item["publish_time"], reverse=True)

    def _sanitize_slug(self, value: str) -> str:
        cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return cleaned or "cluster"

    def _infer_cluster_label(self, documents: list[dict[str, Any]], existing_label: str | None = None) -> str:
        if existing_label:
            return existing_label
        kinds = {document.get("kind") for document in documents}
        stances = {document.get("stance") for document in documents}
        if any(kind in {"race_report", "race_result"} for kind in kinds):
            return "race_result"
        if "prediction" in stances:
            return "prediction"
        if "analysis" in stances:
            return "analysis"
        return "official_update"

    def _default_editorial_status(self, label: str) -> str:
        if label in {"official_update", "race_result"}:
            return "approved"
        if label == "analysis":
            return "review_required"
        return "draft"

    def _build_cluster_metadata(self, label: str) -> dict[str, Any]:
        metadata = {
            "official_update": {"status": "confirmed", "freshness": "new", "confidence": 0.95, "trend": "rising"},
            "race_result": {"status": "confirmed", "freshness": "settled", "confidence": 0.99, "trend": "closed"},
            "analysis": {"status": "developing", "freshness": "live", "confidence": 0.86, "trend": "rising"},
            "prediction": {"status": "watchlist", "freshness": "live", "confidence": 0.66, "trend": "watch"},
        }
        return metadata.get(label, metadata["analysis"])

    def _refresh_editorial_assets(self) -> None:
        current_weekend = self.get_current_weekend()
        current_weekend_id = current_weekend["id"]
        previous_weekend = self.get_previous_weekend(current_weekend_id)
        previous_weekend_id = previous_weekend["id"] if previous_weekend else None

        existing_clusters = {cluster["id"]: deepcopy(cluster) for cluster in self.data["clusters"]}
        existing_summaries = {summary["cluster_id"]: deepcopy(summary) for summary in self.data["summary_outputs"]}
        source_lookup = self._index_by_id("sources")
        entity_lookup = self._index_by_id("entities")
        current_documents = deduplicate_documents(
            [document for document in self.data["documents"] if document.get("weekend_id") == current_weekend_id]
        )
        grouped = cluster_documents_by_hint(current_documents)

        rebuilt_clusters: list[dict[str, Any]] = []
        rebuilt_summaries: list[dict[str, Any]] = []

        for hint, documents in sorted(grouped.items()):
            first_document = documents[0]
            cluster_id = hint if hint.startswith("cluster_") else f"cluster_{self._sanitize_slug(hint)}"
            existing_cluster = existing_clusters.get(cluster_id)
            existing_summary = existing_summaries.get(cluster_id)
            label = self._infer_cluster_label(
                documents,
                existing_label=existing_cluster["label"] if existing_cluster else None,
            )
            cluster_title = existing_cluster["title"] if existing_cluster else first_document["title"]
            entity_ids = sorted({entity_id for document in documents for entity_id in document.get("entity_ids", [])})
            cluster = {
                "id": cluster_id,
                "weekend_id": current_weekend_id,
                "slug": existing_cluster["slug"] if existing_cluster else self._sanitize_slug(cluster_title),
                "title": cluster_title,
                "label": label,
                "race_stage": first_document.get("race_stage") or current_weekend["stage"],
                "summary_output_id": (
                    existing_cluster["summary_output_id"] if existing_cluster else f"summary_{cluster_id}"
                ),
                "document_ids": [document["id"] for document in documents],
                "entity_ids": entity_ids,
                **self._build_cluster_metadata(label),
            }
            source_ids = sorted({document["source_id"] for document in documents})
            summary_generated = generate_cluster_summary(
                cluster=cluster,
                documents=documents,
                sources=[source_lookup[source_id] for source_id in source_ids if source_id in source_lookup],
                entities=[entity_lookup[entity_id] for entity_id in entity_ids if entity_id in entity_lookup],
            )
            rebuilt_clusters.append(cluster)
            rebuilt_summaries.append(
                {
                    "id": cluster["summary_output_id"],
                    "cluster_id": cluster_id,
                    "label": label,
                    "title": summary_generated["title"],
                    "body": summary_generated["body"],
                    "editorial_status": (
                        existing_summary["editorial_status"]
                        if existing_summary
                        else self._default_editorial_status(label)
                    ),
                    "updated_at": summary_generated["updated_at"],
                }
            )

        preserved_clusters = [
            deepcopy(cluster)
            for cluster in self.data["clusters"]
            if cluster["weekend_id"] != current_weekend_id
            and (
                previous_weekend_id is None
                or cluster["weekend_id"] == previous_weekend_id
                or cluster["label"] == "race_result"
            )
        ]
        preserved_summary_ids = {cluster["summary_output_id"] for cluster in preserved_clusters}
        preserved_summaries = [
            deepcopy(summary)
            for summary in self.data["summary_outputs"]
            if summary["id"] in preserved_summary_ids
        ]

        self.data["clusters"] = preserved_clusters + rebuilt_clusters
        self.data["summary_outputs"] = preserved_summaries + rebuilt_summaries
        self.data["distribution_assets"] = [
            {
                "id": f"asset_{summary['id']}",
                "summary_output_id": summary["id"],
                "kind": "digest_card",
                "title": summary["title"],
                "body": summary["body"],
            }
            for summary in rebuilt_summaries[:6]
        ]

    def list_sources(self) -> list[dict[str, Any]]:
        return deepcopy(sorted(self.data["sources"], key=lambda item: item["name"]))

    def list_entities(self) -> list[dict[str, Any]]:
        return deepcopy(sorted(self.data["entities"], key=lambda item: (item["kind"], item["name"])))

    def list_documents(self) -> list[dict[str, Any]]:
        return deepcopy(sorted(self.data["documents"], key=lambda item: item["publish_time"], reverse=True))

    def list_weekends(self) -> list[dict[str, Any]]:
        return deepcopy(self.data["weekends"])

    def get_current_weekend(self) -> dict[str, Any]:
        self._maybe_auto_sync()
        for weekend in self.data["weekends"]:
            if weekend.get("current"):
                return deepcopy(weekend)
        raise KeyError("No current weekend found")

    def get_previous_weekend(self, current_weekend_id: str) -> dict[str, Any] | None:
        weekends = [weekend for weekend in self.data["weekends"] if weekend["id"] != current_weekend_id]
        if not weekends:
            return None
        weekends.sort(key=lambda item: item["started_at"], reverse=True)
        return deepcopy(weekends[0])

    def _get_summary_by_id(self, summary_id: str) -> dict[str, Any]:
        for summary in self.data["summary_outputs"]:
            if summary["id"] == summary_id:
                return summary
        raise KeyError(f"Unknown summary: {summary_id}")

    def _replace_summary(self, updated_summary: dict[str, Any]) -> dict[str, Any]:
        for index, summary in enumerate(self.data["summary_outputs"]):
            if summary["id"] == updated_summary["id"]:
                self.data["summary_outputs"][index] = updated_summary
                self._persist_data()
                return updated_summary
        raise KeyError(f"Unknown summary: {updated_summary['id']}")

    def _build_cluster_view(self, cluster: dict[str, Any]) -> dict[str, Any]:
        summaries = self._index_by_id("summary_outputs")
        documents = self._index_by_id("documents")
        sources = self._index_by_id("sources")
        entities = self._index_by_id("entities")
        weekends = self._weekend_lookup()
        weekend = weekends.get(cluster["weekend_id"], self.get_current_weekend())

        related_documents = [deepcopy(documents[document_id]) for document_id in cluster["document_ids"] if document_id in documents]
        related_entities = [deepcopy(entities[entity_id]) for entity_id in cluster["entity_ids"] if entity_id in entities]
        source_ids = sorted({document["source_id"] for document in related_documents})
        related_sources = [deepcopy(sources[source_id]) for source_id in source_ids if source_id in sources]
        summary = deepcopy(summaries[cluster["summary_output_id"]])

        return {
            **deepcopy(cluster),
            "weekend": {
                "id": weekend["id"],
                "name": weekend["name"],
                "stage": weekend["stage"],
            },
            "summary": summary,
            "documents": related_documents,
            "entities": related_entities,
            "sources": related_sources,
            "source_count": len(related_sources),
            "document_count": len(related_documents),
        }

    def list_clusters(self, weekend_id: str | None = None) -> list[dict[str, Any]]:
        clusters = self.data["clusters"]
        if weekend_id:
            clusters = [cluster for cluster in clusters if cluster["weekend_id"] == weekend_id]
        enriched = [self._build_cluster_view(cluster) for cluster in clusters]
        return sorted(enriched, key=lambda item: item["summary"]["updated_at"], reverse=True)

    def get_cluster(self, cluster_id: str) -> dict[str, Any]:
        for cluster in self.data["clusters"]:
            if cluster["id"] == cluster_id:
                return self._build_cluster_view(cluster)
        raise KeyError(f"Unknown cluster: {cluster_id}")

    def get_dashboard_current(self) -> dict[str, Any]:
        self._maybe_auto_sync()
        current = self.get_current_weekend()
        previous = self.get_previous_weekend(current["id"])
        clusters = self.list_clusters(weekend_id=current["id"])
        race_result_clusters: list[dict[str, Any]] = []
        if previous:
            race_result_clusters = [
                cluster
                for cluster in self.list_clusters(weekend_id=previous["id"])
                if cluster["label"] == "race_result"
            ][:1]
        documents = [document for document in self.list_documents() if document["weekend_id"] == current["id"]]
        source_ids = sorted({document["source_id"] for document in documents})
        source_lookup = self._index_by_id("sources")
        sources = [source_lookup[source_id] for source_id in source_ids if source_id in source_lookup]
        payload = build_dashboard_payload(
            current,
            previous,
            clusters,
            race_result_clusters,
            documents,
            sources,
            self.data["season"],
        )
        payload["sync"] = self.get_sync_status()
        return payload

    def get_prediction_analytics(self) -> dict[str, Any]:
        self._maybe_auto_sync()
        current = self.get_current_weekend()
        previous = self.get_previous_weekend(current["id"])
        return self.prediction_service.build_prediction_payload(
            season=self.data["season"],
            current_weekend=current,
            previous_weekend=previous,
        )

    def run_ingest(self) -> dict[str, Any]:
        documents = self.list_documents()
        deduplicated = deduplicate_documents(documents)
        grouped = cluster_documents_by_hint(deduplicated)
        return {
            "status": "ok",
            "document_count": len(documents),
            "deduplicated_count": len(deduplicated),
            "cluster_candidates": len(grouped),
            "clusters": sorted(grouped.keys()),
        }

    def resummarize_cluster(self, cluster_id: str) -> dict[str, Any]:
        cluster = self.get_cluster(cluster_id)
        summary = generate_cluster_summary(
            cluster=cluster,
            documents=cluster["documents"],
            sources=cluster["sources"],
            entities=cluster["entities"],
        )
        updated_summary = apply_summary_patch(
            cluster["summary"],
            {"title": summary["title"], "body": summary["body"]},
        )
        self._replace_summary(updated_summary)
        return self.get_cluster(cluster_id)

    def patch_summary(self, summary_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        summary = self._get_summary_by_id(summary_id)
        updated_summary = apply_summary_patch(summary, patch)
        self._replace_summary(updated_summary)
        for cluster in self.data["clusters"]:
            if cluster["summary_output_id"] == summary_id and "label" in patch and patch["label"]:
                cluster["label"] = patch["label"]
        self._persist_data()
        return deepcopy(updated_summary)
