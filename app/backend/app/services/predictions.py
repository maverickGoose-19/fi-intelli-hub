from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import json
import logging
import math
from pathlib import Path
import random
from time import perf_counter
from typing import Any

from app.config import settings

try:
    import fastf1
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    fastf1 = None

try:
    import requests
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    requests = None

try:
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    GradientBoostingClassifier = None
    RandomForestClassifier = None


FEATURE_ORDER = [
    "championship_form",
    "constructor_strength",
    "season_wins",
    "podium_rate",
    "qualifying_sharpness",
    "recent_race_form",
    "career_wins",
    "junior_provenance",
    "experience_depth",
    "track_fit",
    "tyre_management_fit",
    "strategy_alignment",
    "reliability",
    "weather_adaptability",
]

FEATURE_META = {
    "championship_form": {
        "label": "Championship form",
        "description": "Current points, ranking, and recent momentum entering the weekend.",
    },
    "constructor_strength": {
        "label": "Car formula",
        "description": "Current constructor package strength, pit crew sharpness, and car platform quality.",
    },
    "season_wins": {
        "label": "Season wins",
        "description": "Win conversion so far this season.",
    },
    "podium_rate": {
        "label": "Podium rate",
        "description": "Ability to stay in the fight across multiple race conditions.",
    },
    "qualifying_sharpness": {
        "label": "Qualifying pace",
        "description": "Average grid strength and one-lap execution.",
    },
    "recent_race_form": {
        "label": "Recent race form",
        "description": "Last-race finishing trend and consistency score.",
    },
    "career_wins": {
        "label": "Career wins",
        "description": "Senior-category race-winning experience.",
    },
    "junior_provenance": {
        "label": "Junior leagues",
        "description": "Formula 2, Formula 3, and junior series record.",
    },
    "experience_depth": {
        "label": "Experience",
        "description": "Seasons at top level and high-pressure decision-making.",
    },
    "track_fit": {
        "label": "Track fit",
        "description": "Street-circuit and layout suitability for the upcoming venue.",
    },
    "tyre_management_fit": {
        "label": "Tyre management",
        "description": "Ability to protect the tyre life profile expected this weekend.",
    },
    "strategy_alignment": {
        "label": "Expected strategy",
        "description": "Fit for the likely race plan and sprint-weekend setup compromise.",
    },
    "reliability": {
        "label": "Reliability",
        "description": "Mechanical finish probability and operational cleanliness.",
    },
    "weather_adaptability": {
        "label": "Weather adaptability",
        "description": "Response to changing grip, heat, and wet-track disruption.",
    },
}

BASE_FEATURE_WEIGHTS = {
    "championship_form": 1.25,
    "constructor_strength": 1.15,
    "season_wins": 0.95,
    "podium_rate": 0.9,
    "qualifying_sharpness": 1.0,
    "recent_race_form": 0.95,
    "career_wins": 0.55,
    "junior_provenance": 0.5,
    "experience_depth": 0.6,
    "track_fit": 0.9,
    "tyre_management_fit": 0.85,
    "strategy_alignment": 0.75,
    "reliability": 0.8,
    "weather_adaptability": 0.55,
}

DRIVER_PROFILE_OVERRIDES = {
    "Kimi Antonelli": {
        "career_wins": 3,
        "career_poles": 2,
        "junior_wins": 19,
        "junior_titles": 3,
        "seasons_experience": 1,
        "qualifying_skill": 0.87,
        "racecraft": 0.88,
        "street_skill": 0.84,
        "tyre_management": 0.83,
        "wet_skill": 0.81,
        "adaptability": 0.89,
    },
    "George Russell": {
        "career_wins": 6,
        "career_poles": 8,
        "junior_wins": 27,
        "junior_titles": 3,
        "seasons_experience": 8,
        "qualifying_skill": 0.9,
        "racecraft": 0.87,
        "street_skill": 0.82,
        "tyre_management": 0.83,
        "wet_skill": 0.88,
        "adaptability": 0.84,
    },
    "Charles Leclerc": {
        "career_wins": 9,
        "career_poles": 26,
        "junior_wins": 19,
        "junior_titles": 2,
        "seasons_experience": 9,
        "qualifying_skill": 0.93,
        "racecraft": 0.86,
        "street_skill": 0.92,
        "tyre_management": 0.8,
        "wet_skill": 0.78,
        "adaptability": 0.84,
    },
    "Lewis Hamilton": {
        "career_wins": 105,
        "career_poles": 104,
        "junior_wins": 29,
        "junior_titles": 4,
        "seasons_experience": 20,
        "qualifying_skill": 0.91,
        "racecraft": 0.95,
        "street_skill": 0.9,
        "tyre_management": 0.91,
        "wet_skill": 0.97,
        "adaptability": 0.93,
    },
    "Lando Norris": {
        "career_wins": 7,
        "career_poles": 8,
        "junior_wins": 24,
        "junior_titles": 4,
        "seasons_experience": 8,
        "qualifying_skill": 0.89,
        "racecraft": 0.87,
        "street_skill": 0.84,
        "tyre_management": 0.84,
        "wet_skill": 0.82,
        "adaptability": 0.88,
    },
    "Oscar Piastri": {
        "career_wins": 5,
        "career_poles": 6,
        "junior_wins": 21,
        "junior_titles": 3,
        "seasons_experience": 4,
        "qualifying_skill": 0.88,
        "racecraft": 0.88,
        "street_skill": 0.81,
        "tyre_management": 0.82,
        "wet_skill": 0.8,
        "adaptability": 0.9,
    },
    "Max Verstappen": {
        "career_wins": 65,
        "career_poles": 42,
        "junior_wins": 16,
        "junior_titles": 0,
        "seasons_experience": 12,
        "qualifying_skill": 0.95,
        "racecraft": 0.97,
        "street_skill": 0.95,
        "tyre_management": 0.91,
        "wet_skill": 0.93,
        "adaptability": 0.94,
    },
    "Carlos Sainz": {
        "career_wins": 4,
        "career_poles": 7,
        "junior_wins": 19,
        "junior_titles": 2,
        "seasons_experience": 12,
        "qualifying_skill": 0.84,
        "racecraft": 0.85,
        "street_skill": 0.86,
        "tyre_management": 0.84,
        "wet_skill": 0.8,
        "adaptability": 0.86,
    },
    "Fernando Alonso": {
        "career_wins": 32,
        "career_poles": 22,
        "junior_wins": 31,
        "junior_titles": 3,
        "seasons_experience": 23,
        "qualifying_skill": 0.83,
        "racecraft": 0.94,
        "street_skill": 0.88,
        "tyre_management": 0.93,
        "wet_skill": 0.9,
        "adaptability": 0.89,
    },
}

