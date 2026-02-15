#!/usr/bin/env python3
from __future__ import annotations

import json

from cryptodeals.notion_schema import EVENTS_PROPERTIES, EXCHANGES_PROPERTIES


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "events": EVENTS_PROPERTIES,
                "exchanges": EXCHANGES_PROPERTIES,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
