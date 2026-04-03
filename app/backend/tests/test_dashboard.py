from __future__ import annotations

from datetime import datetime
import unittest
from zoneinfo import ZoneInfo

from app.seed import load_seed_data
from app.repository import SeedRepository


class DashboardPayloadTests(unittest.TestCase):
    def test_dashboard_includes_season_state_and_results(self) -> None:
        repository = SeedRepository()
        payload = repository.get_dashboard_current()

        self.assertEqual(payload["season"]["current_phase"], "between_races")
        self.assertEqual(payload["season"]["leader_team"], "Mercedes")
        self.assertEqual(payload["latest_weekend_results"]["name"], "2026 Japanese Grand Prix")
        self.assertGreater(len(payload["driver_standings"]), 10)
        self.assertGreater(len(payload["calendar"]), 10)
        self.assertIn("team_cars", payload)
        self.assertIn("article_feed", payload)
        self.assertIn("performance_charts", payload)
        self.assertGreater(len(payload["performance_charts"]["race_labels"]), 0)
        self.assertGreater(len(payload["performance_charts"]["points_series"]), 0)
        self.assertGreater(len(payload["performance_charts"]["points_series"][0]["values"]), 0)
        self.assertIn("completed_weekend_results", payload)
        self.assertGreater(len(payload["completed_weekend_results"]), 0)

    def test_editorial_assets_refresh_when_new_article_document_arrives(self) -> None:
        repository = SeedRepository()
        repository.data["documents"].append(
            {
                "id": "doc_test_editorial_article",
                "source_id": "source_the_race",
                "weekend_id": "weekend_mia_2026",
                "title": "McLaren brings a fresh floor concept to Miami",
                "url": "https://www.the-race.com/formula-1/mclaren-fresh-floor-concept-miami/",
                "kind": "analysis_article",
                "publish_time": "2026-04-02T18:00:00Z",
                "race_stage": "between_races",
                "stance": "analysis",
                "cluster_hint": None,
                "entity_ids": ["team_mclaren"],
                "content": "McLaren brings a fresh floor concept to Miami.",
            }
        )

        repository._refresh_editorial_assets()
        cluster = next(
            cluster
            for cluster in repository.list_clusters("weekend_mia_2026")
            if "doc_test_editorial_article" in cluster["document_ids"]
        )

        self.assertEqual(cluster["label"], "analysis")
        self.assertEqual(cluster["summary"]["editorial_status"], "review_required")

    def test_quick_sync_skips_article_refresh(self) -> None:
        repository = SeedRepository()
        updated = load_seed_data()
        updated["weekends"][0]["current"] = False
        updated["weekends"][1]["current"] = True

        repository.openf1_sync.sync = lambda base_data, now=None: updated  # type: ignore[assignment]

        def fail_article_sync(_weekend_id: str):
            raise AssertionError("article sync should not run during quick sync")

        repository.article_sync.sync_articles = fail_article_sync  # type: ignore[assignment]

        result = repository.sync_openf1(include_articles=False)

        self.assertEqual(result["status"], "success")
        self.assertIn("quick sync", result["message"].lower())

    def test_auto_sync_runs_on_weekend_mornings_only(self) -> None:
        repository = SeedRepository()
        repository._now_local = lambda: datetime(2026, 4, 4, 8, 0, tzinfo=ZoneInfo("America/Los_Angeles"))  # type: ignore[assignment]
        repository.data["sync"]["last_success_at"] = None

        self.assertTrue(repository._should_auto_sync_today())

        repository._now_local = lambda: datetime(2026, 4, 4, 14, 0, tzinfo=ZoneInfo("America/Los_Angeles"))  # type: ignore[assignment]
        self.assertFalse(repository._should_auto_sync_today())

        repository._now_local = lambda: datetime(2026, 4, 6, 8, 0, tzinfo=ZoneInfo("America/Los_Angeles"))  # type: ignore[assignment]
        self.assertFalse(repository._should_auto_sync_today())

    def test_auto_sync_only_runs_once_per_scheduled_day(self) -> None:
        repository = SeedRepository()
        repository._now_local = lambda: datetime(2026, 4, 5, 9, 0, tzinfo=ZoneInfo("America/Los_Angeles"))  # type: ignore[assignment]
        repository.data["sync"]["last_success_at"] = "2026-04-05T08:00:00-07:00"

        self.assertFalse(repository._should_auto_sync_today())


if __name__ == "__main__":
    unittest.main()
