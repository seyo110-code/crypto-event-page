from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import CrawlerNormalizedEvent
from .pipeline import notion_upsert_key


@dataclass
class SyncResult:
    created: int = 0
    updated: int = 0
    skipped: int = 0


class NotionSyncService:
    """Notion API 업서트 인터페이스.

    실제 Notion API 토큰/DB ID 연결 전 단계에서 로직 구조를 고정하기 위한 클래스다.
    """

    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run

    def upsert_events(self, events: list[CrawlerNormalizedEvent]) -> SyncResult:
        result = SyncResult()
        seen: set[str] = set()

        for event in events:
            key = notion_upsert_key(event).as_string()
            if key in seen:
                result.skipped += 1
                continue
            seen.add(key)

            if self.dry_run:
                result.created += 1
            else:
                # TODO: Notion API 호출로 기존 페이지 조회 후 create/update 분기
                result.created += 1

        return result

    @staticmethod
    def build_notion_payload(event: CrawlerNormalizedEvent) -> dict[str, Any]:
        return {
            "Event ID": f"{event.exchange.upper()}-{event.published_at.strftime('%Y%m%d')}-01",
            "거래소명": event.exchange,
            "이벤트명": event.title,
            "참여 링크": str(event.url),
            "카테고리": event.category_raw,
            "지역 구분": event.region.value,
            "혜택 요약": event.reward_raw or "",
            "참여 조건 요약": event.requirements_raw or "",
            "원문 공지일": event.published_at.isoformat(),
            "상태(자동)": event.status_guess.value,
        }
