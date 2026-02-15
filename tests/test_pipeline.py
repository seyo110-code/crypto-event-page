import unittest
from datetime import UTC, datetime, timedelta

from cryptodeals.models import CrawlerNormalizedEvent, Region, StatusGuess
from cryptodeals.pipeline import infer_status, notion_upsert_key


class PipelineTests(unittest.TestCase):
    def test_infer_status_upcoming(self) -> None:
        now = datetime(2026, 2, 15, tzinfo=UTC)
        start = now + timedelta(days=1)
        end = now + timedelta(days=3)
        self.assertEqual(infer_status(start, end, now=now), StatusGuess.UPCOMING)

    def test_infer_status_live(self) -> None:
        now = datetime(2026, 2, 15, tzinfo=UTC)
        start = now - timedelta(days=1)
        end = now + timedelta(days=1)
        self.assertEqual(infer_status(start, end, now=now), StatusGuess.LIVE)

    def test_infer_status_ended(self) -> None:
        now = datetime(2026, 2, 15, tzinfo=UTC)
        end = now - timedelta(minutes=1)
        self.assertEqual(infer_status(None, end, now=now), StatusGuess.ENDED)

    def test_notion_upsert_key(self) -> None:
        now = datetime(2026, 2, 15, tzinfo=UTC)
        event = CrawlerNormalizedEvent(
            exchange="Binance",
            title="Alpha Airdrop",
            url="https://www.binance.com/test",
            published_at=now,
            region=Region.GLOBAL,
        )
        self.assertEqual(
            notion_upsert_key(event).as_string(),
            "Binance|Alpha Airdrop|2026-02-15",
        )


if __name__ == "__main__":
    unittest.main()
