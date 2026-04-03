from __future__ import annotations

import re
from typing import Any


def normalize_title(title: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", title.lower())
    return " ".join(cleaned.split())


def title_similarity(left: str, right: str) -> float:
    left_tokens = set(normalize_title(left).split())
    right_tokens = set(normalize_title(right).split())
    if not left_tokens or not right_tokens:
        return 0.0
    overlap = left_tokens & right_tokens
    union = left_tokens | right_tokens
    return len(overlap) / len(union)


def deduplicate_documents(
    documents: list[dict[str, Any]], similarity_threshold: float = 0.5
) -> list[dict[str, Any]]:
    unique_documents: list[dict[str, Any]] = []
    for candidate in documents:
        is_duplicate = False
        for existing in unique_documents:
            same_url = candidate["url"] == existing["url"]
            same_cluster_hint = candidate.get("cluster_hint") == existing.get("cluster_hint")
            similar_title = (
                title_similarity(candidate["title"], existing["title"]) >= similarity_threshold
            )
            if same_url or (same_cluster_hint and similar_title):
                is_duplicate = True
                break
        if not is_duplicate:
            unique_documents.append(candidate)
    return unique_documents


def cluster_documents_by_hint(
    documents: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for document in documents:
        hint = document.get("cluster_hint") or f"uncategorized:{document['id']}"
        grouped.setdefault(hint, []).append(document)
    return grouped
