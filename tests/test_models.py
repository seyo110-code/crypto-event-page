import unittest
from datetime import UTC, datetime

from cryptodeals.models import CrawlerNormalizedEvent, Region


class ModelTests(unittest.TestCase):
    def test_stable_hash_is_deterministic(self) -> None:
        now = datetime(2026, 2, 15, tzinfo=UTC)
        event = CrawlerNormalizedEvent(
            exchange="Bybit",
            title="Launchpool X",
            url="https://announcements.bybit.com/en/test",
            published_at=now,
            region=Region.GLOBAL,
        )

        h1 = event.stable_hash()
        h2 = event.stable_hash()
        self.assertEqual(h1, h2)

    def test_with_hash_populates_hash(self) -> None:
        now = datetime(2026, 2, 15, tzinfo=UTC)
        event = CrawlerNormalizedEvent(
            exchange="Bybit",
            title="Launchpool X",
            url="https://announcements.bybit.com/en/test",
            published_at=now,
            region=Region.GLOBAL,
        )

        self.assertIsNone(event.hash)
        event.with_hash()
        self.assertIsNotNone(event.hash)


if __name__ == "__main__":
    unittest.main()
