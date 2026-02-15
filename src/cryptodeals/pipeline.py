from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from .models import CrawlerNormalizedEvent, StatusGuess


@dataclass(frozen=True)
class UpsertKey:
    exchange: str
    title: str
    published_date: str

    def as_string(self) -> str:
        return f"{self.exchange}|{self.title}|{self.published_date}"


def infer_status(start_at: datetime | None, end_at: datetime | None, now: datetime | None = None) -> StatusGuess:
    now = now or datetime.now(UTC)

    if start_at is None and end_at is None:
        return StatusGuess.UNKNOWN
    if end_at is not None and end_at < now:
        return StatusGuess.ENDED
    if start_at is not None and start_at > now:
        return StatusGuess.UPCOMING
    return StatusGuess.LIVE


def notion_upsert_key(event: CrawlerNormalizedEvent) -> UpsertKey:
    return UpsertKey(
        exchange=event.exchange.strip(),
        title=event.title.strip(),
        published_date=event.published_at.date().isoformat(),
    )


def normalize_event_status(event: CrawlerNormalizedEvent, now: datetime | None = None) -> CrawlerNormalizedEvent:
    event.status_guess = infer_status(event.start_at, event.end_at, now=now)
    return event


def diff_event_fields(before: dict[str, Any], after: dict[str, Any]) -> dict[str, tuple[Any, Any]]:
    changed: dict[str, tuple[Any, Any]] = {}
    keys = set(before.keys()) | set(after.keys())
    for key in keys:
        if before.get(key) != after.get(key):
            changed[key] = (before.get(key), after.get(key))
    return changed
