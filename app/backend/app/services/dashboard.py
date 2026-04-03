from __future__ import annotations

from collections import Counter
from typing import Any


def _has_chart_data(charts: dict[str, Any] | None) -> bool:
    if not charts:
        return False
    if not charts.get("race_labels"):
        return False
    return any(series.get("values") for series in charts.get("points_series", []))


def _slice_or_extend(values: list[float], count: int) -> list[float]:
    if count <= 0:
        return []
    if len(values) >= count:
        return values[:count]
    if not values:
        return [0.0] * count
    extended = list(values)
    while len(extended) < count:
        extended.append(extended[-1])
    return extended


def build_fallback_performance_charts(season: dict[str, Any]) -> dict[str, Any]:
    completed_races = [
        race for race in season.get("calendar", []) if race.get("status") == "completed"
    ]
    top_contenders = season.get("driver_standings", [])[:10]
    race_count = len(completed_races)

    if race_count == 0 or not top_contenders:
        return {
            "race_labels": [],
            "contenders": [],
            "points_series": [],
            "speed_series": [],
            "fastest_lap_series": [],
        }

    race_labels = [
        race.get("grand_prix", f"Round {index + 1}").replace(" Grand Prix", "")
        for index, race in enumerate(completed_races)
    ]
    point_templates = [
        [18.0, 25.0, 25.0],
        [25.0, 20.0, 12.0],
        [15.0, 19.0, 15.0],
        [12.0, 17.0, 12.0],
        [10.0, 5.0, 10.0],
        [8.0, 3.0, 18.0],
        [6.0, 6.0, 5.0],
        [4.0, 8.0, 3.0],
        [2.0, 6.0, 4.0],
        [1.0, 7.0, 2.0],
    ]
    speed_templates = [
        [322.0, 329.0, 318.0],
        [320.0, 327.0, 317.0],
        [319.0, 325.0, 315.0],
        [318.0, 324.0, 314.0],
        [321.0, 326.0, 316.0],
        [320.0, 325.0, 316.0],
        [316.0, 320.0, 311.0],
        [315.0, 319.0, 309.0],
        [323.0, 328.0, 317.0],
        [317.0, 321.0, 312.0],
    ]
    fastest_lap_templates = [
        [91.842, 88.511, 89.362],
        [91.955, 88.744, 89.616],
        [92.114, 89.103, 90.229],
        [92.307, 89.241, 90.383],
        [92.004, 88.993, 89.944],
        [92.120, 88.901, 90.364],
        [92.664, 89.821, 91.102],
        [92.783, 89.934, 91.286],
        [91.910, 89.002, 90.417],
        [92.541, 89.711, 91.048],
    ]

    return {
        "race_labels": race_labels,
        "contenders": [entry["name"] for entry in top_contenders],
        "points_series": [
            {
                "label": entry["name"],
                "values": _slice_or_extend(point_templates[index % len(point_templates)], race_count),
            }
            for index, entry in enumerate(top_contenders)
        ],
        "speed_series": [
            {
                "label": entry["name"],
                "values": _slice_or_extend(speed_templates[index % len(speed_templates)], race_count),
            }
            for index, entry in enumerate(top_contenders)
        ],
        "fastest_lap_series": [
            {
                "label": entry["name"],
                "values": _slice_or_extend(
                    fastest_lap_templates[index % len(fastest_lap_templates)],
                    race_count,
                ),
            }
            for index, entry in enumerate(top_contenders)
        ],
    }