TEAM_PROFILE_OVERRIDES = {
    "Mercedes": {
        "car_formula_label": "Balanced high-downforce platform",
        "race_pace": 0.93,
        "qualifying_pace": 0.92,
        "pit_crew": 0.86,
        "reliability": 0.9,
        "tyre_usage": 0.86,
        "street_bias": 0.83,
    },
    "Ferrari": {
        "car_formula_label": "Front-end sharp qualifying package",
        "race_pace": 0.87,
        "qualifying_pace": 0.91,
        "pit_crew": 0.84,
        "reliability": 0.85,
        "tyre_usage": 0.79,
        "street_bias": 0.89,
    },
    "McLaren": {
        "car_formula_label": "High-speed aero efficiency package",
        "race_pace": 0.86,
        "qualifying_pace": 0.87,
        "pit_crew": 0.83,
        "reliability": 0.84,
        "tyre_usage": 0.84,
        "street_bias": 0.8,
    },
    "Red Bull Racing": {
        "car_formula_label": "Peak-downforce aggressive rotation package",
        "race_pace": 0.84,
        "qualifying_pace": 0.88,
        "pit_crew": 0.9,
        "reliability": 0.8,
        "tyre_usage": 0.85,
        "street_bias": 0.86,
    },
    "Racing Bulls": {
        "car_formula_label": "Reactive midfield street package",
        "race_pace": 0.67,
        "qualifying_pace": 0.68,
        "pit_crew": 0.77,
        "reliability": 0.78,
        "tyre_usage": 0.74,
        "street_bias": 0.74,
    },
    "Haas F1 Team": {
        "car_formula_label": "Low-drag opportunistic package",
        "race_pace": 0.66,
        "qualifying_pace": 0.65,
        "pit_crew": 0.74,
        "reliability": 0.76,
        "tyre_usage": 0.72,
        "street_bias": 0.68,
    },
    "Alpine": {
        "car_formula_label": "Sensitive balance development package",
        "race_pace": 0.62,
        "qualifying_pace": 0.64,
        "pit_crew": 0.74,
        "reliability": 0.74,
        "tyre_usage": 0.7,
        "street_bias": 0.66,
    },
    "Williams": {
        "car_formula_label": "Straight-line efficiency package",
        "race_pace": 0.6,
        "qualifying_pace": 0.63,
        "pit_crew": 0.73,
        "reliability": 0.75,
        "tyre_usage": 0.67,
        "street_bias": 0.71,
    },
    "Audi": {
        "car_formula_label": "Transition-year efficiency package",
        "race_pace": 0.58,
        "qualifying_pace": 0.59,
        "pit_crew": 0.72,
        "reliability": 0.72,
        "tyre_usage": 0.69,
        "street_bias": 0.66,
    },
    "Aston Martin": {
        "car_formula_label": "Mechanical grip development package",
        "race_pace": 0.57,
        "qualifying_pace": 0.58,
        "pit_crew": 0.74,
        "reliability": 0.73,
        "tyre_usage": 0.7,
        "street_bias": 0.68,
    },
    "Cadillac": {
        "car_formula_label": "New-entry baseline package",
        "race_pace": 0.5,
        "qualifying_pace": 0.51,
        "pit_crew": 0.69,
        "reliability": 0.68,
        "tyre_usage": 0.63,
        "street_bias": 0.6,
    },
}

DEFAULT_TRACK_PROFILE = {
    "track_type": "Mixed layout",
    "street_circuit": 0.4,
    "overtaking": 0.62,
    "tyre_stress": 0.57,
    "traction_importance": 0.66,
    "track_evolution": 0.6,
    "weather_variability": 0.42,
    "expected_strategy": "Likely one-stop with flexibility around an early safety car.",
    "tyre_outlook": "Balanced tyre usage with pressure on rear temperatures late in stints.",
    "notes": "Default circuit model used because no specific track override matched the upcoming venue.",
}

TRACK_PROFILE_OVERRIDES = {
    "miami": {
        "track_type": "Street-style temporary circuit",
        "street_circuit": 0.84,
        "overtaking": 0.78,
        "tyre_stress": 0.63,
        "traction_importance": 0.81,
        "track_evolution": 0.74,
        "weather_variability": 0.68,
        "expected_strategy": "Sprint weekend bias with a likely one-stop race and high value on track position after Saturday.",
        "tyre_outlook": "Rear-limited overheating risk rewards smooth traction and disciplined tyre warm-up.",
        "notes": "Miami usually rewards confidence over traction zones, efficient straight-line speed, and tyre preservation in heat.",
    },
    "australia": {
        "track_type": "Fast semi-street circuit",
        "street_circuit": 0.72,
        "overtaking": 0.61,
        "tyre_stress": 0.56,
        "traction_importance": 0.72,
        "track_evolution": 0.69,
        "weather_variability": 0.63,
        "expected_strategy": "Front-runners benefit from clean air; one-stop remains viable with a safety-car branch.",
        "tyre_outlook": "Front tyre preparation matters in qualifying but race pace stays rear-limited.",
        "notes": "Albert Park-style profiles favor confident rotation and rapid adaptation to evolving grip.",
    },
    "china": {
        "track_type": "Long-radius technical circuit",
        "street_circuit": 0.18,
        "overtaking": 0.73,
        "tyre_stress": 0.7,
        "traction_importance": 0.68,
        "track_evolution": 0.58,
        "weather_variability": 0.49,
        "expected_strategy": "High-deg long corners create strategy pressure and open the undercut window.",
        "tyre_outlook": "Front-left degradation and long-corner management are central to pace retention.",
        "notes": "China-style layouts reward balance through extended loaded corners more than pure qualifying bite.",
    },
    "japan": {
        "track_type": "High-speed technical circuit",
        "street_circuit": 0.08,
        "overtaking": 0.39,
        "tyre_stress": 0.79,
        "traction_importance": 0.62,
        "track_evolution": 0.47,
        "weather_variability": 0.55,
        "expected_strategy": "Qualifying and clean air matter heavily, with tyre life depending on aerodynamic stability.",
        "tyre_outlook": "High-speed loaded corners punish sliding and reward platform confidence.",
        "notes": "Suzuka-style profiles amplify car balance, confidence on fast change of direction, and disciplined tyres.",
    },
}

