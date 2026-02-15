from __future__ import annotations

from datetime import UTC, datetime

import httpx
from bs4 import BeautifulSoup

from ..models import CrawlerNormalizedEvent, Region, SourceType
from ..pipeline import normalize_event_status
from .base import BaseCrawler


class BinanceCrawler(BaseCrawler):
    exchange_name = "Binance"
    url = "https://www.binance.com/en/support/announcement"

    def fetch(self) -> list[CrawlerNormalizedEvent]:
        response = httpx.get(self.url, timeout=20.0)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.select("a[href]")

        events: list[CrawlerNormalizedEvent] = []
        now = datetime.now(UTC)

        for link in links[:30]:
            title = (link.get_text() or "").strip()
            href = link.get("href")
            if not title or not href:
                continue

            lower = title.lower()
            if not any(k in lower for k in ("airdrop", "campaign", "launchpool", "competition", "bonus")):
                continue

            if href.startswith("/"):
                href = f"https://www.binance.com{href}"

            event = CrawlerNormalizedEvent(
                exchange=self.exchange_name,
                title=title,
                url=href,
                published_at=now,
                start_at=now,
                end_at=None,
                category_raw="Other",
                region=Region.GLOBAL,
                reward_raw=None,
                requirements_raw=None,
                source_type=SourceType.OFFICIAL_ANNOUNCEMENT,
            ).with_hash()

            events.append(normalize_event_status(event, now=now))

        return events
