# Supertrend 트레이딩 봇 (Freqtrade)

슈퍼트렌드 기반 선물 봇을 Freqtrade 전략으로 구성했습니다.
개선 요소를 단계별로 켠 **세 가지 변형**을 한 번에 백테스트해서 효과를 비교하는 것이 목적입니다.

| 전략 | 진입 | 청산 | 리스크 관리 |
|---|---|---|---|
| `SupertrendBasic` | 슈퍼트렌드 전환 | 반대 전환 | 고정 비율, 비상 손절 -15% |
| `SupertrendFiltered` | + ADX > 20, + 4h 슈퍼트렌드 방향 일치 | 반대 전환 | 동일 |
| `SupertrendFull` | Filtered와 동일 | + 슈퍼트렌드 선 추적 손절, 1R에서 50% 익절 후 본전 손절 | + 1회 손실 1% 기준 포지션 크기, 연속 손절/낙폭 보호 |

공통 규칙
- 모든 판단은 **마감된 봉** 기준 (Freqtrade 기본 동작). 실시간 봉으로 판단해 신호가 생겼다 사라지는 문제가 없습니다.
- 추세 구간당 진입은 **최대 1회**, 전환 후 `entry_window`(기본 6봉) 안에서만 진입합니다.
  필터 때문에 전환 봉에서 못 들어갔어도 그 안에 필터가 풀리면 진입하고, 추세 끝물 추격 진입은 막습니다.
- 롱/숏 양방향, 레버리지 2배, 격리 마진.

설정값은 `user_data/strategies/supertrend_strategy.py`의 `SupertrendBasic` 클래스 상단에 모여 있습니다
(`st_period`, `st_multiplier`, `adx_threshold`, `partial_tp_r`, `risk_per_trade`, `leverage_value` 등).

## 설치

```bash
cd trading-bot
python3 -m venv .venv && source .venv/bin/activate
pip install freqtrade        # 또는 Docker: https://www.freqtrade.io/en/stable/docker_quickstart/
cp config.example.json config.json
```

> `config.json`은 API 키가 들어가므로 git에 올라가지 않습니다(`.gitignore`).

## 백테스트

```bash
# 1) 데이터 다운로드 (1h + 상위 타임프레임 4h, 선물)
freqtrade download-data -c config.json --timeframes 1h 4h --timerange 20230101-

# 2) 세 전략 비교
freqtrade backtesting -c config.json \
  --strategy-list SupertrendBasic SupertrendFiltered SupertrendFull \
  --timerange 20230101- --breakdown month

# 3) 결과 차트 (선택)
freqtrade plot-dataframe -c config.json -s SupertrendFull --indicators1 st_line
```

비교할 때 볼 지표
- **Drawdown(최대 낙폭)과 수익의 비율**: 총 수익보다 중요합니다.
- **Trades 수와 Win%**: 필터가 휩쏘(횡보장 잦은 손절)를 얼마나 줄였는지 확인합니다.
- **월별 breakdown**: 특정 몇 달에만 수익이 몰려 있는지 확인합니다.
- **기간 분리 검증**: 예를 들어 2023~2024로 파라미터를 고르고, 2025 이후 구간에서 그대로 성과가 나오는지 봅니다(과최적화 확인).

## 모의매매 → 실거래

1. `dry_run: true` 상태로 최소 2~4주 돌리면서 백테스트와 체결이 비슷한지 확인합니다.
2. 텔레그램 알림을 켭니다(`telegram.token`, `chat_id`). `/status`, `/stopentry`, `/forceexit all` 등으로 원격 제어할 수 있습니다.
3. 실거래로 전환할 때 확인할 것
   - `exchange.key`/`secret`: **출금 권한 없는** API 키, IP 화이트리스트
   - `stoploss_on_exchange: true`: 봇이 죽어도 거래소에 손절 주문이 남아 있습니다
   - 바이낸스 선물은 **단방향 포지션 모드**(One-way)여야 합니다
   - 처음에는 `dry_run_wallet`과 비슷한 소액으로 시작합니다

## 운영 (상시 실행)

가장 간단한 방법은 VPS + Docker Compose입니다.

```bash
freqtrade trade -c config.json --strategy SupertrendFull
```

- 재시작해도 열린 포지션은 `tradesv3.sqlite`에서 복구되고, 거래소와 대조됩니다.
- `api_server`를 켜면 FreqUI 웹 대시보드를 쓸 수 있습니다(외부 노출 시 비밀번호와 키를 반드시 변경하세요).

## 테스트

```bash
pip install pytest
pytest tests
```
