# Notion Database Schema

## 1) Events DB

| Property | Type | Required | Notes |
|---|---|---:|---|
| Event ID | Title | Y | `EXCHANGE-YYYYMMDD-SEQ` |
| 거래소명 | Select | Y | Upbit/Bithumb/Coinone/Korbit/GOPAX/Binance/Bybit/OKX/Gate.io/MEXC/Bitget |
| 이벤트명 | Rich text | Y | 공지 제목 |
| 카테고리 | Multi-select | Y | Airdrop, Sign-up Bonus, Deposit/Trading Event, Fee Discount/Cashback, Trading Competition, Staking/Launchpool, Reward Program, Other |
| 시작일 | Date | Y | KST 기준 |
| 종료일 | Date | N | 미공개 가능 |
| 상태(수동) | Status | Y | 예정 / 진행중 / 종료 |
| 상태(자동) | Formula | Y | 날짜 기준 자동 |
| 참여 링크 | URL | Y | 공식 원문 링크 |
| 혜택 요약 | Rich text | Y | 핵심 요약 |
| 난이도 | Select | Y | 하 / 중 / 상 |
| 예상 보상 규모 | Select | Y | 소액/중간/대형/미정 |
| 지역 구분 | Select | Y | 국내 / 해외 |
| 참여 조건 요약 | Rich text | Y | KYC/입금/거래량 등 |
| 원문 공지일 | Date | Y | 게시 시각 |
| 소스 신뢰도 | Select | Y | 공식공지 / 공식블로그 / 제3자 |
| 담당자 | Person | Y | 오너 |
| 마지막 확인일 | Date | Y | 마지막 검증 시각 |
| 중복키 | Formula | Y | 거래소명+이벤트명+시작일 |
| 메모 | Rich text | N | 특이사항 |

### 상태(자동) Formula 예시

```text
if(
  empty(prop("시작일")) and empty(prop("종료일")),
  "상시",
  if(
    not empty(prop("종료일")) and prop("종료일") < now(),
    "종료",
    if(prop("시작일") > now(), "예정", "진행중")
  )
)
```

## 2) Exchanges DB

| Property | Type | Required | Notes |
|---|---|---:|---|
| 거래소명 | Title | Y | 고유명 |
| 지역 | Select | Y | 국내 / 해외 |
| 이벤트 허브 URL | URL | Y | 이벤트/캠페인 허브 |
| 공지 URL | URL | Y | 공지판 |
| 크롤링 난이도 | Select | Y | 하/중/상 |
| 렌더링 방식 | Select | Y | 정적/동적/혼합 |
| 수집 우선순위 | Number | Y | 1~3 |
| 점검 주기 | Select | Y | 1일2회/1일1회/주3회 |
| 비고 | Rich text | N | 앱 전용 여부 등 |

## 3) 추천 Views

- 진행중 전체 (상태 자동=진행중, 종료일 오름차순)
- 마감 임박 7일
- 오늘 종료
- 예정 이벤트
- 거래소별 보드
- 카테고리별 보드
- 고보상 저난이도
- 검수 필요(마지막 확인일 48시간 초과)
