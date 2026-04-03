from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.repository import SeedRepository


class SummaryPatchPayload(BaseModel):
    label: str | None = None
    title: str | None = None
    body: str | None = None
    editorial_status: str | None = None


app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
repository = SeedRepository()


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/dashboard/current")
def get_dashboard_current() -> dict[str, Any]:
    return repository.get_dashboard_current()


@app.get("/api/predictions/next-race")
def get_prediction_analytics() -> dict[str, Any]:
    return repository.get_prediction_analytics()


@app.get("/api/clusters")
def get_clusters(weekend_id: str | None = None) -> dict[str, Any]:
    return {"items": repository.list_clusters(weekend_id=weekend_id)}


@app.get("/api/clusters/{cluster_id}")
def get_cluster(cluster_id: str) -> dict[str, Any]:
    try:
        return {"cluster": repository.get_cluster(cluster_id)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/api/sources")
def get_sources() -> dict[str, Any]:
    return {"items": repository.list_sources()}


@app.get("/api/entities")
def get_entities() -> dict[str, Any]:
    return {"items": repository.list_entities()}


@app.get("/api/weekends/current")
def get_current_weekend() -> dict[str, Any]:
    weekend = repository.get_current_weekend()
    return {"weekend": weekend, "timeline": weekend["phases"]}


@app.post("/api/ingest/run")
def run_ingest() -> dict[str, Any]:
    return repository.run_ingest()


@app.get("/api/sync/status")
def get_sync_status() -> dict[str, Any]:
    return {"sync": repository.get_sync_status()}


@app.post("/api/sync/openf1")
def sync_openf1(force: bool = True, include_articles: bool = True) -> dict[str, Any]:
    try:
        return {
            "sync": repository.sync_openf1(
                force=force,
                reason="manual",
                include_articles=include_articles,
            )
        }
    except Exception as error:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(error)) from error


@app.post("/api/clusters/{cluster_id}/resummarize")
def resummarize_cluster(cluster_id: str) -> dict[str, Any]:
    try:
        return {"cluster": repository.resummarize_cluster(cluster_id)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.patch("/api/summaries/{summary_id}")
def patch_summary(summary_id: str, payload: SummaryPatchPayload) -> dict[str, Any]:
    try:
        updated = repository.patch_summary(summary_id, payload.model_dump())
        return {"summary": updated}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
