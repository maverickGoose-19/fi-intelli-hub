# Deployment Checklist

## Pre-Deploy

- confirm `python3 -m unittest discover -s tests` passes in `app/backend`
- confirm `npm run build` passes in `app/frontend`
- verify `README.md` and docs reflect current behavior
- review the current-vs-target architecture notes in `docs/tech-spec.md`
- confirm `.env` values are set for target environment
- confirm `NEXT_PUBLIC_API_BASE_URL` points to deployed API

## Backend Readiness

- provision Python runtime and install backend dependencies
- set `LOCAL_TIMEZONE`
- set `OPENF1_BASE_URL` if overriding default
- set `APP_ENV=production`
- run FastAPI behind a production process manager and reverse proxy
- enable request logs and error logs

## Frontend Readiness

- install frontend dependencies with clean lockfile
- run `npm run build`
- serve with `next start` or platform-native Next.js hosting
- confirm dashboard and admin routes render in production mode

## Runtime Data

- decide whether to allow file-based runtime cache in deployment
- if keeping file cache temporarily, ensure write access for `app/backend/data`
- if using ephemeral infrastructure, accept that runtime cache may reset between deploys

## Security

- restrict CORS to known origins before public launch
- add authentication for admin/editorial routes before exposing publicly
- validate external article sources remain trusted
- avoid storing secrets in repo or committed env files

## Observability

- add uptime checks for frontend and backend
- add error monitoring for backend sync failures
- log sync mode, outcome, and degraded fallbacks
- alert on repeated OpenF1 or article-ingestion failures

## Functional Smoke Test

- load homepage
- confirm standings render
- run `Quick sync`
- run `Full sync`
- confirm article feed updates after full sync
- confirm admin/editorial page loads
- confirm completed weekend selector works

## Post-Deploy Follow-Up

- inspect logs after first sync
- confirm Friday auto-sync behavior in target timezone
- verify runtime cache behavior after restart
- capture known limitations for the next release:
  - file-based cache
  - no auth on editorial
  - no background worker queue
