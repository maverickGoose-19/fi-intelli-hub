from __future__ import annotations

import unittest

from app.repository import SeedRepository


class PredictionAnalyticsTests(unittest.TestCase):
    def test_prediction_payload_contains_model_and_contenders(self) -> None:
        repository = SeedRepository()

        payload = repository.get_prediction_analytics()

        self.assertEqual(payload["race"]["name"], "Miami Grand Prix")
        self.assertIn("model", payload)
        self.assertIn("track", payload)
        self.assertGreaterEqual(len(payload["contenders"]), 5)
        self.assertEqual(payload["contenders"][0]["rank"], 1)
        self.assertGreater(payload["contenders"][0]["win_probability"], payload["contenders"][1]["win_probability"])
        self.assertGreater(len(payload["feature_importance"]), 3)
        self.assertGreater(len(payload["source_stack"]), 5)

    def test_prediction_probabilities_are_normalized_and_bounded(self) -> None:
        repository = SeedRepository()

        payload = repository.get_prediction_analytics()
        total_win_probability = sum(item["win_probability"] for item in payload["contenders"])

        self.assertAlmostEqual(total_win_probability, 1.0, places=3)
        for contender in payload["contenders"]:
            self.assertGreaterEqual(contender["win_probability"], 0.0)
            self.assertLessEqual(contender["win_probability"], 1.0)
            self.assertGreaterEqual(contender["podium_probability"], contender["win_probability"])
            self.assertLessEqual(contender["podium_probability"], 1.0)


if __name__ == "__main__":
    unittest.main()
