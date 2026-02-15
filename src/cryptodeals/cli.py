from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .exchanges import load_exchange_configs
from .models import CrawlerNormalizedEvent, Region
from .notion_schema import EVENTS_PROPERTIES, EXCHANGES_PROPERTIES
from .pipeline import normalize_event_status, notion_upsert_key


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cryptodeals")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-exchanges", help="Configured exchanges 출력")
    sub.add_parser("print-notion-schema", help="Notion 스키마 JSON 출력")
    sub.add_parser("sample-event", help="샘플 이벤트 생성")

    return parser


def cmd_list_exchanges() -> int:
    cfg_path = Path(__file__).resolve().parents[2] / "configs" / "exchanges.yaml"
    exchanges = load_exchange_configs(cfg_path)
    for ex in exchanges:
        print(f"[{ex.priority}] {ex.name} ({ex.region}) - {ex.event_hub_url}")
    return 0


def cmd_print_notion_schema() -> int:
    payload = {
        "events": EVENTS_PROPERTIES,
        "exchanges": EXCHANGES_PROPERTIES,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_sample_event() -> int:
    now = datetime.now(UTC)
    event = CrawlerNormalizedEvent(
        exchange="Binance",
        title="Sample Launchpool Event",
        url="https://www.binance.com/en/support/announcement/sample",
        published_at=now,
        start_at=now,
        end_at=now + timedelta(days=7),
        category_raw="Staking/Launchpool",
        region=Region.GLOBAL,
        reward_raw="총 100,000 USDT",
        requirements_raw="KYC + 스테이킹",
    ).with_hash()

    event = normalize_event_status(event)
    print(json.dumps(event.model_dump(mode="json"), ensure_ascii=False, indent=2))
    print(f"upsert_key={notion_upsert_key(event).as_string()}")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list-exchanges":
        return cmd_list_exchanges()
    if args.command == "print-notion-schema":
        return cmd_print_notion_schema()
    if args.command == "sample-event":
        return cmd_sample_event()

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