SOURCE_STACK = [
    {
        "label": "OpenF1 live season cache",
        "kind": "data",
        "role": "Current season standings, session results, pace traces, and live weekend context already wired into this codebase.",
        "url": "https://openf1.org/docs",
    },
    {
        "label": "FastF1",
        "kind": "data",
        "role": "Telemetry-compatible data source for session, tyre, and lap-level enrichment when a deeper research pipeline is added.",
        "url": "https://docs.fastf1.dev/getting_started/basics.html",
    },
    {
        "label": "Ergast Developer API",
        "kind": "data",
        "role": "Historical archive reference for long-run driver, team, and circuit priors from 1950 onward.",
        "url": "http://ergast.com/mrd/",
    },
    {
        "label": "scikit-learn workflow",
        "kind": "modeling",
        "role": "Reference workflow for gradient-boosted and classical classification approaches described in the methodology panel.",
        "url": "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingClassifier.html",
    },
    {
        "label": "XGBoost classifier",
        "kind": "modeling",
        "role": "Reference tree-boosting option for a future production training job once more labeled race data is wired in.",
        "url": "https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBClassifier",
    },
    {
        "label": "F1 Race Replay",
        "kind": "inspiration",
        "role": "Telemetry and tyre visualization reference for future simulation overlays and race-shape replays.",
        "url": "https://github.com/IAmTomShaw/f1-race-replay",
    },
    {
        "label": "F1 race prediction simulator",
        "kind": "inspiration",
        "role": "Multi-factor simulation reference covering driver skill, car quality, track characteristics, and weather.",
        "url": "https://github.com/mehmetkahya0/f1-race-prediction",
    },
    {
        "label": "SQL and Python team-performance article",
        "kind": "analysis",
        "role": "Warehouse-style aggregation reference for team trend tables and longitudinal performance views.",
        "url": "https://medium.com/@themathlab/analyzing-formula-1-team-performance-with-sql-and-python-1e30f1e154b9",
    },
]

TRAINING_CACHE_PATH = Path(__file__).resolve().parents[2] / "data" / "prediction-training-cache.json"
FASTF1_CACHE_PATH = Path(__file__).resolve().parents[3] / ".fastf1"
logger = logging.getLogger(__name__)


@dataclass
class SeasonStats:
    wins: dict[str, int]
    podiums: dict[str, int]
    finish_positions: dict[str, list[int]]
    qualifying_positions: dict[str, list[int]]
    recent_positions: dict[str, list[int]]
    team_lookup: dict[str, str]
    completed_races: int


@dataclass
class HistoricalTrainingBundle:
    rows: list[list[float]]
    labels: list[int]
    metadata: dict[str, Any]


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def _safe_mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _sigmoid(value: float) -> float:
    if value >= 0:
        exp_value = math.exp(-value)
        return 1.0 / (1.0 + exp_value)
    exp_value = math.exp(value)
    return exp_value / (1.0 + exp_value)


def _softmax(values: list[float]) -> list[float]:
    if not values:
        return []
    pivot = max(values)
    exps = [math.exp(value - pivot) for value in values]
    total = sum(exps) or 1.0
    return [value / total for value in exps]


def _normalize_count(value: float, scale: float) -> float:
    if scale <= 0:
        return 0.0
    return _clamp(value / scale)


def _display_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def _track_key(*values: str | None) -> str:
    combined = " ".join(value or "" for value in values).lower()
    for key in TRACK_PROFILE_OVERRIDES:
        if key in combined:
            return key
    return "default"


def _race_session(weekend: dict[str, Any]) -> dict[str, Any] | None:
    sessions = weekend.get("sessions", [])
    for preferred_name in ("Race", "Grand Prix"):
        for session in sessions:
            if session.get("name") == preferred_name:
                return session
    for session in sessions:
        if session.get("category") == "race":
            return session
    return None


def _qualifying_session(weekend: dict[str, Any]) -> dict[str, Any] | None:
    sessions = weekend.get("sessions", [])
    for preferred_name in ("Qualifying", "Sprint Qualifying"):
        for session in sessions:
            if session.get("name") == preferred_name:
                return session
    for session in sessions:
        if session.get("category") == "qualifying":
            return session
    return None


