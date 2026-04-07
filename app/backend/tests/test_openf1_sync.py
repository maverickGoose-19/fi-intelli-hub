from __future__ import annotations

from datetime import datetime
import unittest
from urllib.error import HTTPError
from zoneinfo import ZoneInfo

from app.seed import load_seed_data
from app.services.openf1 import OpenF1RateLimiter, OpenF1SyncService


class OpenF1SyncTests(unittest.TestCase):
    def test_rate_limiter_enforces_three_requests_per_second(self) -> None:
        current_time = 0.0
        sleeps: list[float] = []

        def fake_now() -> float:
            return current_time

        def fake_sleep(seconds: float) -> None:
            nonlocal current_time
            sleeps.append(seconds)
            current_time += seconds

        limiter = OpenF1RateLimiter(now_fn=fake_now, sleep_fn=fake_sleep)

        limiter.acquire()
        limiter.acquire()
        limiter.acquire()
        limiter.acquire()

        self.assertEqual(len(sleeps), 1)
        self.assertGreaterEqual(sleeps[0], 1.0)

    def test_rate_limiter_enforces_thirty_requests_per_minute(self) -> None:
        current_time = 0.0
        sleeps: list[float] = []

        def fake_now() -> float:
            return current_time

        def fake_sleep(seconds: float) -> None:
            nonlocal current_time
            sleeps.append(seconds)
            current_time += seconds

        limiter = OpenF1RateLimiter(now_fn=fake_now, sleep_fn=fake_sleep)

        for _ in range(30):
            limiter.acquire()
            current_time += 1.9

        limiter.acquire()

        self.assertEqual(len(sleeps), 1)
        self.assertGreaterEqual(sleeps[0], 2.0)

    def test_sync_builds_between_races_dashboard_state(self) -> None:
        fixtures: dict[tuple[str, tuple[tuple[str, object], ...]], list[dict[str, object]]] = {
            (
                "sessions",
                (("year", 2026),),
            ): [
                {
                    "meeting_key": 100,
                    "session_key": 1001,
                    "meeting_name": "Japanese Grand Prix",
                    "location": "Suzuka",
                    "circuit_short_name": "Suzuka",
                    "session_name": "Practice 1",
                    "date_start": "2026-03-27T02:00:00+00:00",
                    "date_end": "2026-03-27T03:00:00+00:00",
                },
                {
                    "meeting_key": 100,
                    "session_key": 1002,
                    "meeting_name": "Japanese Grand Prix",
                    "location": "Suzuka",
                    "circuit_short_name": "Suzuka",
                    "session_name": "Qualifying",
                    "date_start": "2026-03-28T06:00:00+00:00",
                    "date_end": "2026-03-28T07:00:00+00:00",
                },
                {
                    "meeting_key": 100,
                    "session_key": 1003,
                    "meeting_name": "Japanese Grand Prix",
                    "location": "Suzuka",
                    "circuit_short_name": "Suzuka",
                    "session_name": "Race",
                    "date_start": "2026-03-29T05:00:00+00:00",
                    "date_end": "2026-03-29T07:00:00+00:00",
                },
                {
                    "meeting_key": 101,
                    "session_key": 1011,
                    "meeting_name": "Miami Grand Prix",
                    "location": "Miami",
                    "circuit_short_name": "Miami",
                    "session_name": "Practice 1",
                    "date_start": "2026-05-01T16:30:00+00:00",
                    "date_end": "2026-05-01T17:30:00+00:00",
                },
                {
                    "meeting_key": 101,
                    "session_key": 1012,
                    "meeting_name": "Miami Grand Prix",
                    "location": "Miami",
                    "circuit_short_name": "Miami",
                    "session_name": "Sprint Qualifying",
                    "date_start": "2026-05-01T20:30:00+00:00",
                    "date_end": "2026-05-01T21:14:00+00:00",
                },
                {
                    "meeting_key": 101,
                    "session_key": 1013,
                    "meeting_name": "Miami Grand Prix",
                    "location": "Miami",
                    "circuit_short_name": "Miami",
                    "session_name": "Sprint",
                    "date_start": "2026-05-02T16:00:00+00:00",
                    "date_end": "2026-05-02T17:00:00+00:00",
                },
                {
                    "meeting_key": 101,
                    "session_key": 1014,
                    "meeting_name": "Miami Grand Prix",
                    "location": "Miami",
                    "circuit_short_name": "Miami",
                    "session_name": "Qualifying",
                    "date_start": "2026-05-02T20:00:00+00:00",
                    "date_end": "2026-05-02T21:00:00+00:00",
                },
                {
                    "meeting_key": 101,
                    "session_key": 1015,
                    "meeting_name": "Miami Grand Prix",
                    "location": "Miami",
                    "circuit_short_name": "Miami",
                    "session_name": "Race",
                    "date_start": "2026-05-03T20:00:00+00:00",
                    "date_end": "2026-05-03T22:00:00+00:00",
                },
            ],
            (
                "drivers",
                (("session_key", 1003),),
            ): [
                {"driver_number": 12, "full_name": "Kimi Antonelli", "team_name": "Mercedes", "name_acronym": "ANT"},
                {"driver_number": 63, "full_name": "George Russell", "team_name": "Mercedes", "name_acronym": "RUS"},
                {"driver_number": 16, "full_name": "Charles Leclerc", "team_name": "Ferrari", "name_acronym": "LEC"},
            ],
            (
                "championship_drivers",
                (("session_key", 1003),),
            ): [
                {"position": 1, "full_name": "Kimi Antonelli", "team_name": "Mercedes", "name_acronym": "ANT", "points": 72},
                {"position": 2, "full_name": "George Russell", "team_name": "Mercedes", "name_acronym": "RUS", "points": 63},
                {"position": 3, "full_name": "Charles Leclerc", "team_name": "Ferrari", "name_acronym": "LEC", "points": 49},
            ],
            (
                "championship_teams",
                (("session_key", 1003),),
            ): [
                {"position": 1, "team_name": "Mercedes", "points": 135},
                {"position": 2, "team_name": "Ferrari", "points": 90},
                {"position": 3, "team_name": "McLaren", "points": 46},
            ],
            (
                "session_result",
                (("session_key", 1001),),
            ): [
                {"position": 1, "driver_number": 63, "duration": "1:31.666"},
                {"position": 2, "driver_number": 12, "gap_to_leader": "+0.026s"},
                {"position": 3, "driver_number": 16, "gap_to_leader": "+0.289s"},
            ],
            (
                "session_result",
                (("session_key", 1002),),
            ): [
                {"position": 1, "driver_number": 12, "duration": "1:28.778"},
                {"position": 2, "driver_number": 63, "gap_to_leader": "+0.298s"},
                {"position": 3, "driver_number": 16, "gap_to_leader": "+0.627s"},
            ],
            (
                "session_result",
                (("session_key", 1003),),
            ): [
                {"position": 1, "driver_number": 12, "time": "1:28:03.403", "points": 25},
                {"position": 2, "driver_number": 63, "gap_to_leader": "+3.400s", "points": 18},
                {"position": 3, "driver_number": 16, "gap_to_leader": "+11.120s", "points": 15},
            ],
        }

        def fake_fetch(endpoint: str, params: dict[str, object]) -> list[dict[str, object]]:
            key = (endpoint, tuple(sorted(params.items())))
            return fixtures.get(key, [])

        service = OpenF1SyncService(fetch_json=fake_fetch)
        updated = service.sync(
            load_seed_data(),
            now=datetime(2026, 4, 2, 12, 0, tzinfo=ZoneInfo("America/Los_Angeles")),
        )

        self.assertEqual(updated["season"]["current_phase"], "between_races")
        self.assertEqual(updated["season"]["leader_driver"], "Kimi Antonelli")
        self.assertEqual(updated["season"]["leader_team"], "Mercedes")
        self.assertEqual(updated["season"]["next_race"]["name"], "Miami Grand Prix")
        self.assertEqual(updated["weekends"][1]["current"], True)
        self.assertEqual(updated["weekends"][0]["session_results"][0]["name"], "Practice 1")
        self.assertEqual(updated["season"]["completed_weekend_results"][0]["name"], "Japanese Grand Prix")

    def test_sync_reuses_cached_historical_sections_when_completed_meetings_match(self) -> None:
        seed_data = load_seed_data()
        seed_data["season"]["performance_charts"] = {
            "race_labels": ["Japanese Grand Prix"],
            "contenders": ["Kimi Antonelli"],
            "points_series": [{"label": "Kimi Antonelli", "values": [25]}],
            "speed_series": [{"label": "Kimi Antonelli", "values": [325]}],
            "fastest_lap_series": [{"label": "Kimi Antonelli", "values": [89.1]}],
        }
        seed_data["season"]["completed_weekend_results"] = [
            {
                "id": "weekend_100",
                "name": "Japanese Grand Prix",
                "date_range": "27 - 29 Mar 2026",
                "sessions": [{"name": "Race", "entries": []}],
            }
        ]
        fixtures: dict[tuple[str, tuple[tuple[str, object], ...]], list[dict[str, object]]] = {
            (
                "sessions",
                (("year", 2026),),
            ): [
                {
                    "meeting_key": 100,
                    "session_key": 1003,
                    "meeting_name": "Japanese Grand Prix",
                    "location": "Suzuka",
                    "circuit_short_name": "Suzuka",
                    "session_name": "Race",
                    "date_start": "2026-03-29T05:00:00+00:00",
                    "date_end": "2026-03-29T07:00:00+00:00",
                },
                {
                    "meeting_key": 101,
                    "session_key": 1015,
                    "meeting_name": "Miami Grand Prix",
                    "location": "Miami",
                    "circuit_short_name": "Miami",
                    "session_name": "Race",
                    "date_start": "2026-05-03T20:00:00+00:00",
                    "date_end": "2026-05-03T22:00:00+00:00",
                },
            ],
            (
                "drivers",
                (("session_key", 1003),),
            ): [
                {"driver_number": 12, "full_name": "Kimi Antonelli", "team_name": "Mercedes", "name_acronym": "ANT"},
            ],
            (
                "championship_drivers",
                (("session_key", 1003),),
            ): [
                {"position": 1, "full_name": "Kimi Antonelli", "team_name": "Mercedes", "name_acronym": "ANT", "points": 72},
            ],
            (
                "championship_teams",
                (("session_key", 1003),),
            ): [
                {"position": 1, "team_name": "Mercedes", "points": 135},
            ],
            (
                "session_result",
                (("session_key", 1003),),
            ): [
                {"position": 1, "driver_number": 12, "time": "1:28:03.403", "points": 25},
            ],
        }

        call_counts: dict[tuple[str, tuple[tuple[str, object], ...]], int] = {}

        def fake_fetch(endpoint: str, params: dict[str, object]) -> list[dict[str, object]]:
            key = (endpoint, tuple(sorted(params.items())))
            call_counts[key] = call_counts.get(key, 0) + 1
            return fixtures.get(key, [])

        service = OpenF1SyncService(fetch_json=fake_fetch)
        updated = service.sync(
            seed_data,
            now=datetime(2026, 4, 2, 12, 0, tzinfo=ZoneInfo("America/Los_Angeles")),
        )

        self.assertEqual(updated["season"]["performance_charts"]["race_labels"], ["Japanese Grand Prix"])
        self.assertEqual(len(updated["season"]["completed_weekend_results"]), 1)
        self.assertNotIn(("laps", (("session_key", 1003),)), call_counts)

    def test_sync_falls_back_when_optional_openf1_endpoints_404(self) -> None:
        fixtures: dict[tuple[str, tuple[tuple[str, object], ...]], list[dict[str, object]]] = {
            (
                "sessions",
                (("year", 2026),),
            ): [
                {
                    "meeting_key": 100,
                    "session_key": 1003,
                    "meeting_name": "Japanese Grand Prix",
                    "location": "Suzuka",
                    "circuit_short_name": "Suzuka",
                    "session_name": "Race",
                    "date_start": "2026-03-29T05:00:00+00:00",
                    "date_end": "2026-03-29T07:00:00+00:00",
                },
                {
                    "meeting_key": 101,
                    "session_key": 1015,
                    "meeting_name": "Miami Grand Prix",
                    "location": "Miami",
                    "circuit_short_name": "Miami",
                    "session_name": "Race",
                    "date_start": "2026-05-03T20:00:00+00:00",
                    "date_end": "2026-05-03T22:00:00+00:00",
                },
            ],
            (
                "drivers",
                (("session_key", 1003),),
            ): [
                {"driver_number": 12, "full_name": "Kimi Antonelli", "team_name": "Mercedes", "name_acronym": "ANT"},
            ],
            (
                "session_result",
                (("session_key", 1003),),
            ): [
                {"position": 1, "driver_number": 12, "time": "1:28:03.403", "points": 25},
            ],
        }

        def fake_fetch(endpoint: str, params: dict[str, object]) -> list[dict[str, object]]:
            if endpoint in {"championship_drivers", "championship_teams", "laps"}:
                raise HTTPError(
                    url=f"https://api.openf1.org/v1/{endpoint}",
                    code=404,
                    msg="Not Found",
                    hdrs=None,
                    fp=None,
                )
            key = (endpoint, tuple(sorted(params.items())))
            return fixtures.get(key, [])

        service = OpenF1SyncService(fetch_json=fake_fetch)
        updated = service.sync(
            load_seed_data(),
            now=datetime(2026, 4, 2, 12, 0, tzinfo=ZoneInfo("America/Los_Angeles")),
        )

        self.assertGreater(len(updated["season"]["driver_standings"]), 0)
        self.assertGreater(len(updated["season"]["constructor_standings"]), 0)
        self.assertEqual(updated["season"]["completed_weekend_results"][0]["name"], "Japanese Grand Prix")


if __name__ == "__main__":
    unittest.main()
