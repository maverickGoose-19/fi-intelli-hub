from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import json
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from app.config import settings


JsonFetcher = Callable[[str, dict[str, Any]], list[dict[str, Any]]]


def _normalized_openf1_base_url() -> str:
    base_url = settings.openf1_base_url.rstrip("/")
    return base_url if base_url.endswith("/v1") else f"{base_url}/v1"


def _default_fetch_json(endpoint: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    query = urlencode({key: value for key, value in params.items() if value is not None}, doseq=True)
    url = f"{_normalized_openf1_base_url()}/{endpoint}"
    if query:
        url = f"{url}?{query}"
    request = Request(url, headers={"User-Agent": "F1-Intelligence-Hub/0.1"})
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=ZoneInfo("UTC"))
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=ZoneInfo("UTC"))
    return parsed


def _meeting_name(session: dict[str, Any]) -> str:
    if session.get("meeting_name"):
        return str(session["meeting_name"])
    location = session.get("location") or session.get("country_name") or "Unknown"
    return f"{location} Grand Prix"


def _normalize_phase(session_name: str) -> str:
    lowered = session_name.lower()
    if "sprint qualifying" in lowered:
        return "sprint_qualifying"
    if lowered.strip() == "sprint":
        return "sprint"
    if "qualifying" in lowered:
        return "qualifying"
    if "practice" in lowered or lowered.startswith("fp"):
        return "practice"
    if "race" in lowered:
        return "race"
    return lowered.replace(" ", "_")


def _display_phase(phase: str) -> str:
    return phase.replace("_", " ")


def _session_category(session_name: str) -> str:
    phase = _normalize_phase(session_name)
    if phase == "qualifying" or phase == "sprint_qualifying":
        return "qualifying"
    if phase == "race" or phase == "sprint":
        return "race"
    return "practice"


def _format_date_range(start: datetime, end: datetime) -> str:
    start_text = start.strftime("%d %b %Y")
    if start.date() == end.date():
        return start_text
    if start.year == end.year:
        if start.month == end.month:
            return f"{start.strftime('%d')} - {end.strftime('%d %b %Y')}"
        return f"{start.strftime('%d %b')} - {end.strftime('%d %b %Y')}"
    return f"{start.strftime('%d %b %Y')} - {end.strftime('%d %b %Y')}"


def _format_local_session_window(start: datetime, end: datetime) -> str:
    timezone_label = start.strftime("%Z")
    if start.date() == end.date():
        return f"{start.strftime('%d %b · %H:%M')} - {end.strftime('%H:%M')} {timezone_label}"
    return f"{start.strftime('%d %b · %H:%M')} - {end.strftime('%d %b · %H:%M')} {timezone_label}"


def _best_driver_name(item: dict[str, Any]) -> str:
    return (
        item.get("full_name")
        or item.get("driver_name")
        or item.get("broadcast_name")
        or item.get("name")
        or f"Driver {item.get('driver_number', '?')}"
    )


def _resolve_team_name(item: dict[str, Any]) -> str:
    return item.get("team_name") or item.get("team") or "Unknown Team"


def _result_metric(entry: dict[str, Any], position: int) -> str:
    for key in ("duration", "lap_time", "time", "gap_to_leader", "interval_to_position_ahead"):
        value = entry.get(key)
        if value not in (None, ""):
            return str(value)
    if position == 1:
        return "Leader"
    return "-"


