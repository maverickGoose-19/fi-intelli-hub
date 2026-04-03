from __future__ import annotations

import unittest

from app.services.editorial import apply_summary_patch


class EditorialPolicyTests(unittest.TestCase):
    def test_apply_summary_patch_updates_allowed_fields(self) -> None:
        summary = {
            "id": "summary_1",
            "label": "analysis",
            "title": "Old title",
            "body": "Old body",
            "editorial_status": "draft",
            "updated_at": "2026-04-01T00:00:00Z",
        }
        updated = apply_summary_patch(
            summary,
            {
                "label": "prediction",
                "editorial_status": "review_required",
                "body": "Updated body",
            },
        )
        self.assertEqual(updated["label"], "prediction")
        self.assertEqual(updated["editorial_status"], "review_required")
        self.assertEqual(updated["body"], "Updated body")
        self.assertNotEqual(updated["updated_at"], summary["updated_at"])

    def test_apply_summary_patch_rejects_invalid_labels(self) -> None:
        summary = {
            "id": "summary_1",
            "label": "analysis",
            "title": "Old title",
            "body": "Old body",
            "editorial_status": "draft",
            "updated_at": "2026-04-01T00:00:00Z",
        }
        with self.assertRaises(ValueError):
            apply_summary_patch(summary, {"label": "mixed_fact_prediction"})


if __name__ == "__main__":
    unittest.main()