class RaceWinnerPredictionService:
    def build_prediction_payload(
        self,
        season: dict[str, Any],
        current_weekend: dict[str, Any],
        previous_weekend: dict[str, Any] | None,
    ) -> dict[str, Any]:
        started_at = perf_counter()
        completed_weekends = list(season.get("completed_weekend_results", []))
        if previous_weekend and all(weekend["id"] != previous_weekend["id"] for weekend in completed_weekends):
            completed_weekends.append(
                {
                    "id": previous_weekend["id"],
                    "name": previous_weekend["name"],
                    "date_range": previous_weekend.get("date_range"),
                    "sessions": previous_weekend.get("session_results", []),
                }
            )

        standings = list(season.get("driver_standings", []))
        constructor_standings = list(season.get("constructor_standings", []))
        next_race = dict(season.get("next_race", {}))
        track_profile = self._track_profile(next_race.get("name"), next_race.get("venue"))
        season_stats = self._build_season_stats(completed_weekends, standings)
        constructor_lookup = {entry["name"]: entry for entry in constructor_standings}

        training_rows, training_labels = self._build_training_dataset(
            completed_weekends,
            standings,
            constructor_lookup,
            season_stats,
        )
        model = self._fit_logistic_regression(training_rows, training_labels)
        historical_bundle = self._load_historical_training_bundle()
        external_model = self._fit_external_model(historical_bundle)
        schedule_context = self._fastf1_schedule_context(season.get("year"), next_race.get("name"))
        training_completed_races = historical_bundle.metadata.get("races", season_stats.completed_races)
        training_observations = historical_bundle.metadata.get("observations", len(training_rows))
        training_positive_examples = historical_bundle.metadata.get("positive_examples", sum(training_labels))

        contenders = []
        raw_scores: list[float] = []
        selected_entries = standings[: min(len(standings), 12)]
        for entry in selected_entries:
            driver = entry["name"]
            team = entry.get("team") or season_stats.team_lookup.get(driver, "Unknown Team")
            profile = self._driver_profile(driver, entry)
            team_profile = self._team_profile(team, constructor_lookup.get(team))
            features = self._feature_map(
                entry=entry,
                team=team,
                driver_profile=profile,
                team_profile=team_profile,
                season_stats=season_stats,
                track_profile=track_profile,
                total_drivers=max(len(standings), 1),
                driver_points_ceiling=max(float(item.get("points") or 0.0) for item in standings) if standings else 1.0,
                constructor_lookup=constructor_lookup,
            )
            base_score = self._base_score(features)
            learned_score = self._predict_logistic(model, features)
            external_score = self._predict_external_model(external_model, features)
            combined_score = (
                (0.34 * base_score) + (0.18 * learned_score) + (0.48 * external_score)
                if external_model
                else (0.58 * base_score) + (0.42 * learned_score)
            )
            raw_scores.append(combined_score * 3.2)
            contenders.append(
                {
                    "driver": driver,
                    "team": team,
                    "features": features,
                    "base_score": base_score,
                    "learned_score": learned_score,
                    "external_score": external_score,
                    "combined_score": combined_score,
                    "team_profile": team_profile,
                }
            )

        win_probabilities = _softmax(raw_scores)
        podium_probabilities = self._simulate_podium_probabilities(contenders, raw_scores)
        sorted_contenders = []
        for index, contender in enumerate(contenders):
            contender["win_probability"] = win_probabilities[index]
            contender["podium_probability"] = podium_probabilities.get(contender["driver"], 0.0)
            sorted_contenders.append(contender)

        sorted_contenders.sort(key=lambda item: item["combined_score"], reverse=True)

        champion_gap = 0.0
        if len(sorted_contenders) > 1:
            champion_gap = sorted_contenders[0]["combined_score"] - sorted_contenders[1]["combined_score"]

        payload_contenders = []
        for rank, contender in enumerate(sorted_contenders, start=1):
            payload_contenders.append(
                {
                    "rank": rank,
                    "driver": contender["driver"],
                    "team": contender["team"],
                    "win_probability": round(contender["win_probability"], 4),
                    "podium_probability": round(contender["podium_probability"], 4),
                    "model_score": round(contender["combined_score"], 4),
                    "confidence": self._confidence_label(contender["win_probability"], champion_gap),
                    "outlook": self._build_outlook(
                        contender["driver"],
                        contender["team"],
                        contender["features"],
                        season_stats,
                        track_profile,
                    ),
                    "evidence": self._evidence_points(
                        contender["driver"],
                        contender["team"],
                        contender["features"],
                        season_stats,
                        track_profile,
                    ),
                    "features": [
                        {
                            "key": key,
                            "label": FEATURE_META[key]["label"],
                            "value": round(contender["features"][key], 4),
                            "display_value": _display_percent(contender["features"][key]),
                            "impact": FEATURE_META[key]["description"],
                        }
                        for key in FEATURE_ORDER
                    ],
                }
            )

        feature_importance = self._feature_importance(model, external_model)
        constructor_outlook = self._constructor_outlook(constructor_standings)
        logger.info(
            "Prediction model ready for %s in %.2fs; external_model=%s cache=%s",
            next_race.get("name", current_weekend["name"]),
            perf_counter() - started_at,
            bool(external_model),
            TRAINING_CACHE_PATH.exists(),
        )

        return {
            "race": {
                "name": next_race.get("name", current_weekend["name"]),
                "date_range": next_race.get("date_range", current_weekend.get("date_range")),
                "weekend_format": next_race.get("weekend_format", "Standard"),
                "venue": next_race.get("venue", current_weekend.get("name")),
                "phase": season.get("current_phase", current_weekend.get("stage")),
            },
            "track": {
                "track_type": track_profile["track_type"],
                "street_circuit_bias": round(track_profile["street_circuit"], 4),
                "overtaking_score": round(track_profile["overtaking"], 4),
                "tyre_stress_score": round(track_profile["tyre_stress"], 4),
                "traction_importance": round(track_profile["traction_importance"], 4),
                "track_evolution": round(track_profile["track_evolution"], 4),
                "weather_variability": round(track_profile["weather_variability"], 4),
                "expected_strategy": track_profile["expected_strategy"],
                "tyre_outlook": track_profile["tyre_outlook"],
                "notes": track_profile["notes"],
            },
            "model": {
                "name": "Hybrid F1 Winner Model",
                "version": "0.1.0",
                "overview": (
                    "The model blends engineered motorsport priors, an in-app calibration layer, and a historical "
                    "classifier trained on Ergast-compatible race and qualifying data when that stack is available."
                ),
                "target": "Predict the most likely winner of the next Formula 1 race weekend.",
                "training": {
                    "completed_races": training_completed_races,
                    "observations": training_observations,
                    "positive_examples": training_positive_examples,
                    "blend": (
                        "34% domain feature prior + 18% in-app calibration + 48% historical classifier"
                        if external_model
                        else "58% domain feature prior + 42% calibrated logistic winner model"
                    ),
                },
                "confidence": self._overall_confidence(training_completed_races, champion_gap),
                "notes": [
                    "Inference, not an official result. The current repo contributes live season context while the optional historical stack lifts sample size.",
                    (
                        "Historical training is live: Ergast-compatible results and qualifying data were cached locally and FastF1 schedule metadata was used for event context."
                        if external_model
                        else "The service falls back to the in-app model when the historical training stack is unavailable."
                    ),
                    "Tyre and strategy signals are modeled as expected weekend conditions rather than official Pirelli or team declarations.",
                    (
                        f"FastF1 schedule check matched {schedule_context} for the current race calendar."
                        if schedule_context
                        else "FastF1 schedule metadata was not available for this runtime, so the app kept its existing season calendar."
                    ),
                ],
            },
            "contenders": payload_contenders,
            "feature_importance": feature_importance,
            "constructor_outlook": constructor_outlook,
            "scenario_matrix": self._scenario_matrix(track_profile, payload_contenders[:3]),
            "source_stack": SOURCE_STACK,
        }

    def _load_historical_training_bundle(self) -> HistoricalTrainingBundle:
        empty_bundle = HistoricalTrainingBundle(
            rows=[],
            labels=[],
            metadata={"races": 0, "observations": 0, "positive_examples": 0, "source": "fallback"},
        )
        if requests is None:
            logger.warning("Requests is unavailable; prediction service is using in-app fallback only.")
            return empty_bundle

        try:
            if TRAINING_CACHE_PATH.exists():
                payload = json.loads(TRAINING_CACHE_PATH.read_text(encoding="utf-8"))
                generated_at = datetime.fromisoformat(payload.get("generated_at", "1970-01-01T00:00:00+00:00"))
                if (datetime.now(UTC) - generated_at) < timedelta(days=7):
                    logger.info("Using cached historical training bundle from %s", generated_at.isoformat())
                    return HistoricalTrainingBundle(
                        rows=payload.get("rows", []),
                        labels=payload.get("labels", []),
                        metadata=payload.get("metadata", {}),
                    )
        except Exception as error:  # noqa: BLE001
            logger.warning("Historical training cache could not be read; rebuilding. error=%s", error)

        if settings.app_env == "production" and not settings.prediction_enable_live_training:
            logger.info(
                "Skipping live historical training in production because PREDICTION_ENABLE_LIVE_TRAINING is disabled."
            )
            return empty_bundle

        try:
            bundle = self._fetch_historical_training_bundle()
        except Exception as error:  # noqa: BLE001
            logger.warning("Historical training fetch failed; falling back to in-app model. error=%s", error)
            return empty_bundle
        if bundle.rows:
            TRAINING_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            TRAINING_CACHE_PATH.write_text(
                json.dumps(
                    {
                        "generated_at": datetime.now(UTC).isoformat(),
                        "rows": bundle.rows,
                        "labels": bundle.labels,
                        "metadata": bundle.metadata,
                    },
                    ensure_ascii=True,
                    indent=2,
                ),
                encoding="utf-8",
            )
            logger.info(
                "Stored historical training bundle at %s with %s races and %s observations",
                TRAINING_CACHE_PATH,
                bundle.metadata.get("races"),
                bundle.metadata.get("observations"),
            )
            return bundle
        logger.info("Historical training bundle returned no rows; using in-app fallback.")
        return empty_bundle

    def _fetch_historical_training_bundle(self) -> HistoricalTrainingBundle:
        logger.info("Fetching historical training data for prediction model.")
        rows: list[list[float]] = []
        labels: list[int] = []
        seasons = [2024]
        total_races = 0

        for season_year in seasons:
            schedule = self._ergast_races(f"/{season_year}.json")
            if not schedule:
                continue
            season_results = {
                race.get("round"): race
                for race in self._ergast_paginated_races(f"/{season_year}/results.json")
            }
            season_qualifying = {
                race.get("round"): race
                for race in self._ergast_paginated_races(f"/{season_year}/qualifying.json")
            }

            driver_points: dict[str, float] = defaultdict(float)
            driver_wins: dict[str, int] = defaultdict(int)
            driver_podiums: dict[str, int] = defaultdict(int)
            driver_recent_positions: dict[str, list[int]] = defaultdict(list)
            driver_qualifying_positions: dict[str, list[int]] = defaultdict(list)
            constructor_points: dict[str, float] = defaultdict(float)
            driver_teams: dict[str, str] = {}

            for race in schedule:
                round_number = race.get("round")
                if not round_number:
                    continue

                race_payload = season_results.get(str(round_number)) or season_results.get(round_number)
                qualifying_payload = season_qualifying.get(str(round_number)) or season_qualifying.get(round_number) or {}
                if not race_payload:
                    continue
                result_rows = race_payload.get("Results", [])
                qualifying_rows = qualifying_payload.get("QualifyingResults", [])
                if not result_rows:
                    continue

                total_races += 1
                track_profile = self._track_profile(
                    race_payload.get("raceName"),
                    race_payload.get("Circuit", {}).get("circuitName"),
                )
                field_drivers = []
                qualifying_map: dict[str, int] = {}

                for row in qualifying_rows:
                    driver_name = self._ergast_driver_name(row.get("Driver", {}))
                    qualifying_map[driver_name] = int(row.get("position") or 99)

                for row in result_rows:
                    driver_name = self._ergast_driver_name(row.get("Driver", {}))
                    team_name = row.get("Constructor", {}).get("name", "Unknown Team")
                    driver_teams[driver_name] = team_name
                    field_drivers.append(driver_name)

                driver_order = sorted(
                    field_drivers,
                    key=lambda name: (-driver_points[name], -driver_wins[name], name),
                )
                driver_position_lookup = {name: index + 1 for index, name in enumerate(driver_order)}
                team_order = sorted(
                    {driver_teams[name] for name in field_drivers},
                    key=lambda team: (-constructor_points[team], team),
                )
                constructor_lookup = {
                    team: {"position": index + 1, "points": constructor_points[team]}
                    for index, team in enumerate(team_order)
                }

                season_stats = SeasonStats(
                    wins=dict(driver_wins),
                    podiums=dict(driver_podiums),
                    finish_positions={key: value[-3:] for key, value in driver_recent_positions.items()},
                    qualifying_positions={key: value[-3:] for key, value in driver_qualifying_positions.items()},
                    recent_positions={key: value[-3:] for key, value in driver_recent_positions.items()},
                    team_lookup=dict(driver_teams),
                    completed_races=max(total_races - 1, 0),
                )

                driver_points_ceiling = max((driver_points[name] for name in field_drivers), default=25.0)
                total_drivers = len(field_drivers)

                for row in result_rows:
                    driver_name = self._ergast_driver_name(row.get("Driver", {}))
                    team_name = row.get("Constructor", {}).get("name", "Unknown Team")
                    qualifying_positions = season_stats.qualifying_positions.setdefault(driver_name, [])
                    if driver_name in qualifying_map:
                        qualifying_positions = [*qualifying_positions, qualifying_map[driver_name]]
                        season_stats.qualifying_positions[driver_name] = qualifying_positions[-3:]

                    features = self._feature_map(
                        entry={
                            "name": driver_name,
                            "position": driver_position_lookup.get(driver_name, total_drivers),
                            "points": driver_points[driver_name],
                        },
                        team=team_name,
                        driver_profile=self._driver_profile(
                            driver_name,
                            {"name": driver_name, "position": driver_position_lookup.get(driver_name, total_drivers)},
                        ),
                        team_profile=self._team_profile(team_name, constructor_lookup.get(team_name)),
                        season_stats=season_stats,
                        track_profile=track_profile,
                        total_drivers=total_drivers,
                        driver_points_ceiling=driver_points_ceiling,
                        constructor_lookup=constructor_lookup,
                    )
                    if driver_name in qualifying_map:
                        grid_score = 1.0 - ((qualifying_map[driver_name] - 1.0) / max(total_drivers - 1, 1))
                        features["qualifying_sharpness"] = _clamp(
                            (features["qualifying_sharpness"] * 0.55) + (grid_score * 0.45)
                        )

                    rows.append([features[key] for key in FEATURE_ORDER])
                    labels.append(1 if int(row.get("position") or 99) == 1 else 0)

                for row in qualifying_rows:
                    driver_name = self._ergast_driver_name(row.get("Driver", {}))
                    driver_qualifying_positions[driver_name].append(int(row.get("position") or 99))
                    driver_qualifying_positions[driver_name] = driver_qualifying_positions[driver_name][-3:]

                for row in result_rows:
                    driver_name = self._ergast_driver_name(row.get("Driver", {}))
                    team_name = row.get("Constructor", {}).get("name", "Unknown Team")
                    finish_position = int(row.get("position") or 99)
                    driver_recent_positions[driver_name].append(finish_position)
                    driver_recent_positions[driver_name] = driver_recent_positions[driver_name][-3:]
                    driver_points[driver_name] += float(row.get("points") or 0.0)
                    constructor_points[team_name] += float(row.get("points") or 0.0)
                    if finish_position == 1:
                        driver_wins[driver_name] += 1
                    if finish_position <= 3:
                        driver_podiums[driver_name] += 1

        return HistoricalTrainingBundle(
            rows=rows,
            labels=labels,
            metadata={
                "races": total_races,
                "observations": len(rows),
                "positive_examples": sum(labels),
                "source": "ergast-compatible",
            },
        )

    def _ergast_races(self, path: str) -> list[dict[str, Any]]:
        if requests is None:
            return []
        response = requests.get(
            f"https://api.jolpi.ca/ergast/f1{path}",
            timeout=settings.prediction_http_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("MRData", {}).get("RaceTable", {}).get("Races", [])

    def _ergast_paginated_races(self, path: str) -> list[dict[str, Any]]:
        if requests is None:
            return []
        races: list[dict[str, Any]] = []
        offset = 0
        limit = 100
        while True:
            response = requests.get(
                f"https://api.jolpi.ca/ergast/f1{path}?limit={limit}&offset={offset}",
                timeout=settings.prediction_http_timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json().get("MRData", {})
            table_races = payload.get("RaceTable", {}).get("Races", [])
            races.extend(table_races)
            total = int(payload.get("total", 0) or 0)
            offset += limit
            if offset >= total or not table_races:
                break
        return races

    def _ergast_driver_name(self, driver: dict[str, Any]) -> str:
        given_name = str(driver.get("givenName", "")).strip()
        family_name = str(driver.get("familyName", "")).strip()
        full_name = f"{given_name} {family_name}".strip()
        return full_name or str(driver.get("driverId", "Unknown Driver"))

    def _fit_external_model(self, bundle: HistoricalTrainingBundle) -> dict[str, Any] | None:
        if not bundle.rows or GradientBoostingClassifier is None or RandomForestClassifier is None:
            return None

        gradient_boosting = GradientBoostingClassifier(
            random_state=42,
            n_estimators=240,
            learning_rate=0.05,
            max_depth=3,
            subsample=0.9,
        )
        random_forest = RandomForestClassifier(
            n_estimators=320,
            max_depth=6,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
        )
        gradient_boosting.fit(bundle.rows, bundle.labels)
        random_forest.fit(bundle.rows, bundle.labels)
        feature_importances = [
            (
                float(gradient_boosting.feature_importances_[index])
                + float(random_forest.feature_importances_[index])
            )
            / 2.0
            for index in range(len(FEATURE_ORDER))
        ]
        return {
            "gradient_boosting": gradient_boosting,
            "random_forest": random_forest,
            "feature_importances": feature_importances,
            "metadata": bundle.metadata,
        }

    def _predict_external_model(self, model: dict[str, Any] | None, features: dict[str, float]) -> float:
        if not model:
            return 0.0
        vector = [[features[key] for key in FEATURE_ORDER]]
        gb_probability = float(model["gradient_boosting"].predict_proba(vector)[0][1])
        rf_probability = float(model["random_forest"].predict_proba(vector)[0][1])
        return (gb_probability + rf_probability) / 2.0

    def _fastf1_schedule_context(self, season_year: int | None, race_name: str | None) -> str | None:
        if fastf1 is None or season_year is None or not race_name:
            return None
        try:
            FASTF1_CACHE_PATH.mkdir(parents=True, exist_ok=True)
            fastf1.Cache.enable_cache(str(FASTF1_CACHE_PATH))
            schedule = fastf1.get_event_schedule(int(season_year), include_testing=False)
            normalized_name = race_name.replace("Grand Prix", "").strip().lower()
            candidates = schedule[
                schedule["EventName"].astype(str).str.lower().str.contains(normalized_name, na=False)
            ]
            if candidates.empty:
                return None
            event = candidates.iloc[0]
            return f"{event['EventName']} at {event['Location']}"
        except Exception as error:  # noqa: BLE001
            logger.info("FastF1 schedule context unavailable for %s: %s", race_name, error)
            return None

    def _build_season_stats(
        self,
        completed_weekends: list[dict[str, Any]],
        standings: list[dict[str, Any]],
    ) -> SeasonStats:
        wins: dict[str, int] = defaultdict(int)
        podiums: dict[str, int] = defaultdict(int)
        finish_positions: dict[str, list[int]] = defaultdict(list)
        qualifying_positions: dict[str, list[int]] = defaultdict(list)
        recent_positions: dict[str, list[int]] = defaultdict(list)
        team_lookup = {entry["name"]: entry.get("team", "Unknown Team") for entry in standings}

        for weekend in completed_weekends:
            race_session = _race_session(weekend)
            qualifying_session = _qualifying_session(weekend)

            if qualifying_session:
                for row in qualifying_session.get("entries", []):
                    qualifying_positions[row["driver"]].append(int(row["position"]))
                    team_lookup.setdefault(row["driver"], row.get("team", "Unknown Team"))

            if race_session:
                ordered_entries = sorted(
                    race_session.get("entries", []),
                    key=lambda row: int(row.get("position", 999)),
                )
                for row in ordered_entries:
                    driver = row["driver"]
                    position = int(row["position"])
                    finish_positions[driver].append(position)
                    recent_positions[driver].append(position)
                    team_lookup.setdefault(driver, row.get("team", "Unknown Team"))
                    if position <= 3:
                        podiums[driver] += 1
                    if position == 1:
                        wins[driver] += 1

        return SeasonStats(
            wins=dict(wins),
            podiums=dict(podiums),
            finish_positions={key: value[-3:] for key, value in finish_positions.items()},
            qualifying_positions=dict(qualifying_positions),
            recent_positions={key: value[-3:] for key, value in recent_positions.items()},
            team_lookup=team_lookup,
            completed_races=len(completed_weekends),
        )

    def _build_training_dataset(
        self,
        completed_weekends: list[dict[str, Any]],
        standings: list[dict[str, Any]],
        constructor_lookup: dict[str, dict[str, Any]],
        season_stats: SeasonStats,
    ) -> tuple[list[list[float]], list[int]]:
        rows: list[list[float]] = []
        labels: list[int] = []
        total_drivers = max(len(standings), 1)

        for weekend in completed_weekends:
            track_profile = self._track_profile(weekend.get("name"), weekend.get("name"))
            race_session = _race_session(weekend)
            if not race_session:
                continue
            winners = {entry["driver"] for entry in race_session.get("entries", []) if int(entry["position"]) == 1}

            for entry in standings[: min(len(standings), 12)]:
                driver = entry["name"]
                team = entry.get("team") or season_stats.team_lookup.get(driver, "Unknown Team")
                feature_map = self._feature_map(
                    entry=entry,
                    team=team,
                    driver_profile=self._driver_profile(driver, entry),
                    team_profile=self._team_profile(team, constructor_lookup.get(team)),
                    season_stats=season_stats,
                    track_profile=track_profile,
                    total_drivers=total_drivers,
                    driver_points_ceiling=max(float(item.get("points") or 0.0) for item in standings) if standings else 1.0,
                    constructor_lookup=constructor_lookup,
                )
                rows.append([feature_map[key] for key in FEATURE_ORDER])
                labels.append(1 if driver in winners else 0)

        return rows, labels

    def _fit_logistic_regression(
        self,
        rows: list[list[float]],
        labels: list[int],
    ) -> dict[str, Any]:
        if not rows:
            return {
                "means": [0.0] * len(FEATURE_ORDER),
                "stds": [1.0] * len(FEATURE_ORDER),
                "weights": [0.0] * len(FEATURE_ORDER),
                "bias": 0.0,
            }

        feature_count = len(rows[0])
        means = [_safe_mean([row[index] for row in rows]) for index in range(feature_count)]
        stds = []
        for index in range(feature_count):
            variance = _safe_mean([(row[index] - means[index]) ** 2 for row in rows])
            stds.append(math.sqrt(variance) or 1.0)

        normalized_rows = [
            [(value - means[index]) / stds[index] for index, value in enumerate(row)]
            for row in rows
        ]

        weights = [0.0] * feature_count
        bias = -2.2
        learning_rate = 0.08
        regularization = 0.18
        positive_weight = 8.0

        for _ in range(750):
            gradient_w = [0.0] * feature_count
            gradient_b = 0.0

            for row, label in zip(normalized_rows, labels):
                score = bias + sum(weight * value for weight, value in zip(weights, row))
                prediction = _sigmoid(score)
                sample_weight = positive_weight if label == 1 else 1.0
                error = (prediction - label) * sample_weight
                gradient_b += error
                for index, value in enumerate(row):
                    gradient_w[index] += error * value

            scale = 1.0 / max(len(normalized_rows), 1)
            for index in range(feature_count):
                weights[index] -= learning_rate * ((gradient_w[index] * scale) + (regularization * weights[index]))
            bias -= learning_rate * gradient_b * scale

        return {
            "means": means,
            "stds": stds,
            "weights": weights,
            "bias": bias,
        }

    def _predict_logistic(self, model: dict[str, Any], features: dict[str, float]) -> float:
        score = float(model.get("bias", 0.0))
        for index, key in enumerate(FEATURE_ORDER):
            mean = model["means"][index]
            std = model["stds"][index] or 1.0
            value = (features[key] - mean) / std
            score += model["weights"][index] * value
        return _sigmoid(score)

    def _base_score(self, features: dict[str, float]) -> float:
        weighted_total = 0.0
        weight_sum = 0.0
        for key in FEATURE_ORDER:
            weight = BASE_FEATURE_WEIGHTS[key]
            weighted_total += features[key] * weight
            weight_sum += weight
        return weighted_total / weight_sum if weight_sum else 0.0

    def _feature_map(
        self,
        entry: dict[str, Any],
        team: str,
        driver_profile: dict[str, float | str],
        team_profile: dict[str, float | str],
        season_stats: SeasonStats,
        track_profile: dict[str, Any],
        total_drivers: int,
        driver_points_ceiling: float,
        constructor_lookup: dict[str, dict[str, Any]],
    ) -> dict[str, float]:
        driver = entry["name"]
        points = float(entry.get("points") or 0.0)
        max_points = max(float(item.get("points") or 0.0) for item in constructor_lookup.values()) if constructor_lookup else 1.0

        avg_finish = _safe_mean([float(position) for position in season_stats.finish_positions.get(driver, [])])
        avg_quali = _safe_mean([float(position) for position in season_stats.qualifying_positions.get(driver, [])])
        recent_positions = [float(position) for position in season_stats.recent_positions.get(driver, [])]
        recent_form = 1.0 - ((_safe_mean(recent_positions) - 1.0) / max(total_drivers - 1, 1)) if recent_positions else 0.45
        team_position = float(constructor_lookup.get(team, {}).get("position") or total_drivers)
        team_points = float(constructor_lookup.get(team, {}).get("points") or 0.0)
        street_alignment = (float(driver_profile["street_skill"]) * 0.55) + (float(team_profile["street_bias"]) * 0.45)
        tyre_alignment = (float(driver_profile["tyre_management"]) * 0.6) + (float(team_profile["tyre_usage"]) * 0.4)
        weather_alignment = (float(driver_profile["wet_skill"]) * 0.55) + (track_profile["weather_variability"] * 0.45)

        constructor_strength = (
            (1.0 - ((team_position - 1.0) / max(len(constructor_lookup) - 1, 1))) * 0.45
            + _normalize_count(team_points, max_points) * 0.25
            + float(team_profile["race_pace"]) * 0.15
            + float(team_profile["qualifying_pace"]) * 0.15
        )
        strategy_alignment = (
            (tyre_alignment * 0.4)
            + (float(driver_profile["adaptability"]) * 0.25)
            + (float(team_profile["pit_crew"]) * 0.15)
            + (track_profile["track_evolution"] * 0.2)
        )
        track_fit = (
            (street_alignment * track_profile["street_circuit"])
            + (float(driver_profile["qualifying_skill"]) * (1.0 - track_profile["street_circuit"]) * 0.35)
            + (float(driver_profile["racecraft"]) * track_profile["overtaking"] * 0.25)
            + (float(team_profile["race_pace"]) * track_profile["traction_importance"] * 0.15)
        )

        return {
            "championship_form": _clamp(
                (1.0 - ((float(entry["position"]) - 1.0) / max(total_drivers - 1, 1))) * 0.45
                + _normalize_count(points, max(driver_points_ceiling, 1.0)) * 0.55
            ),
            "constructor_strength": _clamp(constructor_strength),
            "season_wins": _normalize_count(float(season_stats.wins.get(driver, 0)), max(season_stats.completed_races, 1)),
            "podium_rate": _normalize_count(float(season_stats.podiums.get(driver, 0)), max(season_stats.completed_races, 1)),
            "qualifying_sharpness": _clamp(
                1.0 - ((avg_quali - 1.0) / max(total_drivers - 1, 1)) if avg_quali else float(driver_profile["qualifying_skill"])
            ),
            "recent_race_form": _clamp(recent_form if avg_finish else float(driver_profile["racecraft"])),
            "career_wins": _normalize_count(float(driver_profile["career_wins"]), 110.0),
            "junior_provenance": _clamp(
                (_normalize_count(float(driver_profile["junior_wins"]), 30.0) * 0.7)
                + (_normalize_count(float(driver_profile["junior_titles"]), 4.0) * 0.3)
            ),
            "experience_depth": _normalize_count(float(driver_profile["seasons_experience"]), 20.0),
            "track_fit": _clamp(track_fit),
            "tyre_management_fit": _clamp((tyre_alignment * 0.75) + (track_profile["tyre_stress"] * 0.25)),
            "strategy_alignment": _clamp(strategy_alignment),
            "reliability": _clamp((float(team_profile["reliability"]) * 0.7) + (float(driver_profile["adaptability"]) * 0.3)),
            "weather_adaptability": _clamp(weather_alignment),
        }

    def _driver_profile(self, driver: str, entry: dict[str, Any]) -> dict[str, float | str]:
        default_profile: dict[str, float | str] = {
            "career_wins": 0.0,
            "career_poles": 0.0,
            "junior_wins": 14.0,
            "junior_titles": 1.0,
            "seasons_experience": max(1.0, 12.0 - float(entry.get("position", 12))),
            "qualifying_skill": _clamp(0.58 + (0.015 * max(0, 12 - float(entry.get("position", 12))))),
            "racecraft": _clamp(0.6 + (0.015 * max(0, 12 - float(entry.get("position", 12))))),
            "street_skill": 0.66,
            "tyre_management": 0.67,
            "wet_skill": 0.64,
            "adaptability": 0.69,
        }
        default_profile.update(DRIVER_PROFILE_OVERRIDES.get(driver, {}))
        return default_profile

    def _team_profile(
        self,
        team: str,
        constructor_entry: dict[str, Any] | None,
    ) -> dict[str, float | str]:
        profile: dict[str, float | str] = {
            "car_formula_label": "Baseline midfield package",
            "race_pace": 0.58,
            "qualifying_pace": 0.58,
            "pit_crew": 0.72,
            "reliability": 0.72,
            "tyre_usage": 0.68,
            "street_bias": 0.65,
        }
        if constructor_entry:
            field_size = 11.0
            team_strength = 1.0 - ((float(constructor_entry.get("position", field_size)) - 1.0) / max(field_size - 1.0, 1.0))
            profile.update(
                {
                    "race_pace": _clamp(0.5 + (team_strength * 0.4)),
                    "qualifying_pace": _clamp(0.5 + (team_strength * 0.38)),
                    "pit_crew": _clamp(0.68 + (team_strength * 0.18)),
                    "reliability": _clamp(0.66 + (team_strength * 0.2)),
                    "tyre_usage": _clamp(0.64 + (team_strength * 0.18)),
                    "street_bias": _clamp(0.62 + (team_strength * 0.2)),
                }
            )
        profile.update(TEAM_PROFILE_OVERRIDES.get(team, {}))
        return profile

    def _track_profile(self, name: str | None, venue: str | None) -> dict[str, Any]:
        key = _track_key(name, venue)
        profile = dict(DEFAULT_TRACK_PROFILE)
        profile.update(TRACK_PROFILE_OVERRIDES.get(key, {}))
        return profile

    def _simulate_podium_probabilities(
        self,
        contenders: list[dict[str, Any]],
        raw_scores: list[float],
    ) -> dict[str, float]:
        if not contenders:
            return {}

        rng = random.Random(42)
        podium_counts = defaultdict(int)
        simulations = 3000
        for _ in range(simulations):
            remaining = [
                {"driver": contender["driver"], "score": raw_scores[index]}
                for index, contender in enumerate(contenders)
            ]
            for _slot in range(min(3, len(remaining))):
                weights = [math.exp(item["score"]) for item in remaining]
                total = sum(weights) or 1.0
                target = rng.random() * total
                running = 0.0
                chosen_index = 0
                for index, weight in enumerate(weights):
                    running += weight
                    if running >= target:
                        chosen_index = index
                        break
                podium_counts[remaining[chosen_index]["driver"]] += 1
                remaining.pop(chosen_index)

        return {driver: count / simulations for driver, count in podium_counts.items()}

    def _confidence_label(self, win_probability: float, gap: float) -> str:
        if win_probability >= 0.3 and gap >= 0.04:
            return "high"
        if win_probability >= 0.2:
            return "medium"
        return "watch"

    def _overall_confidence(self, completed_races: int, gap: float) -> str:
        if completed_races >= 4 and gap >= 0.04:
            return "medium"
        return "developing"

    def _build_outlook(
        self,
        driver: str,
        team: str,
        features: dict[str, float],
        season_stats: SeasonStats,
        track_profile: dict[str, Any],
    ) -> str:
        wins = season_stats.wins.get(driver, 0)
        if wins >= 2 and features["track_fit"] >= 0.78:
            return f"{driver} arrives as a strong favorite because current form and {track_profile['track_type'].lower()} fit are both elite."
        if features["qualifying_sharpness"] >= 0.8 and track_profile["street_circuit"] >= 0.7:
            return f"{driver} looks dangerous if {team} locks in track position early on this sprint-style weekend."
        if features["strategy_alignment"] >= 0.78:
            return f"{driver} profiles as a strategy threat if the race opens into an undercut or safety-car window."
        return f"{driver} needs a clean qualifying and stable tyre life to convert this profile into a win chance."

    def _evidence_points(
        self,
        driver: str,
        team: str,
        features: dict[str, float],
        season_stats: SeasonStats,
        track_profile: dict[str, Any],
    ) -> list[str]:
        notes = [
            f"{season_stats.wins.get(driver, 0)} season wins and {season_stats.podiums.get(driver, 0)} podiums so far.",
            f"{FEATURE_META['constructor_strength']['label']}: {_display_percent(features['constructor_strength'])} for the current {team} package.",
            f"{FEATURE_META['track_fit']['label']}: {_display_percent(features['track_fit'])} against a {track_profile['track_type'].lower()} profile.",
            f"{FEATURE_META['strategy_alignment']['label']}: {_display_percent(features['strategy_alignment'])} under the projected race plan.",
        ]
        return notes

    def _feature_importance(
        self,
        model: dict[str, Any],
        external_model: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        learned = [abs(weight) for weight in model.get("weights", [])]
        max_learned = max(learned) if learned else 1.0
        max_prior = max(BASE_FEATURE_WEIGHTS.values())
        external = external_model.get("feature_importances", []) if external_model else []
        max_external = max(external) if external else 1.0
        items = []
        for index, key in enumerate(FEATURE_ORDER):
            learned_share = learned[index] / max_learned if max_learned else 0.0
            prior_share = BASE_FEATURE_WEIGHTS[key] / max_prior if max_prior else 0.0
            external_share = external[index] / max_external if external else 0.0
            combined = (
                (prior_share * 0.3) + (learned_share * 0.2) + (external_share * 0.5)
                if external
                else (prior_share * 0.58) + (learned_share * 0.42)
            )
            items.append(
                {
                    "label": FEATURE_META[key]["label"],
                    "value": round(combined, 4),
                    "description": FEATURE_META[key]["description"],
                }
            )
        return sorted(items, key=lambda item: item["value"], reverse=True)

    def _constructor_outlook(self, constructor_standings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        lookup = {entry["name"]: entry for entry in constructor_standings}
        outlook = []
        for entry in constructor_standings[:6]:
            team = entry["name"]
            profile = self._team_profile(team, lookup.get(team))
            outlook.append(
                {
                    "team": team,
                    "car_formula": profile["car_formula_label"],
                    "power_score": round(float(profile["race_pace"]), 4),
                    "qualifying_score": round(float(profile["qualifying_pace"]), 4),
                    "tyre_score": round(float(profile["tyre_usage"]), 4),
                    "reliability": round(float(profile["reliability"]), 4),
                }
            )
        return outlook

    def _scenario_matrix(
        self,
        track_profile: dict[str, Any],
        top_contenders: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        leader = top_contenders[0]["driver"] if top_contenders else "The leader"
        challenger = top_contenders[1]["driver"] if len(top_contenders) > 1 else "the next-best challenger"
        return [
            {
                "title": "Front-row lockout",
                "description": f"If {leader} starts on the first row, the current model expects clean-air advantage to matter more than strategy variance.",
                "effect": "Boosts the favorite and suppresses midfield upset paths.",
            },
            {
                "title": "High-degradation race",
                "description": f"If Miami-style heat pushes tyre wear higher than expected, the model shifts toward drivers with stronger tyre-management scores such as {challenger}.",
                "effect": "Strengthens strategy-first contenders and increases podium volatility.",
            },
            {
                "title": "Safety-car reshuffle",
                "description": f"With {track_profile['overtaking'] * 100:.0f}% overtaking weight, a late neutralization can materially reopen the race even after the first stop cycle.",
                "effect": "Raises upset probability and compresses the top-six outcome spread.",
            },
        ]