class OpenF1SyncService:
    def __init__(self, fetch_json: JsonFetcher | None = None) -> None:
        self.fetch_json = fetch_json or _default_fetch_json

    def sync(self, base_data: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
        local_zone = ZoneInfo(settings.local_timezone)
        current_time = now or datetime.now(local_zone)
        current_time = current_time.astimezone(local_zone)
        year = current_time.year

        sessions = self._fetch_sessions_for_year(year)
        if not sessions:
            raise ValueError("OpenF1 returned no session data")

        meetings = self._group_meetings(sessions)
        latest_completed = self._latest_completed_meeting(meetings, current_time)
        next_meeting = self._next_meeting(meetings, current_time)
        active_meeting = self._active_meeting(meetings, current_time)
        current_meeting = active_meeting or next_meeting or latest_completed
        if current_meeting is None or latest_completed is None:
            raise ValueError("Unable to derive current and latest completed meetings from OpenF1")

        latest_race_session = self._latest_race_session(latest_completed)
        reference_session = latest_race_session or latest_completed["sessions"][-1]
        driver_lookup = self._build_driver_lookup(reference_session["session_key"])
        latest_results = self._build_latest_results(latest_completed, driver_lookup)
        driver_standings = self._fetch_driver_standings(reference_session["session_key"])
        if not driver_standings:
            driver_standings = deepcopy(base_data.get("season", {}).get("driver_standings", []))
        constructor_standings = self._fetch_constructor_standings(reference_session["session_key"])
        if not constructor_standings:
            constructor_standings = deepcopy(base_data.get("season", {}).get("constructor_standings", []))
        calendar = self._build_calendar(meetings, current_time)
        current_phase = self._compute_current_phase(current_meeting, active_meeting, current_time)
        performance_charts = self._build_performance_charts(meetings, driver_standings)
        completed_weekend_results = self._build_completed_weekend_results(meetings)

        updated = deepcopy(base_data)
        updated["season"] = self._build_season_payload(
            current_phase=current_phase,
            current_time=current_time,
            latest_completed=latest_completed,
            next_meeting=next_meeting or current_meeting,
            driver_standings=driver_standings,
            constructor_standings=constructor_standings,
            calendar=calendar,
            performance_charts=performance_charts,
            completed_weekend_results=completed_weekend_results,
        )
        updated["weekends"] = [
            self._build_latest_completed_weekend(latest_completed, latest_results),
            self._build_current_weekend(
                current_meeting=current_meeting,
                latest_completed=latest_completed,
                current_phase=current_phase,
                driver_standings=driver_standings,
                constructor_standings=constructor_standings,
            ),
        ]
        current_weekend_id = f"weekend_{current_meeting['meeting_key']}"
        previous_weekend_id = f"weekend_{latest_completed['meeting_key']}"
        derived = self._build_dynamic_content(
            updated["season"],
            latest_completed,
            current_weekend_id=current_weekend_id,
            previous_weekend_id=previous_weekend_id,
        )
        updated["documents"] = derived["documents"]
        updated["clusters"] = derived["clusters"]
        updated["summary_outputs"] = derived["summary_outputs"]
        updated["distribution_assets"] = derived["distribution_assets"]
        return updated

    def _fetch_sessions_for_year(self, target_year: int) -> list[dict[str, Any]]:
        try:
            return self.fetch_json("sessions", {"year": target_year})
        except HTTPError as error:
            if error.code != 404:
                raise
        return []

    def _safe_fetch_json(self, endpoint: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            return self.fetch_json(endpoint, params)
        except HTTPError as error:
            if error.code == 404:
                return []
            raise

    def _group_meetings(self, sessions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[int, dict[str, Any]] = {}
        for session in sessions:
            meeting_key = int(session["meeting_key"])
            bucket = grouped.setdefault(
                meeting_key,
                {
                    "meeting_key": meeting_key,
                    "name": _meeting_name(session),
                    "location": session.get("location") or session.get("country_name") or "Unknown",
                    "circuit": session.get("circuit_short_name") or session.get("location") or "Unknown",
                    "date_start": _parse_datetime(session.get("date_start")),
                    "date_end": _parse_datetime(session.get("date_end")),
                    "sessions": [],
                },
            )
            session_start = _parse_datetime(session.get("date_start"))
            session_end = _parse_datetime(session.get("date_end"))
            bucket["date_start"] = min(bucket["date_start"], session_start)
            bucket["date_end"] = max(bucket["date_end"], session_end)
            bucket["sessions"].append(
                {
                    "session_key": int(session["session_key"]),
                    "session_name": str(session.get("session_name") or session.get("session_type") or "Session"),
                    "date_start": session_start,
                    "date_end": session_end,
                }
            )
        ordered = sorted(grouped.values(), key=lambda item: item["date_start"])
        for meeting in ordered:
            meeting["sessions"].sort(key=lambda item: item["date_start"])
            meeting["date_range"] = _format_date_range(meeting["date_start"], meeting["date_end"])
        return ordered

    def _latest_completed_meeting(
        self, meetings: list[dict[str, Any]], now: datetime
    ) -> dict[str, Any] | None:
        completed = [meeting for meeting in meetings if meeting["date_end"] < now]
        return completed[-1] if completed else None

    def _next_meeting(self, meetings: list[dict[str, Any]], now: datetime) -> dict[str, Any] | None:
        upcoming = [meeting for meeting in meetings if meeting["date_start"] > now]
        return upcoming[0] if upcoming else None

    def _active_meeting(self, meetings: list[dict[str, Any]], now: datetime) -> dict[str, Any] | None:
        for meeting in meetings:
            if meeting["date_start"] <= now <= meeting["date_end"]:
                return meeting
        return None

    def _latest_race_session(self, meeting: dict[str, Any]) -> dict[str, Any] | None:
        race_sessions = [
            session
            for session in meeting["sessions"]
            if _normalize_phase(session["session_name"]) == "race"
        ]
        return race_sessions[-1] if race_sessions else None

    def _build_driver_lookup(self, session_key: int) -> dict[int, dict[str, Any]]:
        drivers = self._safe_fetch_json("drivers", {"session_key": session_key})
        return {int(driver["driver_number"]): driver for driver in drivers if driver.get("driver_number") is not None}

    def _build_latest_results(
        self, meeting: dict[str, Any], driver_lookup: dict[int, dict[str, Any]]
    ) -> list[dict[str, Any]]:
        session_results: list[dict[str, Any]] = []
        supported = {"practice", "qualifying", "race", "sprint", "sprint_qualifying"}
        for session in meeting["sessions"]:
            normalized = _normalize_phase(session["session_name"])
            if normalized not in supported:
                continue
            raw_entries = self._safe_fetch_json("session_result", {"session_key": session["session_key"]})
            sorted_entries = sorted(
                raw_entries,
                key=lambda item: int(item.get("position") or 999),
            )[:5]
            entries = []
            for raw_entry in sorted_entries:
                driver_number = raw_entry.get("driver_number")
                driver_record = driver_lookup.get(int(driver_number)) if driver_number is not None else {}
                position = int(raw_entry.get("position") or len(entries) + 1)
                entries.append(
                    {
                        "position": position,
                        "driver": _best_driver_name({**driver_record, **raw_entry}),
                        "team": _resolve_team_name({**driver_record, **raw_entry}),
                        "metric": _result_metric(raw_entry, position),
                        "points": raw_entry.get("points"),
                    }
                )
            session_results.append(
                {
                    "name": session["session_name"],
                    "category": _session_category(session["session_name"]),
                    "status": "completed",
                    "source_url": "https://openf1.org/docs/#api-endpoints",
                    "entries": entries,
                }
            )
        return session_results

    def _fetch_driver_standings(self, session_key: int) -> list[dict[str, Any]]:
        standings = self._safe_fetch_json("championship_drivers", {"session_key": session_key})
        mapped = []
        for item in standings:
            mapped.append(
                {
                    "position": int(item.get("position_current") or item.get("position") or len(mapped) + 1),
                    "name": _best_driver_name(item),
                    "code": item.get("name_acronym") or item.get("acronym"),
                    "team": _resolve_team_name(item),
                    "nationality": item.get("country_code"),
                    "points": float(item.get("points_current") or item.get("points") or 0),
                }
            )
        return mapped

    def _fetch_constructor_standings(self, session_key: int) -> list[dict[str, Any]]:
        standings = self._safe_fetch_json("championship_teams", {"session_key": session_key})
        mapped = []
        for item in standings:
            mapped.append(
                {
                    "position": int(item.get("position_current") or item.get("position") or len(mapped) + 1),
                    "name": item.get("team_name") or item.get("name") or "Unknown Team",
                    "points": float(item.get("points_current") or item.get("points") or 0),
                }
            )
        return mapped

    def _build_calendar(self, meetings: list[dict[str, Any]], now: datetime) -> list[dict[str, Any]]:
        calendar: list[dict[str, Any]] = []
        next_key = self._next_meeting(meetings, now)
        next_meeting_key = next_key["meeting_key"] if next_key else None
        for index, meeting in enumerate(meetings, start=1):
            if meeting["date_end"] < now:
                status = "completed"
            elif meeting["meeting_key"] == next_meeting_key:
                status = "next"
            else:
                status = "upcoming"
            calendar.append(
                {
                    "round": index,
                    "grand_prix": meeting["name"],
                    "date_range": meeting["date_range"],
                    "venue": meeting["circuit"],
                    "status": status,
                }
            )
        return calendar

    def _compute_current_phase(
        self,
        current_meeting: dict[str, Any],
        active_meeting: dict[str, Any] | None,
        now: datetime,
    ) -> str:
        if active_meeting is None:
            return "between_races"
        for session in active_meeting["sessions"]:
            if session["date_start"] <= now <= session["date_end"]:
                return _normalize_phase(session["session_name"])
        upcoming = [session for session in active_meeting["sessions"] if session["date_start"] > now]
        if upcoming:
            return _normalize_phase(upcoming[0]["session_name"])
        return "post_race"

    def _build_current_weekend(
        self,
        current_meeting: dict[str, Any],
        latest_completed: dict[str, Any],
        current_phase: str,
        driver_standings: list[dict[str, Any]],
        constructor_standings: list[dict[str, Any]],
    ) -> dict[str, Any]:
        next_sessions = []
        for session in current_meeting["sessions"]:
            local_start = session["date_start"].astimezone(ZoneInfo(settings.local_timezone))
            local_end = session["date_end"].astimezone(ZoneInfo(settings.local_timezone))
            next_sessions.append(
                {
                    "name": session["session_name"],
                    "time_local": _format_local_session_window(local_start, local_end),
                }
            )

        return {
            "id": f"weekend_{current_meeting['meeting_key']}",
            "name": current_meeting["name"],
            "slug": current_meeting["name"].lower().replace(" ", "-"),
            "season": current_meeting["date_start"].year,
            "date_range": current_meeting["date_range"],
            "circuit_entity_id": f"circuit_{current_meeting['meeting_key']}",
            "current": True,
            "stage": current_phase,
            "started_at": current_meeting["date_start"].isoformat(),
            "ended_at": current_meeting["date_end"].isoformat(),
            "changes_since_last_race": [
                f"{driver_standings[0]['name']} leads the Drivers' Championship on {driver_standings[0]['points']} points."
                if driver_standings
                else "Drivers' standings will update after the latest official session.",
                f"{constructor_standings[0]['name']} leads the Constructors' Championship on {constructor_standings[0]['points']} points."
                if constructor_standings
                else "Constructors' standings will update after the latest official session.",
                f"The last completed race was {latest_completed['name']}. The next stop is {current_meeting['name']}.",
            ],
            "phases": self._build_timeline(current_phase, current_meeting),
            "session_results": [],
            "next_sessions": next_sessions,
        }

    def _build_latest_completed_weekend(
        self, latest_completed: dict[str, Any], latest_results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        return {
            "id": f"weekend_{latest_completed['meeting_key']}",
            "name": latest_completed["name"],
            "slug": latest_completed["name"].lower().replace(" ", "-"),
            "season": latest_completed["date_start"].year,
            "date_range": latest_completed["date_range"],
            "circuit_entity_id": f"circuit_{latest_completed['meeting_key']}",
            "current": False,
            "stage": "post_race",
            "started_at": latest_completed["date_start"].isoformat(),
            "ended_at": latest_completed["date_end"].isoformat(),
            "phases": self._build_completed_timeline(latest_completed),
            "session_results": latest_results,
        }

    def _build_timeline(self, current_phase: str, meeting: dict[str, Any]) -> list[dict[str, Any]]:
        phases = [
            "between_races",
            "pre_race",
            "practice",
            "sprint_qualifying",
            "sprint",
            "qualifying",
            "race",
            "post_race",
        ]
        current_index = phases.index(current_phase) if current_phase in phases else 0
        timeline = []
        for index, phase in enumerate(phases):
            state = "complete" if index < current_index else "active" if index == current_index else "upcoming"
            headline = (
                f"{meeting['name']} is currently in the {_display_phase(phase)} phase."
                if state == "active"
                else f"{meeting['name']} {('completed' if state == 'complete' else 'will move into')} {_display_phase(phase)}."
            )
            timeline.append(
                {
                    "phase": phase,
                    "state": state,
                    "headline": headline,
                    "focus": self._phase_focus(phase),
                }
            )
        return timeline

    def _build_completed_timeline(self, meeting: dict[str, Any]) -> list[dict[str, Any]]:
        phases = ["pre_race", "practice", "qualifying", "race", "post_race"]
        return [
            {
                "phase": phase,
                "state": "complete",
                "headline": f"{meeting['name']} completed the {_display_phase(phase)} phase.",
                "focus": self._phase_focus(phase),
            }
            for phase in phases
        ]

    def _phase_focus(self, phase: str) -> str:
        mapping = {
            "between_races": "standings, schedule, next-race framing",
            "pre_race": "setup direction, forecast, weekend format",
            "practice": "pace, balance, reliability",
            "sprint_qualifying": "track position, compressed qualifying execution",
            "sprint": "short-form race pace, points, risk appetite",
            "qualifying": "one-lap pace, grid order, tire prep",
            "race": "strategy, degradation, conversion of pace",
            "post_race": "results, standings, momentum shift",
        }
        return mapping.get(phase, "context")

    def _build_season_payload(
        self,
        current_phase: str,
        current_time: datetime,
        latest_completed: dict[str, Any],
        next_meeting: dict[str, Any],
        driver_standings: list[dict[str, Any]],
        constructor_standings: list[dict[str, Any]],
        calendar: list[dict[str, Any]],
        performance_charts: dict[str, Any],
        completed_weekend_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        next_sessions = []
        for session in next_meeting["sessions"]:
            local_start = session["date_start"].astimezone(ZoneInfo(settings.local_timezone))
            local_end = session["date_end"].astimezone(ZoneInfo(settings.local_timezone))
            next_sessions.append(
                {
                    "name": session["session_name"],
                    "time_local": _format_local_session_window(local_start, local_end),
                }
            )

        top_three = []
        for position, entry in enumerate(driver_standings[:3], start=1):
            top_three.append(
                {
                    "position": position,
                    "driver": entry["name"],
                    "team": entry.get("team") or "Unknown Team",
                }
            )

        return {
            "year": current_time.year,
            "current_phase": current_phase,
            "status_note": (
                f"{latest_completed['name']} finished on {latest_completed['date_end'].strftime('%B %d, %Y')}. "
                f"The next race is {next_meeting['name']} on {next_meeting['date_range']}."
            ),
            "rounds_completed": sum(1 for race in calendar if race["status"] == "completed"),
            "total_rounds": len(calendar),
            "leader_driver": driver_standings[0]["name"] if driver_standings else "Unknown",
            "leader_team": constructor_standings[0]["name"] if constructor_standings else "Unknown",
            "next_race": {
                "name": next_meeting["name"],
                "date_range": next_meeting["date_range"],
                "weekend_format": "Sprint"
                if any(_normalize_phase(session["session_name"]) == "sprint" for session in next_meeting["sessions"])
                else "Standard",
                "venue": next_meeting["circuit"],
                "sessions": next_sessions,
            },
            "driver_standings": driver_standings,
            "constructor_standings": constructor_standings,
            "calendar": calendar,
            "performance_charts": performance_charts,
            "completed_weekend_results": completed_weekend_results,
            "next_race_prediction": {
                "race_name": next_meeting["name"],
                "date_range": next_meeting["date_range"],
                "weekend_format": "Sprint"
                if any(_normalize_phase(session["session_name"]) == "sprint" for session in next_meeting["sessions"])
                else "Standard",
                "reason": (
                    "Inference from OpenF1 standings and session data: the prediction follows the current championship order "
                    "and should be treated as a forecast rather than an official result."
                ),
                "top_three": top_three,
            },
        }

    def _build_performance_charts(
        self, meetings: list[dict[str, Any]], driver_standings: list[dict[str, Any]]
    ) -> dict[str, Any]:
        top_contenders = driver_standings[:10]
        contender_names = [entry["name"] for entry in top_contenders]
        contender_points = {entry["name"]: [] for entry in top_contenders}
        contender_speeds = {entry["name"]: [] for entry in top_contenders}
        contender_fastest_laps = {entry["name"]: [] for entry in top_contenders}
        race_labels: list[str] = []

        completed_meetings = [meeting for meeting in meetings if self._latest_race_session(meeting)]
        for meeting in completed_meetings:
            race_session = self._latest_race_session(meeting)
            if race_session is None:
                continue
            race_labels.append(meeting["name"])
            drivers = self._build_driver_lookup(race_session["session_key"])
            results = self._safe_fetch_json("session_result", {"session_key": race_session["session_key"]})
            laps = self._safe_fetch_json("laps", {"session_key": race_session["session_key"]})

            results_by_name: dict[str, dict[str, Any]] = {}
            for result in results:
                driver_number = result.get("driver_number")
                if driver_number is None:
                    continue
                driver = drivers.get(int(driver_number), {})
                results_by_name[_best_driver_name({**driver, **result})] = result

            laps_by_name: dict[str, list[dict[str, Any]]] = {}
            for lap in laps:
                driver_number = lap.get("driver_number")
                if driver_number is None:
                    continue
                driver = drivers.get(int(driver_number), {})
                name = _best_driver_name({**driver, **lap})
                laps_by_name.setdefault(name, []).append(lap)

            for contender in contender_names:
                result = results_by_name.get(contender, {})
                contender_points[contender].append(float(result.get("points") or 0))
                contender_laps = laps_by_name.get(contender, [])
                fastest = min(
                    (
                        float(lap["lap_duration"])
                        for lap in contender_laps
                        if lap.get("lap_duration") not in (None, "") and not lap.get("is_pit_out_lap")
                    ),
                    default=0.0,
                )
                top_speed = max(
                    (
                        max(
                            float(lap.get("st_speed") or 0),
                            float(lap.get("i1_speed") or 0),
                            float(lap.get("i2_speed") or 0),
                        )
                        for lap in contender_laps
                    ),
                    default=0.0,
                )
                contender_fastest_laps[contender].append(fastest)
                contender_speeds[contender].append(top_speed)

        return {
            "race_labels": race_labels,
            "contenders": contender_names,
            "points_series": [
                {"label": contender, "values": contender_points[contender]}
                for contender in contender_names
            ],
            "speed_series": [
                {"label": contender, "values": contender_speeds[contender]}
                for contender in contender_names
            ],
            "fastest_lap_series": [
                {"label": contender, "values": contender_fastest_laps[contender]}
                for contender in contender_names
            ],
        }

    def _build_completed_weekend_results(self, meetings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        completed_weekends: list[dict[str, Any]] = []
        for meeting in meetings:
            race_session = self._latest_race_session(meeting)
            if race_session is None:
                continue
            driver_lookup = self._build_driver_lookup(race_session["session_key"])
            completed_weekends.append(
                {
                    "id": f"weekend_{meeting['meeting_key']}",
                    "name": meeting["name"],
                    "date_range": meeting["date_range"],
                    "sessions": self._build_latest_results(meeting, driver_lookup),
                }
            )
        return completed_weekends

    def _build_dynamic_content(
        self,
        season: dict[str, Any],
        latest_completed: dict[str, Any],
        current_weekend_id: str,
        previous_weekend_id: str,
    ) -> dict[str, Any]:
        latest_name = latest_completed["name"]
        next_name = season["next_race"]["name"]
        leader_driver = season["leader_driver"]
        leader_team = season["leader_team"]
        leader_points = season["driver_standings"][0]["points"] if season["driver_standings"] else 0

        documents = [
            {
                "id": "doc_openf1_standings",
                "source_id": "source_formula1",
                "weekend_id": current_weekend_id,
                "title": f"{season['year']} championship standings snapshot",
                "url": "https://openf1.org/docs/#drivers-championship-beta",
                "kind": "standings",
                "publish_time": datetime.now(ZoneInfo(settings.local_timezone)).isoformat(),
                "race_stage": season["current_phase"],
                "stance": "official",
                "cluster_hint": "cluster_championship_lead",
                "entity_ids": ["theme_driver_standings", "theme_constructor_standings"],
                "content": f"{leader_driver} leads on {leader_points} points and {leader_team} tops the constructors table.",
            },
            {
                "id": "doc_openf1_schedule",
                "source_id": "source_formula1",
                "weekend_id": current_weekend_id,
                "title": f"{next_name} weekend schedule",
                "url": "https://openf1.org/docs/#sessions",
                "kind": "schedule",
                "publish_time": datetime.now(ZoneInfo(settings.local_timezone)).isoformat(),
                "race_stage": season["current_phase"],
                "stance": "official",
                "cluster_hint": "cluster_next_race_schedule",
                "entity_ids": ["theme_sprint_weekend"],
                "content": f"Next on the calendar is {next_name}.",
            },
        ]

        summary_outputs = [
            {
                "id": "summary_latest_result",
                "cluster_id": "cluster_latest_result",
                "label": "race_result",
                "title": f"{latest_name} is the latest fully completed race weekend",
                "body": f"The last official completed round was {latest_name}, which now anchors the current standings and season state.",
                "editorial_status": "approved",
                "updated_at": datetime.now(ZoneInfo(settings.local_timezone)).isoformat(),
            },
            {
                "id": "summary_next_schedule",
                "cluster_id": "cluster_next_race_schedule",
                "label": "official_update",
                "title": f"{next_name} is the next scheduled race",
                "body": f"The current phase is {season['current_phase'].replace('_', ' ')} and the next official race weekend is {next_name}.",
                "editorial_status": "approved",
                "updated_at": datetime.now(ZoneInfo(settings.local_timezone)).isoformat(),
            },
            {
                "id": "summary_championship_lead",
                "cluster_id": "cluster_championship_lead",
                "label": "analysis",
                "title": f"{leader_team} holds the strongest championship position right now",
                "body": f"{leader_driver} leads the Drivers' table and {leader_team} leads the Constructors', making them the clearest benchmark going into {next_name}.",
                "editorial_status": "approved",
                "updated_at": datetime.now(ZoneInfo(settings.local_timezone)).isoformat(),
            },
            {
                "id": "summary_prediction",
                "cluster_id": "cluster_prediction",
                "label": "prediction",
                "title": f"Current podium projection for {next_name}",
                "body": f"This prediction follows the current championship order and remains speculative until the next official session begins.",
                "editorial_status": "review_required",
                "updated_at": datetime.now(ZoneInfo(settings.local_timezone)).isoformat(),
            },
        ]

        clusters = [
            {
                "id": "cluster_latest_result",
                "weekend_id": previous_weekend_id,
                "slug": "latest-completed-race",
                "title": f"{latest_name} anchors the current season state",
                "label": "race_result",
                "status": "confirmed",
                "race_stage": "post_race",
                "freshness": "settled",
                "confidence": 0.99,
                "trend": "closed",
                "summary_output_id": "summary_latest_result",
                "document_ids": [],
                "entity_ids": [],
            },
            {
                "id": "cluster_next_race_schedule",
                "weekend_id": current_weekend_id,
                "slug": "next-race-schedule",
                "title": f"{next_name} is the next official race",
                "label": "official_update",
                "status": "confirmed",
                "race_stage": season["current_phase"],
                "freshness": "new",
                "confidence": 0.98,
                "trend": "rising",
                "summary_output_id": "summary_next_schedule",
                "document_ids": ["doc_openf1_schedule"],
                "entity_ids": [],
            },
            {
                "id": "cluster_championship_lead",
                "weekend_id": current_weekend_id,
                "slug": "championship-lead",
                "title": f"{leader_team} leads both title conversations",
                "label": "analysis",
                "status": "developing",
                "race_stage": season["current_phase"],
                "freshness": "live",
                "confidence": 0.9,
                "trend": "rising",
                "summary_output_id": "summary_championship_lead",
                "document_ids": ["doc_openf1_standings"],
                "entity_ids": [],
            },
            {
                "id": "cluster_prediction",
                "weekend_id": current_weekend_id,
                "slug": "next-race-prediction",
                "title": f"Prediction watch for {next_name}",
                "label": "prediction",
                "status": "watchlist",
                "race_stage": season["current_phase"],
                "freshness": "live",
                "confidence": 0.66,
                "trend": "watch",
                "summary_output_id": "summary_prediction",
                "document_ids": ["doc_openf1_standings", "doc_openf1_schedule"],
                "entity_ids": [],
            },
        ]

        return {
            "documents": documents,
            "clusters": clusters,
            "summary_outputs": summary_outputs,
            "distribution_assets": [
                {
                    "id": "asset_sync_digest",
                    "summary_output_id": "summary_next_schedule",
                    "kind": "digest_card",
                    "title": "OpenF1 sync status",
                    "body": f"Latest sync tracked the current phase as {season['current_phase'].replace('_', ' ')}.",
                }
            ],
        }
