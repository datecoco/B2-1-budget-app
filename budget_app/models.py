"""프로그램에서 사용할 데이터 모양을 정의한다."""

from dataclasses import dataclass, field


@dataclass
class Transaction:
    """수입 또는 지출 거래 한 건을 표현한다."""

    # 거래를 구별하는 고유 번호
    id: str

    # income(수입) 또는 expense(지출)
    type: str

    # 거래 날짜. 예: 2026-09-18
    date: str

    # 금액. 정수로 저장한다.
    amount: int

    # 예: food, transport, salary
    category: str

    # 메모는 없어도 되므로 기본값을 빈 문자열로 둔다.
    memo: str = ""

    # 태그도 없어도 된다.
    # field(default_factory=list)는 거래마다 새로운 빈 목록을 만들게 한다.
    tags: list[str] = field(default_factory=list)