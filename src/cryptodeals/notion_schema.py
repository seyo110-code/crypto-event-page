from __future__ import annotations

EVENTS_PROPERTIES = {
    "Event ID": "title",
    "거래소명": "select",
    "이벤트명": "rich_text",
    "카테고리": "multi_select",
    "시작일": "date",
    "종료일": "date",
    "상태(수동)": "status",
    "상태(자동)": "formula",
    "참여 링크": "url",
    "혜택 요약": "rich_text",
    "난이도": "select",
    "예상 보상 규모": "select",
    "지역 구분": "select",
    "참여 조건 요약": "rich_text",
    "원문 공지일": "date",
    "소스 신뢰도": "select",
    "담당자": "people",
    "마지막 확인일": "date",
    "중복키": "formula",
    "메모": "rich_text",
}

EXCHANGES_PROPERTIES = {
    "거래소명": "title",
    "지역": "select",
    "이벤트 허브 URL": "url",
    "공지 URL": "url",
    "크롤링 난이도": "select",
    "렌더링 방식": "select",
    "수집 우선순위": "number",
    "점검 주기": "select",
    "비고": "rich_text",
}
