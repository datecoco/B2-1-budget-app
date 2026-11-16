"""거래 데이터를 파일에 저장하고 읽어 오는 기능을 담당한다."""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import asdict
from pathlib import Path

from budget_app.models import Transaction


class TransactionRepository:
    """transactions.jsonl 파일을 관리한다."""

    def __init__(self, data_dir: str | Path = "data") -> None:
        # data_dir 문자열을 파일 경로를 다루기 편한 Path 객체로 바꾼다.
        self.data_dir = Path(data_dir)

        # 실제 거래 데이터가 저장될 파일의 위치다.
        self.file_path = self.data_dir / "transactions.jsonl"

        # data 폴더가 없으면 자동으로 만든다.
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 거래 파일이 없으면 빈 파일을 만든다.
        self.file_path.touch(exist_ok=True)

    def add(self, transaction: Transaction) -> None:
        """거래 한 건을 JSONL 파일 마지막 줄에 추가한다."""

        # dataclass 객체를 파일에 저장 가능한 딕셔너리로 바꾼다.
        record = asdict(transaction)

        # "a"는 append의 약자다. 기존 내용을 지우지 않고 마지막에 추가한다.
        with self.file_path.open("a", encoding="utf-8") as file:
            # JSON 한 줄을 저장하고 줄바꿈을 붙인다.
            # ensure_ascii=False로 한글 메모도 그대로 저장한다.
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def iter_transactions(self) -> Iterator[Transaction]:
        """파일을 한 줄씩 읽으며 거래를 하나씩 반환한다."""

        # 파일 전체를 한꺼번에 읽지 않는다.
        with self.file_path.open("r", encoding="utf-8") as file:
            for line in file:
                # 빈 줄은 건너뛴다.
                if not line.strip():
                    continue

                # JSON 문자열 한 줄을 딕셔너리로 되돌린다.
                record = json.loads(line)

                # 딕셔너리를 Transaction 객체로 바꾼 뒤 하나씩 반환한다.
                yield Transaction(**record)


    def save_all(self, transactions: list[Transaction]) -> None:
        """거래 목록 전체로 파일을 새로 쓴다. 수정·삭제할 때 쓴다."""

        # "w"는 write의 약자다. 기존 내용을 지우고 처음부터 다시 쓴다.
        with self.file_path.open("w", encoding="utf-8") as file:
            for transaction in transactions:
                record = asdict(transaction)
                file.write(json.dumps(record, ensure_ascii=False) + "\n")



class CategoryRepository:
    """categories.jsonl 파일을 관리한다."""

    # 처음 실행할 때 자동으로 넣을 기본 카테고리다.
    DEFAULT_CATEGORIES = ("food", "transport", "rent", "salary", "etc")

    def __init__(self, data_dir: str | Path = "data") -> None:
        # CategoryRepository도 같은 data 폴더를 사용한다.
        self.data_dir = Path(data_dir)

        # 카테고리 목록을 저장할 파일 위치다.
        self.file_path = self.data_dir / "categories.jsonl"

        # data 폴더와 파일이 없으면 자동으로 만든다.
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)

        # 파일이 완전히 비어 있다면 기본 카테고리를 채운다.
        if self.file_path.stat().st_size == 0:
            for category in self.DEFAULT_CATEGORIES:
                self.add(category)

    def add(self, category: str) -> None:
        """카테고리 하나를 JSONL 파일 마지막에 추가한다."""

        # 앞뒤 공백을 없애고, 빈 이름은 막는다.
        category = category.strip()
        if not category:
            raise ValueError("카테고리 이름은 비어 있을 수 없습니다.")

        # JSON 한 줄에 카테고리 하나를 저장한다.
        with self.file_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps({"name": category}, ensure_ascii=False) + "\n")

    def iter_categories(self) -> Iterator[str]:
        """카테고리를 파일에서 하나씩 읽어 반환한다."""

        with self.file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue

                # {"name": "food"}에서 "food"만 꺼내 반환한다.
                record = json.loads(line)
                yield record["name"]
    

    def remove(self, category: str) -> bool:
        """카테고리 하나를 지운다. 지웠으면 True, 없었으면 False를 돌려준다."""

        categories = list(self.iter_categories())
        if category not in categories:
            return False

        # 지울 이름만 빼고 파일을 처음부터 다시 쓴다.
        with self.file_path.open("w", encoding="utf-8") as file:
            for name in categories:
                if name != category:
                    file.write(json.dumps({"name": name}, ensure_ascii=False) + "\n")

        return True