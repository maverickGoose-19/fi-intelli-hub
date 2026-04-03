+++
title = "F1 Intelligence Hub v2"
slug = "f1-intelligence-hub-v2"
domain = "Media Intelligence, Sports Data, and Predictive Product Systems"
short_description = "A production-oriented Formula 1 intelligence platform that combines race-week ingestion, editorial source separation, historical modeling, and a dedicated prediction experience across dashboard and analytics surfaces."
tagline = "A motorsport intelligence system that treats Formula 1 as a structured data-and-decision problem, not just a content feed."
impact_summary = "Turns race-week noise into a source-aware operating layer with live standings, weekend state, editorially separated summaries, and a hybrid ML prediction engine backed by historical race data and explainable feature scoring."
stack = ["Next.js", "React", "TypeScript", "Tailwind CSS", "FastAPI", "Python", "Postgres", "OpenF1", "FastF1", "Ergast-compatible APIs", "scikit-learn", "Background jobs", "Editorial workflows"]
featured = false
sort_order = 5
hero_stat = "From feed to system"
hero_label = "Race-week intelligence"
category = "Sports / Data / Product"
context = "Formula 1 creates a uniquely fragmented information environment. Official schedules, FIA rulings, session results, constructor form, technical narratives, and media speculation all move at different speeds. The product opportunity is not just better summarization. It is to build a system that can model race-week state, preserve provenance, and expose separate surfaces for facts, analysis, and forward-looking predictions."
problem = "Most F1 products either show raw scores or publish commentary, but very few connect official race state, source quality, editorial review, and predictive intelligence in one coherent experience. Users end up switching between timing pages, standings tables, media stories, and social posts to understand what changed and what is likely to happen next."
why_it_matters = "The value is trust plus synthesis. Fans want a faster read on the championship, but they also need to know whether a claim is official, interpretive, or speculative. Once prediction is added, that boundary matters even more. A credible sports intelligence product needs provenance, freshness, explainability, and a path to operational production quality."
what_i_built = [
  "A season dashboard that unifies standings, race calendar, completed weekend results, team watch, article feed, performance charts, and next-race context",
  "An editorial intelligence layer that separates `official_update`, `race_result`, `analysis`, and `prediction` content instead of flattening all surfaces together",
  "A dedicated prediction analytics page with contender rankings, win and podium probabilities, feature importance, scenario analysis, constructor outlook, and methodology notes",
  "A hybrid prediction service that combines live in-app season context with historical race and qualifying data and explainable feature engineering",
  "A sync architecture with quick race-data refresh, full sync with article ingestion and editorial refresh, and resilient fallback behavior when external data sources fail"
]
architecture = [
  "Next.js frontend for dashboard, editorial, and dedicated predictions surfaces",
  "FastAPI backend as the orchestration layer for season payload assembly, sync execution, editorial clustering, and prediction serving",
  "Source ingestion from OpenF1 plus approved article sources with explicit source labels and publish times",
  "Historical model-training path using Ergast-compatible APIs for race and qualifying data, with FastF1 available for richer schedule and telemetry-aware context",
  "A repository/service architecture that cleanly separates sync logic, dashboard shaping, clustering, summarization, and predictions so each can evolve independently"
]
engineering_decisions = [
  "Keep fact, result, analysis, and prediction labels structurally separate across the API and UI rather than leaving that distinction to copy alone",
  "Use seeded and cached fallbacks so the app still renders if external sources are unavailable or partially degraded",
  "Make prediction output explainable through feature-level scoring, contender evidence, and scenario matrices instead of returning opaque probabilities",
  "Support a lightweight in-app fallback model while also enabling a stronger historical classifier when ML dependencies and external datasets are available",
  "Design the backend around services and repository orchestration so the current JSON-backed MVP can migrate to Postgres without rewriting product logic"
]
tradeoffs = [
  "A transparent hybrid model is more trustworthy than a black-box predictor, though it adds more surface area to maintain",
  "Using current-season data plus historical priors improves usefulness, but the model still needs careful labeling because sports outcomes remain volatile",
  "File-backed runtime state made the MVP fast to build, though it is not the right long-term answer for concurrency, history, or multi-instance deployment",
  "Request-triggered syncs keep the stack simple during development, though production should move ingestion and model refreshes into scheduled jobs"
]
outcomes = [
  "Users can move from current standings to completed weekend context to next-race prediction without leaving the product",
  "The system now exposes a real prediction API and a dedicated analytics page rather than a single hard-coded podium card",
  "The project has a credible production migration path: Postgres for state, background workers for ingestion, and model-serving patterns that can expand beyond the MVP",
  "The same underlying source model can power fan-facing explainers, editorial review, and analytics-grade prediction surfaces while preserving provenance"
]
role_ownership = [
  "Owned the product framing of F1 race week as a structured intelligence and prediction system rather than a generic sports dashboard",
  "Designed the backend service boundaries across ingestion, editorial clustering, dashboard shaping, and prediction modeling",
  "Implemented the dedicated predictions experience end to end, including API design, model logic, explainability surfaces, and frontend analytics UI",
  "Defined the target production architecture around Postgres, workers, source reliability, and stronger operational maturity"
]
lessons_learned = [
  "Prediction only becomes credible in a media product when provenance and labeling are first-class product concepts",
  "In fast-moving sports domains, clustering, freshness, and state modeling are as important as the predictive model itself",
  "A useful MVP can start with file-backed state and deterministic workflows, but it should be shaped early around the production architecture it wants to become",
  "A dedicated analytics page creates much more product value than a single embedded prediction widget because it makes methodology and confidence inspectable"
]
future_improvements = [
  "Migrate runtime state, editorial objects, historical snapshots, and model features into Postgres",
  "Add scheduled workers for OpenF1 sync, article ingestion, feature materialization, and model retraining",
  "Expand the model with richer telemetry and tyre-degradation features using FastF1 session data",
  "Introduce authenticated editorial roles, approvals, and audit trails",
  "Add team, driver, and circuit profile pages with longitudinal trend analysis and simulation views"
]
+++
## Project overview

