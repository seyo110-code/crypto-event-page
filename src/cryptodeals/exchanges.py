from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class ExchangeConfig:
    name: str
    region: str
    event_hub_url: str
    announcement_url: str
    crawl_difficulty: str
    rendering: str
    priority: int
    cadence: str


def load_exchange_configs(path: str | Path) -> list[ExchangeConfig]:
    config_path = Path(path)
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    rows = raw.get("exchanges", [])

    configs: list[ExchangeConfig] = []
    for row in rows:
        configs.append(
            ExchangeConfig(
                name=row["name"],
                region=row["region"],
                event_hub_url=row["event_hub_url"],
                announcement_url=row["announcement_url"],
                crawl_difficulty=row["crawl_difficulty"],
                rendering=row["rendering"],
                priority=int(row["priority"]),
                cadence=row["cadence"],
            )
        )
    return sorted(configs, key=lambda c: (c.priority, c.name.lower()))
