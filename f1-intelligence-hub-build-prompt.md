# F1 Intelligence Hub Build Prompt

Use the prompt below with a coding model to build the webapp described in `f1-intelligence-hub.md`.

---

You are a senior full-stack engineer. Build a polished MVP of **F1 Intelligence Hub**, a race-week intelligence webapp that ingests official and trusted media sources, clusters overlapping stories, and turns them into source-backed F1 summaries with clear separation between **fact**, **analysis**, and **prediction**.

## Product Goal

This is **not** a generic sports news feed. It is an intelligence product for Formula 1 fans that helps users understand:

- what changed since the last race
- which updates are official
- which claims are interpretation or speculation
- how race-week context evolves from pre-race through post-race

The app should feel like a source-aware intelligence dashboard, not a blog homepage.

## Core Guardrails

These are non-negotiable:

- facts and predictions must never share the same label
- every summary must show source attribution
- recency must be obvious at a glance
- official sources should anchor truth, while media sources add context
- duplicate coverage should be clustered into one topic surface instead of repeated as separate cards

## Recommended Stack

Use this stack unless there is a strong reason not to:

- frontend: Next.js 15+ with App Router, TypeScript, Tailwind CSS, shadcn/ui
- backend: FastAPI + Python
- database: Postgres
- jobs/ingestion: Python background jobs or FastAPI task runner abstraction
- ORM: SQLAlchemy or SQLModel
- validation: Pydantic
- LLM layer: provider-agnostic summarization service with a clean adapter interface

If live external integrations slow down the build, use realistic seed data and mock adapters, but keep the code structured so real RSS/API ingestion can be plugged in later.

## What To Build

Build a functional MVP with:

1. A **Home / Race Week Dashboard**
   - hero section with current race-week status
   - cards for `official updates`, `race results`, `analysis`, and `predictions`
   - "what changed since last race" summary block
   - top clusters/trend cards
   - visible timestamps and source counts

2. A **Topic Cluster View**
   - grouped coverage around a single story
   - cluster title, label, freshness, affected entities, and confidence/status
   - supporting source list beneath the summary
   - explicit distinction between official update vs interpretation vs prediction

3. A **Race Weekend Timeline**
   - phases: pre-race, practice, qualifying, race, post-race
   - show how the weekend state changes across the timeline
   - users should quickly see what matters at each phase

4. A **Sources / Provenance Panel**
   - each summary links back to its sources
   - each source shows publisher, publish time, source type, and reliability tier

5. A **Simple Admin / Editorial View**
   - inspect ingested documents
   - approve or reject summaries
   - re-run clustering/summarization for a topic
   - edit labels if necessary

6. A **Seeded Demo Experience**
   - preload realistic sample data for FIA regulations, Formula1.com results, team updates, and selected media coverage
   - make the app immediately explorable without setup-heavy integrations

## Required Content Model

Design the schema around these entities:

- `sources`: FIA, Formula 1, teams, approved media outlets
- `documents`: raw regulations, result pages, press releases, race reports, articles
- `entities`: drivers, teams, circuits, weekends, regulation topics, technical themes
- `clusters`: grouped race-week topics
- `summary_outputs`: summaries labeled as `official_update`, `race_result`, `analysis`, or `prediction`
- `distribution_assets`: optional short-form outputs for digest cards or scripts

Include relational links so a cluster can connect to many documents and many tagged entities.

## Backend Requirements

Implement:

- ingestion models and services
- deduplication logic for near-identical stories
- entity tagging
- topic clustering
- summary generation service
- editorial review state
- weekend stage awareness

Create clean FastAPI endpoints for:

- `GET /api/dashboard/current`
- `GET /api/clusters`
- `GET /api/clusters/:id`
- `GET /api/sources`
- `GET /api/entities`
- `GET /api/weekends/current`
- `POST /api/ingest/run`
- `POST /api/clusters/:id/resummarize`
- `PATCH /api/summaries/:id`

Use seeded fixture data if real feeds are unavailable, but architect the ingestion layer for real RSS or scraper adapters later.

## Frontend Requirements

The UI should feel premium, editorial, and data-aware. Avoid a bland dashboard.

Design direction:

- dark, technical motorsport-inspired tone without becoming gimmicky
- strong typography and clear content hierarchy
- cards that emphasize status, recency, and provenance
- subtle motion and polished loading states
- responsive on mobile and desktop

Build these reusable UI components:

- cluster card
- source badge
- freshness indicator
- summary label pill
- race-week phase switcher
- trend card
- provenance drawer or modal

## Editorial Logic

Model summary behavior carefully:

- `official_update`: only for primary-source changes or rulings
- `race_result`: objective result or penalty outcome
- `analysis`: interpretive but source-backed commentary
- `prediction`: clearly speculative forward-looking content

Never let predictions appear visually equivalent to official updates.

Every summary should display:

- label
- last updated time
- source list
- related entities
- race-week phase

## Demo Data Expectations

Seed examples such as:

- FIA technical directive or regulation note
- Formula1.com qualifying or race result page
- team press release about an upgrade or driver quote
- media analysis articles discussing pace, setup, or strategy
- a cluster about penalties
- a cluster about qualifying performance shifts
- a cluster about technical upgrade discussion

## Engineering Expectations

Please:

- keep the code modular and production-minded
- add a README with setup and architecture notes
- add database migrations or clear schema bootstrapping
- add a few meaningful tests for clustering, labeling, and API responses
- use environment variables for secrets and provider config
- keep provider integrations swappable behind interfaces

## Nice-To-Have Features

If time permits, add:

- team and driver profile pages with trend summaries
- a "changed in the last 24 hours" filter
- short-form content asset generation from approved summaries
- multilingual-ready content model

## Output Format

Produce:

1. the full codebase
2. a short architecture summary
3. setup instructions
4. notes on where mock data or mocked integrations were used

Prefer completing an end-to-end MVP over leaving a partial scaffold.

---

## Shorter Version

If you want a tighter prompt for tools with smaller context windows, use this:

> Build an MVP webapp called **F1 Intelligence Hub** using **Next.js + TypeScript + Tailwind** for the frontend and **FastAPI + Python + Postgres** for the backend. The product should ingest official F1/FIA and trusted media sources, deduplicate and cluster overlapping stories, tag drivers/teams/weekends/regulation themes, and generate source-backed summaries labeled as `official_update`, `race_result`, `analysis`, or `prediction`. Facts and predictions must never share the same label or visual treatment. The app should include a race-week dashboard, topic cluster detail pages, a race-week timeline by phase, source provenance surfaces, and a lightweight admin/editorial review panel. Every summary must show timestamps, linked sources, related entities, and race-week stage. Use realistic seed data if live integrations are not available, but architect the ingestion and summarization layers so real adapters can be plugged in later. Add a README, tests for core flows, and a polished responsive UI that feels like a motorsport intelligence product rather than a generic news feed.