F1 Intelligence Hub v2 is the version where the project stops looking like a summarization prototype and starts behaving like a real sports intelligence product.

The core shift is that the system now has three distinct layers:

```text
Live race data + source ingestion
-> editorial and intelligence modeling
-> dashboard and prediction products
```

That distinction matters. The app is no longer just assembling a season page from a few feeds. It now models race-week context, preserves source boundaries, and serves a dedicated prediction experience that explains why the model likes one driver over another.

## What changed in v2

Compared with the original concept, v2 adds:

- a dedicated `/predictions` product surface instead of a single embedded next-race card
- a live `GET /api/predictions/next-race` endpoint served by the backend
- a hybrid modeling layer combining in-app season features with historical qualifying and results data
- explicit contender evidence, feature scoring, track-fit logic, scenario matrices, and constructor outlook tables
- an architectural path toward production state management and model operations

At the product level, that moves F1 Intelligence Hub from “help me understand the weekend” to “help me understand the weekend and the forecast.”

## Current application shape

Today the system is split into a Next.js frontend and a FastAPI backend.

The frontend now has three core experiences:

- the main season dashboard
- the editorial/admin workbench
- the dedicated prediction analytics page

The backend is responsible for:

- assembling dashboard payloads
- syncing OpenF1 session and standings data
- ingesting articles and rebuilding editorial clusters
- serving the prediction model output
- preserving fallback behavior when external calls fail

This gives the project a clean service boundary: the frontend renders product surfaces, and the backend owns state derivation, orchestration, and model output.

## Prediction system

The prediction service is the most important v2 addition.

Instead of returning a static podium guess, the backend now constructs a hybrid winner model that blends:

- championship form
- constructor strength and car package quality
- season wins and podium conversion
- qualifying sharpness
- recent race form
- career wins and senior-level experience
- junior-league success
- track-fit assumptions
- tyre-management fit
- expected strategy alignment
- reliability and weather adaptability

The implementation supports two modes:

```text
Fallback mode:
in-app season data -> engineered feature scoring -> lightweight calibrated model

ML mode:
in-app season data + historical race/qualifying data -> hybrid scoring -> contender probabilities
```

When the ML stack is available, the system trains from Ergast-compatible historical race and qualifying data and uses FastF1 for event-context enrichment. That gives the app a stronger training base without losing the explainability of the feature-engineered layer.

## Why the predictions page matters

The dedicated predictions page is not just a visual add-on. It changes the product meaningfully because it makes the model inspectable.

The page shows:

