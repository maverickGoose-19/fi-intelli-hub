# Backend

FastAPI backend for F1 Intelligence Hub.

## Responsibilities

- assemble the dashboard payload
- sync OpenF1 data
- optionally ingest articles
- rebuild editorial clusters on full sync
- expose admin/editorial patch endpoints

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,ml]"
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Core Endpoints

- `GET /health`
- `GET /api/dashboard/current`
- `GET /api/predictions/next-race`
- `GET /api/clusters`
- `GET /api/clusters/{cluster_id}`
- `GET /api/sources`
- `GET /api/entities`
- `GET /api/weekends/current`
- `GET /api/sync/status`
- `POST /api/sync/openf1?include_articles=false` for quick sync
- `POST /api/sync/openf1?include_articles=true` for full sync
- `POST /api/clusters/{cluster_id}/resummarize`
- `PATCH /api/summaries/{summary_id}`

## Notes

- runtime state is currently file-backed and persisted to `app/backend/data/runtime-cache.json`
- full sync rebuilds current-weekend editorial clusters from refreshed documents
- the prediction endpoint will use the historical ML stack when the backend is installed with the `ml` extra
- for broader project context, see the root [README](/Users/abhishekbhatnagar/Documents/First/f1-intelli/README.md) and docs under [docs](/Users/abhishekbhatnagar/Documents/First/f1-intelli/docs)
