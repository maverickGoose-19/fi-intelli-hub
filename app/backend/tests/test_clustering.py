from __future__ import annotations

import unittest

from app.services.clustering import deduplicate_documents, normalize_title, title_similarity


class ClusteringTests(unittest.TestCase):
    def test_normalize_title_removes_punctuation(self) -> None:
        self.assertEqual(
            normalize_title("Grid penalty applied to car one!"),
            "grid penalty applied to car one",
        )

    def test_title_similarity_rewards_overlapping_titles(self) -> None:
        similarity = title_similarity(
            "McLaren leads long-run averages at Suzuka",
            "Suzuka long run averages show McLaren in front",
        )
        self.assertGreaterEqual(similarity, 0.5)

    def test_deduplicate_documents_keeps_unique_items(self) -> None:
        documents = [
            {
                "id": "1",
                "title": "McLaren leads long-run averages at Suzuka",
                "url": "https://example.com/a",
                "cluster_hint": "pace",
            },
            {
                "id": "2",
                "title": "Suzuka long run averages show McLaren in front",
                "url": "https://example.com/b",
                "cluster_hint": "pace",
            },
            {
                "id": "3",
                "title": "FIA confirms grid penalty before qualifying",
                "url": "https://example.com/c",
                "cluster_hint": "penalty",
            },
        ]
        deduplicated = deduplicate_documents(documents)
        self.assertEqual(len(deduplicated), 2)


if __name__ == "__main__":
    unittest.main()