- ranked contenders
- win and podium probabilities
- feature breakdown for the favorite
- feature-importance summaries
- constructor outlook
- scenario-matrix explanations
- methodology and source notes

This is important because prediction in sports products is usually either too shallow or too opaque. Here, the user can see both the forecast and the reasoning structure behind it.

## Editorial and trust model

The editorial model remains a core part of the product and becomes even more important in v2.

The system still enforces four distinct summary classes:

- `official_update`
- `race_result`
- `analysis`
- `prediction`

That separation gives the product a trust hierarchy:

- official and result surfaces anchor the known state
- analysis surfaces add interpretation
- prediction surfaces are explicitly speculative

This is the right structure for a sports intelligence app because it prevents the product from blending authoritative information and model output into one ambiguous narrative.

## Data model

The system is already shaped around explicit domain objects:

- `sources`
- `documents`
- `entities`
- `clusters`
- `summary_outputs`
- `distribution_assets`
- season state, standings, weekends, and sync metadata

That model is what makes the project extensible. Because the objects are explicit, the same system can support:

- fan-facing dashboard experiences
- editorial review workflows
- prediction features
- future profile pages for drivers, teams, and circuits

This is one of the biggest reasons the project now has production value. The app is built on reusable domain structure, not page-specific glue code.

## Production end state

The current codebase is still an MVP in some operational areas, but the target end state is now much clearer.

The production version of F1 Intelligence Hub should look like this:

```text
Next.js frontend
-> CDN / managed frontend hosting

FastAPI backend
-> reverse proxy + structured logging + metrics

Postgres
-> source records, editorial state, weekend snapshots, model features, prediction history

Workers / schedulers
-> OpenF1 sync, article ingestion, feature materialization, model refresh

Model layer
-> versioned feature sets, trained classifiers, cached inference outputs, evaluation tracking
```

In that end state:

- Postgres replaces the JSON runtime cache as the system of record
- historical snapshots support backtesting and model evaluation
- syncs run in background jobs instead of request-triggered code paths
- prediction outputs can be persisted and compared over time
- editorial actions can be audited and role-gated
- source health and fetch failures can be monitored operationally

That is the right long-term shape because sports intelligence is really a stateful systems problem. Once the project handles live race data, editorial workflows, and model output together, a durable database and job architecture stop being “nice to have” and become part of the product itself.

## Postgres as the backbone

Postgres is the most important production upgrade because it unlocks several capabilities at once:

- durable runtime state
- multi-user editorial workflows
- historical weekend snapshots
- feature-store style tables for model inputs
- prediction history for evaluation and calibration
- reliable deployment across multiple backend instances

A clean production schema would likely separate:

- raw source and document ingestion tables
- normalized entities and clusters
- editorial summaries and approval history
- weekend/session/race-state snapshots
- model-feature materializations
- prediction outputs and evaluation results

That would turn the current MVP into a real operational intelligence platform.

## Model operations end state

The prediction system should eventually mature beyond on-request training or fallback scoring.

The production model workflow should look like:

```text
Historical race + qualifying data
+ current season state
+ telemetry-derived features
-> feature pipeline
-> offline training
-> evaluation and calibration
-> versioned model artifact
-> API inference service
-> saved prediction outputs
```

That would support:

- reproducible retraining
- calibration tracking
- versioned model rollouts
- backtesting on prior weekends
- clearer comparisons between heuristic and learned models

In other words, v2 introduces the prediction surface, and the production end state turns it into a proper model-serving system.

## Why this project has stronger production value now

What makes the project more valuable in v2 is not just the new page. It is that the system now ties together:

- live race-week state
- editorial trust boundaries
- reusable data structures
- explainable prediction outputs
- a realistic production architecture path

That makes it interesting both as a fan product and as a systems design project. It demonstrates product judgment, information architecture, backend orchestration, and the beginnings of an actual model-driven feature set.

## Final state

The best way to describe the final product is:

F1 Intelligence Hub v2 is a source-aware Formula 1 intelligence platform that combines race-week aggregation, editorial separation, and predictive analytics into a single explainable product system.

It starts as a dashboard, but the real end state is broader:

- a trustworthy fan intelligence layer
- a reusable editorial operating surface
- a prediction product with transparent methodology
- a production-ready data platform backed by Postgres and scheduled jobs

That is the version of the project that feels durable, defensible, and expandable.
