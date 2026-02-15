from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import CrawlerNormalizedEvent


class BaseCrawler(ABC):
    exchange_name: str

    @abstractmethod
    def fetch(self) -> list[CrawlerNormalizedEvent]:
        """거래소 공지 페이지에서 이벤트를 수집해 정규화 형태로 반환."""
        raise NotImplementedError
