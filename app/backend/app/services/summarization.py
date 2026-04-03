from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


LABEL_INTROS = {
    "official_update": "Officially, the state changed here:",
    "race_result": "The verified result signal is straightforward:",
    "analysis": "The source-backed interpretation is:",
    "prediction": "This remains forward-looking rather than verified:",
}


def generate_cluster_summary(
    cluster: dict[str, Any],
    documents: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    entities: list[dict[str, Any]],
) -> dict[str, Any]:
    source_names = ", ".join(source["name"] for source in sources[:3])
    entity_names = ", ".join(entity["name"] for entity in entities[:4])
    intro = LABEL_INTROS.get(cluster["label"], "Signal update:")
    body = (
        f"{intro} {cluster['title']} "
        f"This cluster draws on {len(documents)} source document(s) from {source_names}. "
        f"Key entities in scope: {entity_names}."
    )
    return {
        "title": cluster["title"],
        "body": body,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

