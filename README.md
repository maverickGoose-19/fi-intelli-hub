# F1 Intelligence Hub

F1 Intelligence Hub is a Formula 1 season intelligence app that combines race schedule context, standings, session results, article ingestion, editorial labeling, and lightweight prediction surfaces in a single dashboard.

## What It Does

- syncs OpenF1 session and standings data
- supports `Quick sync` for race data only
- supports `Full sync` for race data plus articles and editorial refresh
- separates `official_update`, `race_result`, `analysis`, and `prediction` surfaces
- shows completed-race timing/results, standings, team watch, charts, calendar, and article feed
- includes an editorial workbench for relabeling, approval state, and resummarization

## Tech Stack

- frontend: Next.js App Router, React, TypeScript, Tailwind CSS
- backend: FastAPI, pure-Python service layer
- data: seeded JSON fallback plus runtime cache from OpenF1/article syncs

## Repository Layout

```text
f1-intelli/
├── app/
│   ├── backend/
│   ├── docs/
│   ├── frontend/
│   └── shared/
├── docs/
│   ├── deployment-checklist.md
│   ├── prd.md
│   └── tech-spec.md
├── .env.example
└── README.md
```

## Local Development

### Backend

```bash
cd /Users/abhishekbhatnagar/Documents/First/f1-intelli/app/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

```bash
cd /Users/abhishekbhatnagar/Documents/First/f1-intelli/app/frontend
npm install
npm run dev
```

If the API is not running on `http://127.0.0.1:8000`, set `NEXT_PUBLIC_API_BASE_URL`.

## Sync Modes

- `Quick sync`: refreshes OpenF1 race/session/standings data only
- `Full sync`: refreshes OpenF1 data, ingests articles, and rebuilds editorial clusters

Friday auto-sync is enabled on the backend in `America/Los_Angeles`. The backend also keeps serving seed data or the last good runtime cache if external syncs fail.

## Quality Gates

### Backend tests

```bash
cd /Users/abhishekbhatnagar/Documents/First/f1-intelli/app/backend
python3 -m unittest discover -s tests
```

### Frontend production build

```bash
cd /Users/abhishekbhatnagar/Documents/First/f1-intelli/app/frontend
npm run build
```

## Docs

- [Product requirements](/Users/abhishekbhatnagar/Documents/First/f1-intelli/docs/prd.md)
- [Technical specification](/Users/abhishekbhatnagar/Documents/First/f1-intelli/docs/tech-spec.md)
- [Deployment checklist](/Users/abhishekbhatnagar/Documents/First/f1-intelli/docs/deployment-checklist.md)
- [Schema reference](/Users/abhishekbhatnagar/Documents/First/f1-intelli/app/docs/schema.sql)

## Production Notes

The codebase is cleaner and more deployment-friendly now, but this is still an MVP architecture. Before a public production launch, the highest-value next steps are:

- move runtime state from JSON cache to Postgres
- add background jobs instead of request-triggered syncs
- add auth for admin/editorial actions
- add structured logging and monitoring
- add stronger outbound fetch retries, rate limiting, and source health alerts

The current and target architecture are documented in more detail in [tech-spec.md](/Users/abhishekbhatnagar/Documents/First/f1-intelli/docs/tech-spec.md).
