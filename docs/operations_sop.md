# Operations SOP

## Daily routine (KST)

- 09:30: 국내 5개 + 해외 우선순위 1 거래소 확인
- 21:30: 해외 전체 + 국내 재확인
- 긴급 공지: 발견 즉시 등록

## Source URLs

- Upbit: `https://event.upbit.com/`, `https://support.upbit.com/`
- Bithumb: `https://support.bithumb.com/`, `https://www.bithumb.com/customer_support/info`
- Coinone: `https://coinone.co.kr/info/notice/`
- Korbit: `https://www.korbit.co.kr/events/`
- GOPAX: `https://academy.gopax.co.kr/`
- Binance: `https://www.binance.com/en/support/announcement`
- Bybit: `https://announcements.bybit.com/en/`
- OKX: `https://www.okx.com/campaigns/`
- Gate.io: `https://www.gate.com/announcements`
- MEXC: `https://www.mexc.com/support`
- Bitget: `https://www.bitget.com/support`

## Event registration checklist

1. 도메인과 원문 URL 검증
2. 시작일/종료일/원문 공지일 입력
3. 참여 조건(KYC, 입금, 거래량) 정리
4. 보상 지급 방식(선착순/추첨/비례) 입력
5. 상태(수동)와 상태(자동) 일치 확인
6. 중복키 검색 후 신규/업데이트 판단
7. 마지막 확인일/담당자 입력
8. 등록 24시간 이내 1회 재검수

## Expiry handling

- 00:10 자동 점검: 종료일 지난 이벤트 `종료` 처리
- 종료 후 7일: 종료 보관 뷰로 이동
- 종료 후 30일: `archived=true`로 아카이브

## Data quality rules

- 공식 공지 우선, 제3자 출처는 소스 신뢰도 `제3자`
- 투자 권유 표현 금지(확정 수익, 무조건 등)
- 위험 신호(외부 지갑 연결 강요/URL 불일치) 발견 시 `보류`
