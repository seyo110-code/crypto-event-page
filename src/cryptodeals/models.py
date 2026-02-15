from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from hashlib import sha256
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class Region(str, Enum):
    KR = "KR"
    GLOBAL = "GLOBAL"


class StatusGuess(str, Enum):
    UPCOMING = "upcoming"
    LIVE = "live"
    ENDED = "ended"
    UNKNOWN = "unknown"


class SourceType(str, Enum):
    OFFICIAL_ANNOUNCEMENT = "official_announcement"
    OFFICIAL_BLOG = "official_blog"
    THIRD_PARTY = "third_party"


class CrawlerNormalizedEvent(BaseModel):
    exchange: str = Field(min_length=2)
    title: str = Field(min_length=2)
    url: HttpUrl
    published_at: datetime
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    category_raw: str = "Other"
    region: Region
    reward_raw: Optional[str] = None
    requirements_raw: Optional[str] = None
    status_guess: StatusGuess = StatusGuess.UNKNOWN
    source_type: SourceType = SourceType.OFFICIAL_ANNOUNCEMENT
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    hash: Optional[str] = None

    def stable_hash(self) -> str:
        payload = "|".join(
            [
                self.exchange.strip().lower(),
                self.title.strip().lower(),
                str(self.url),
                self.published_at.date().isoformat(),
            ]
        )
        return sha256(payload.encode("utf-8")).hexdigest()

    def with_hash(self) -> "CrawlerNormalizedEvent":
        self.hash = self.stable_hash()
        return self
