from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from typing import Callable
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from app.config import settings


HtmlFetcher = Callable[[str], str]


def _default_fetch_html(url: str) -> str:
    request = Request(url, headers={"User-Agent": "F1-Intelligence-Hub/0.1"})
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="ignore")


@dataclass(frozen=True)
class ArticleSourceDefinition:
    source_id: str
    url: str
    source_kind: str
    stance: str
    kind: str
    allowed_path_fragments: tuple[str, ...]


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._current_href: str | None = None
        self._capture_text = False
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if not href:
            return
        self._current_href = href
        self._capture_text = True
        self._chunks = []

    def handle_data(self, data: str) -> None:
        if self._capture_text:
            self._chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self._capture_text or not self._current_href:
            return
        title = " ".join(chunk.strip() for chunk in self._chunks if chunk.strip()).strip()
        if title:
            self.links.append((self._current_href, title))
        self._current_href = None
        self._capture_text = False
        self._chunks = []


class ArticleSyncService:
    def __init__(self, fetch_html: HtmlFetcher | None = None) -> None:
        self.fetch_html = fetch_html or _default_fetch_html
        self.sources = (
            ArticleSourceDefinition(
                source_id="source_formula1",
                url="https://www.formula1.com/en/latest",
                source_kind="official",
                stance="official",
                kind="news_article",
                allowed_path_fragments=("/en/latest/article/",),
            ),
            ArticleSourceDefinition(
                source_id="source_fia",
                url="https://www.fia.com/regulation/category/110",
                source_kind="official",
                stance="official",
                kind="regulation_update",
                allowed_path_fragments=("/regulation/", "/document/"),
            ),
            ArticleSourceDefinition(
                source_id="source_mercedes",
                url="https://www.mercedesamgf1.com/news",
                source_kind="team",
                stance="official",
                kind="team_update",
                allowed_path_fragments=("/news/",),
            ),
            ArticleSourceDefinition(
                source_id="source_ferrari",
                url="https://www.ferrari.com/en-EN/formula1/articles",
                source_kind="team",
                stance="official",
                kind="team_update",
                allowed_path_fragments=("/articles/",),
            ),
            ArticleSourceDefinition(
                source_id="source_mclaren",
                url="https://www.mclaren.com/racing/formula-1/latest-news/",
                source_kind="team",
                stance="official",
                kind="team_update",
                allowed_path_fragments=("/racing/formula-1/",),
            ),
            ArticleSourceDefinition(
                source_id="source_the_race",
                url="https://www.the-race.com/formula-1/",
                source_kind="media",
                stance="analysis",
                kind="analysis_article",
                allowed_path_fragments=("/formula-1/",),
            ),
        )

    def sync_articles(self, current_weekend_id: str) -> list[dict[str, str]]:
        synced: list[dict[str, str]] = []
        seen_urls: set[str] = set()
        source_counts: dict[str, int] = {}
        publish_time = datetime.now(ZoneInfo(settings.local_timezone)).isoformat()

        for source in self.sources:
            try:
                html = self.fetch_html(source.url)
            except Exception:  # noqa: BLE001
                continue
            extractor = LinkExtractor()
            extractor.feed(html)
            for href, title in extractor.links:
                absolute_url = urljoin(source.url, href)
                if absolute_url in seen_urls:
                    continue
                if not any(fragment in absolute_url for fragment in source.allowed_path_fragments):
                    continue
                if len(title) < 18:
                    continue
                if source_counts.get(source.source_id, 0) >= 6:
                    break
                seen_urls.add(absolute_url)
                synced.append(
                    {
                        "id": f"article_{source.source_id}_{len(synced)+1}",
                        "source_id": source.source_id,
                        "weekend_id": current_weekend_id,
                        "title": title,
                        "url": absolute_url,
                        "kind": source.kind,
                        "publish_time": publish_time,
                        "race_stage": "between_races",
                        "stance": source.stance,
                        "cluster_hint": None,
                        "entity_ids": [],
                        "content": title,
                    }
                )
                source_counts[source.source_id] = source_counts.get(source.source_id, 0) + 1
        return synced