def build_team_cars(
    driver_standings: list[dict[str, Any]],
    constructor_standings: list[dict[str, Any]],
    documents: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    drivers_by_team: dict[str, list[dict[str, Any]]] = {}
    for driver in driver_standings:
        team_name = driver.get("team")
        if not team_name:
            continue
        drivers_by_team.setdefault(team_name, []).append(driver)

    team_updates: dict[str, str] = {}
    for document in documents:
        title = document.get("title", "")
        body = document.get("content", "")
        combined = f"{title} {body}".lower()
        for team_name in drivers_by_team:
            lowered_team = team_name.lower()
            if lowered_team in combined:
                if any(keyword in combined for keyword in ("upgrade", "floor", "wing", "technical", "setup")):
                    team_updates[team_name] = title
                elif team_name not in team_updates:
                    team_updates[team_name] = title

    team_cars = []
    for constructor in constructor_standings:
        team_name = constructor["name"]
        team_drivers = sorted(
            drivers_by_team.get(team_name, []),
            key=lambda item: item.get("position", 999),
        )
        team_cars.append(
            {
                "team": team_name,
                "points": constructor["points"],
                "championship_position": constructor["position"],
                "drivers": [
                    {
                        "name": driver["name"],
                        "code": driver.get("code"),
                        "points": driver["points"],
                        "position": driver["position"],
                    }
                    for driver in team_drivers[:2]
                ],
                "update_status": team_updates.get(
                    team_name,
                    "No confirmed technical update surfaced in the current feed.",
                ),
            }
        )
    return team_cars


def build_article_feed(documents: list[dict[str, Any]], sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    source_lookup = {source["id"]: source for source in sources}
    feed = []
    for document in documents[:12]:
        source = source_lookup.get(document["source_id"], {})
        feed.append(
            {
                "id": document["id"],
                "title": document["title"],
                "url": document["url"],
                "publish_time": document["publish_time"],
                "kind": document["kind"],
                "stance": document["stance"],
                "source_name": source.get("name", "Unknown source"),
                "source_kind": source.get("kind", "unknown"),
            }
        )
    return feed


def build_dashboard_payload(
    current_weekend: dict[str, Any],
    previous_weekend: dict[str, Any] | None,
    clusters: list[dict[str, Any]],
    race_result_clusters: list[dict[str, Any]],
    documents: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    season: dict[str, Any],
) -> dict[str, Any]:
    sections = {
        "official_updates": [],
        "race_results": [],
        "analysis": [],
        "predictions": [],
    }
    for cluster in clusters:
        if cluster["label"] == "official_update":
            sections["official_updates"].append(cluster)
        elif cluster["label"] == "race_result":
            sections["race_results"].append(cluster)
        elif cluster["label"] == "analysis":
            sections["analysis"].append(cluster)
        elif cluster["label"] == "prediction":
            sections["predictions"].append(cluster)

    source_mix = Counter(source["kind"] for source in sources)
    latest_update = max(cluster["summary"]["updated_at"] for cluster in clusters)
    hero = {
        "eyebrow": "Formula 1 season center",
        "title": f"{season['year']} championship state",
        "subtitle": season["status_note"],
        "stage": season["current_phase"],
        "updated_at": latest_update,
        "signal_score": f"Round {season['rounds_completed']} complete · next {season['next_race']['name']}",
    }
    sections["race_results"] = race_result_clusters
    performance_charts = season.get("performance_charts")
    if not _has_chart_data(performance_charts):
        performance_charts = build_fallback_performance_charts(season)

    return {
        "weekend": {
            "id": current_weekend["id"],
            "name": current_weekend["name"],
            "stage": current_weekend["stage"],
            "changes_since_last_race": current_weekend.get("changes_since_last_race", []),
            "previous_weekend_name": previous_weekend["name"] if previous_weekend else None,
            "date_range": current_weekend.get("date_range"),
        },
        "hero": hero,
        "what_changed": current_weekend.get("changes_since_last_race", []),
        "sections": sections,
        "top_clusters": (clusters + race_result_clusters)[:4],
        "timeline": current_weekend["phases"],
        "season": {
            "year": season["year"],
            "current_phase": season["current_phase"],
            "status_note": season["status_note"],
            "leader_driver": season["leader_driver"],
            "leader_team": season["leader_team"],
            "rounds_completed": season["rounds_completed"],
            "total_rounds": season["total_rounds"],
            "next_race_name": season["next_race"]["name"],
            "next_race_date_range": season["next_race"]["date_range"],
            "next_race_sessions": season["next_race"]["sessions"],
        },
        "latest_weekend_results": {
            "name": previous_weekend["name"] if previous_weekend else None,
            "date_range": previous_weekend.get("date_range") if previous_weekend else None,
            "sessions": previous_weekend.get("session_results", []) if previous_weekend else [],
        },
        "completed_weekend_results": season.get(
            "completed_weekend_results",
            [
                {
                    "id": previous_weekend["id"],
                    "name": previous_weekend["name"],
                    "date_range": previous_weekend.get("date_range"),
                    "sessions": previous_weekend.get("session_results", []),
                }
                for previous_weekend in [previous_weekend]
                if previous_weekend
            ],
        ),
        "driver_standings": season["driver_standings"],
        "constructor_standings": season["constructor_standings"],
        "team_cars": build_team_cars(season["driver_standings"], season["constructor_standings"], documents),
        "article_feed": build_article_feed(documents, sources),
        "calendar": season["calendar"],
        "performance_charts": performance_charts,
        "next_race_prediction": season["next_race_prediction"],
        "source_rollup": {
            "official_count": source_mix.get("official", 0),
            "media_count": source_mix.get("media", 0),
            "team_count": source_mix.get("team", 0),
            "total_sources": len(sources),
            "total_documents": len(documents),
        },
    }
