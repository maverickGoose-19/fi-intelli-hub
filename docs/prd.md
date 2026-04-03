# Product Requirements Document

## Product Name

F1 Intelligence Hub

## Summary

F1 Intelligence Hub is a Formula 1 season intelligence dashboard for fans who want a fast, trustworthy read on what happened, what changed, and what matters next without mixing confirmed results with speculation.

## Problem

Formula 1 information is fragmented across official sites, timing feeds, team announcements, FIA documents, and media coverage. Fans and analysts have to manually piece together:

- current race weekend status
- latest results and standings
- confirmed technical or regulatory updates
- interpretation versus verified fact
- upcoming race context

The result is a noisy and slow information loop.

## Goals

- present the current season state in one dashboard
- distinguish facts, results, analysis, and predictions clearly
- support fast manual refresh during race weekends
- make completed race weekends explorable after they finish
- surface article-backed updates in the editorial queue

## Non-Goals

- live lap-by-lap telemetry visualization
- betting features
- user accounts or social features
- full CMS workflow with version history
- official Formula 1 branding asset usage

## Target Users

- Formula 1 fans who want a reliable race-week dashboard
- editors or operators curating an F1 intelligence feed
- technically curious users comparing performance across races

## Core User Stories

1. As a fan, I want to see the current standings, calendar, and latest completed race results in one place.
2. As a race-week user, I want a quick refresh button for timing and standings without waiting for article ingestion.
3. As an editor, I want synced articles to appear in the editorial workbench so I can review and relabel them.
4. As a user, I want to switch between completed race weekends and compare session results.
5. As a user, I want charts that compare the leading drivers across completed races.

## Functional Requirements

### Dashboard

- show season state, current phase, and progress
- show driver and constructor standings
- show completed race-weekend results with weekend selector
- show next-race prediction and schedule
- show season calendar
- show article feed and team car watch
- show performance charts for top contenders

### Sync

- provide `Quick sync` for OpenF1-only refresh
- provide `Full sync` for OpenF1 plus article ingestion
- keep serving last good data when sync fails
- attempt one scheduled Friday sync in local timezone

### Editorial

- cluster synced article documents into editorial items
- generate summaries for new clusters
- preserve editorial status where cluster identity is stable
- support relabeling and resummarization

## Experience Principles

- speed over clutter
- clear trust labeling
- race-week relevance first
- visually distinct team and surface identity

## Success Metrics

- dashboard loads successfully using either live or fallback data
- quick sync completes faster than full sync
- editorial queue reflects new article ingestion after full sync
- build and backend tests pass on each release candidate

## Risks

- OpenF1 endpoint availability and schema changes
- article site markup changes that break scraping
- runtime JSON cache limits for concurrent or multi-instance deployment
- no authentication on admin/editorial surfaces yet
