from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


VALID_LABELS = {"official_update", "race_result", "analysis", "prediction"}
VALID_EDITORIAL_STATUSES = {"draft", "review_required", "approved"}


def ensure_valid_label(label: str) -> str:
    if label not in VALID_LABELS:
        raise ValueError(f"Unsupported label: {label}")
    return label


def ensure_valid_editorial_status(status: str) -> str:
    if status not in VALID_EDITORIAL_STATUSES:
        raise ValueError(f"Unsupported editorial status: {status}")
    return status


def apply_summary_patch(summary: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    updated = deepcopy(summary)
    if "label" in patch and patch["label"] is not None:
        updated["label"] = ensure_valid_label(patch["label"])
    if "editorial_status" in patch and patch["editorial_status"] is not None:
        updated["editorial_status"] = ensure_valid_editorial_status(patch["editorial_status"])
    if "title" in patch and patch["title"]:
        updated["title"] = patch["title"].strip()
    if "body" in patch and patch["body"]:
        updated["body"] = patch["body"].strip()
    updated["updated_at"] = datetime.now(timezone.utc).isoformat()
    return updated

