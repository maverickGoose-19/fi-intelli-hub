# Technical Specification

## Architecture Summary

The application is split into a Next.js frontend and a FastAPI backend. The backend is the source of truth for dashboard payload assembly, syncing, editorial clustering, and summary generation. The frontend renders a server-driven dashboard with seeded fallbacks for resilience.

## Architecture Status

### Current architecture

- Next.js frontend served separately from a FastAPI backend
- file-backed runtime cache for synced state
- request-triggered sync execution
- unauthenticated admin and editorial routes
- deterministic summary generation instead of provider-backed LLM summarization

### Target production architecture

- Next.js frontend behind CDN or managed app hosting
- FastAPI backend behind a reverse proxy with structured logging and metrics
- Postgres for runtime state, editorial state, and historical snapshots
- background worker or scheduler for OpenF1 and article ingestion
- authenticated admin/editorial access with role-based controls
- source monitoring, retry policies, and operational alerting

## System Components

### Frontend

- framework: Next.js App Router
- language: TypeScript
- styling: Tailwind CSS
- rendering model: server-rendered dashboard with selective client components for interactions

Key areas:

- `app/page.tsx`: main season dashboard
- `app/admin/page.tsx`: editorial workbench
- `components/sync-button.tsx`: quick/full sync controls
- `components/completed-weekend-results.tsx`: completed weekend selector
- `components/performance-charts.tsx`: top-contender chart panels

### Backend

- framework: FastAPI
- data layer: in-memory repository backed by seeded JSON plus runtime cache
- sync services:
  - OpenF1 session/standings sync
  - article link ingestion
- editorial services:
  - clustering by `cluster_hint`
  - deterministic summary generation
  - label and editorial-state patching

Key modules:

- `app/main.py`: API routes
- `app/repository.py`: orchestration and state management
- `app/services/openf1.py`: OpenF1 sync and derived payload generation
- `app/services/articles.py`: article ingestion from external sources
- `app/services/dashboard.py`: dashboard response shaping

## Data Flow

### Dashboard request

1. frontend requests `GET /api/dashboard/current`
2. backend optionally runs Friday auto-sync
3. repository assembles current weekend, prior weekend, clusters, documents, sources, and season state
4. dashboard payload is returned to frontend
5. frontend merges live payload over seeded fallback data where needed

### Quick sync

1. frontend posts to `POST /api/sync/openf1?include_articles=false`
2. backend refreshes OpenF1 session and standings data
3. backend persists updated runtime cache
4. frontend refreshes dashboard

### Full sync

1. frontend posts to `POST /api/sync/openf1?include_articles=true`
2. backend refreshes OpenF1 data
3. backend ingests article links
4. backend rebuilds current-weekend editorial clusters and summaries
5. backend persists runtime cache
6. frontend refreshes dashboard and editorial surfaces

## API Surface

- `GET /health`
- `GET /api/dashboard/current`
- `GET /api/clusters`
- `GET /api/clusters/{cluster_id}`
- `GET /api/sources`
- `GET /api/entities`
- `GET /api/weekends/current`
- `GET /api/sync/status`
- `POST /api/sync/openf1`
- `POST /api/clusters/{cluster_id}/resummarize`
- `PATCH /api/summaries/{summary_id}`

## Sync Behavior

### OpenF1

- base URL normalized to support configs with or without `/v1`
- optional endpoint `404`s degrade gracefully instead of failing the full dashboard
- standings and chart data fall back to cached or seeded state when incomplete

### Article ingestion

- sources are scraped by link extraction and allowlisted path fragments
- article ingestion is only part of full sync
- per-source ingestion is capped
- synced article documents can now enter the editorial queue automatically

## Editorial Model

Cluster labels:

- `official_update`
- `race_result`
- `analysis`
- `prediction`

Editorial statuses:

- `draft`
- `review_required`
- `approved`

Behavior:

- stable clusters preserve editorial status where possible
- summaries are regenerated from the current source set
- admin users can relabel or resummarize through the workbench

## Production Readiness Improvements Completed

- removed generated runtime/build artifacts from the repo
- added ignore rule for runtime cache
- added separate quick/full sync modes
- added graceful degradation for OpenF1 `404`s
- added article-to-editorial refresh on full sync
- tightened article ingestion performance with per-source counters
- added outbound user-agent headers for sync requests
- simplified some frontend and repository paths

## Current Constraints

- runtime cache is file-based, not database-backed
- admin endpoints are unauthenticated
- article ingestion is link-level, not full content extraction
- no background worker or job scheduler outside request-triggered flow

## Recommended Next Steps

1. replace JSON runtime cache with Postgres tables
2. run syncs via scheduled workers instead of request path execution
3. add auth and role checks for editorial endpoints
4. add structured logs, metrics, and source health dashboards
5. move article ingestion to full-content extraction plus entity tagging
