"""프로그램에서 사용할 데이터 모양을 정의한다."""

from dataclasses import dataclass, field
from datetime import date
import re


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
    # 거래마다 새로운 빈 목록을 만들기 위해 default_factory를 쓴다.
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """거래 객체가 만들어진 직후, 입력값이 올바른지 검사한다."""

        # type은 수입 또는 지출 둘 중 하나여야 한다.
        if self.type not in {"income", "expense"}:
            raise ValueError("type은 income 또는 expense여야 합니다.")

        # YYYY-MM-DD 모양인지 먼저 확인한다.
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", self.date):
            raise ValueError("날짜는 YYYY-MM-DD 형식이어야 합니다.")

        # 실제 존재하는 날짜인지 확인한다.
        # 예: 2026-02-30은 모양은 맞지만 존재하지 않는 날짜다.
        try:
            date.fromisoformat(self.date)
        except ValueError as error:
            raise ValueError("존재하지 않는 날짜입니다.") from error

        # 금액은 반드시 0보다 커야 한다.
        if self.amount <= 0:
            raise ValueError("금액은 0보다 커야 합니다.")

        # 공백만 입력한 카테고리도 빈 카테고리로 처리한다.
        if not self.category.strip():
            raise ValueError("카테고리는 비어 있을 수 없습니다.")