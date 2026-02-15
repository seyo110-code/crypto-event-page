# CryptoDeals

국내외 가상화폐 거래소 이벤트/프로모션 통합 정리 서비스입니다.

초기 목표는 Notion 기반 수동 운영이며, 이후 크롤링/Notion API/웹·봇 확장으로 진행합니다.

## What is included

- Notion DB 스키마 정의 (`docs/notion_schema.md`)
- 운영 SOP (`docs/operations_sop.md`)
- 거래소 메타데이터 (`configs/exchanges.yaml`)
- 정규화 이벤트 타입/상태 계산/업서트 키 생성 코드 (`src/cryptodeals/`)
- 크롤러 인터페이스와 예시 크롤러 뼈대 (`src/cryptodeals/crawlers/`)
- 기본 테스트 (`tests/`)

## Quick start

```bash
cd /home/seyo110/crypto-event-page
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m cryptodeals.cli list-exchanges
python -m cryptodeals.cli print-notion-schema
```

## Commands

```bash
python -m cryptodeals.cli list-exchanges
python -m cryptodeals.cli print-notion-schema
python -m cryptodeals.cli sample-event
```

## Project structure

```text
configs/                     # 거래소 수집 URL 및 우선순위
src/cryptodeals/models.py    # 표준 이벤트 타입
src/cryptodeals/pipeline.py  # 상태 추론/업서트키/변경점 계산
src/cryptodeals/notion_schema.py
src/cryptodeals/crawlers/    # 거래소별 크롤러 뼈대
scripts/                     # 운영 유틸
docs/                        # Notion/운영 문서
tests/                       # 핵심 로직 테스트
```

## Next implementation targets

1. 거래소별 크롤러 실제 파서 완성 (Binance/Bybit 우선)
2. Notion API 업서트 구현 (`notion_sync.py` 확장)
3. 스케줄링 (cron/GitHub Actions) 및 장애 알림
