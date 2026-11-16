"""명령줄 입력을 받아 용돈 기입장 기능을 실행한다."""

from __future__ import annotations

import argparse

import uuid

from budget_app.models import Transaction
from budget_app.repositories import CategoryRepository, TransactionRepository


# 프로그램이 제공할 명령어와 짧은 설명이다.
COMMAND_DESCRIPTIONS = {
    "add": "대화형으로 거래를 추가합니다.",
    "list": "최신 거래 목록을 조회합니다.",
    "search": "조건에 맞는 거래를 검색합니다.",
    "summary": "월별 수입·지출을 요약합니다.",
    "budget": "월 예산을 설정하거나 조회합니다.",
    "category": "카테고리를 관리합니다.",
    "update": "거래를 수정합니다.",
    "delete": "거래를 삭제합니다.",
    "import": "CSV 거래 파일을 가져옵니다.",
    "export": "조건에 맞는 거래를 CSV로 내보냅니다.",
}


def create_parser() -> argparse.ArgumentParser:
    """프로그램의 명령어 규칙과 도움말을 만든다."""

    # 전체 프로그램의 기본 도움말을 만든다.
    parser = argparse.ArgumentParser(
        prog="py -m budget_app",
        description="나만의 파일 기반 용돈 기입장",
    )

    # 저장 파일 폴더를 바꾸고 싶을 때 쓰는 공통 옵션이다.
    parser.add_argument(
        "--data-dir",
        default="data",
        help="저장 파일 폴더 (기본값: data)",
    )

    # add, list처럼 첫 번째 명령어를 등록할 준비를 한다.
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    # category를 제외한 일반 명령어를 등록한다.
    for command, description in COMMAND_DESCRIPTIONS.items():
        if command != "category":
            command_parser = subparsers.add_parser(
                command,
                help=description,
                description=description,
            )

            # search는 찾을 조건을 옵션으로 받는다. 안 넣은 조건은 무시한다.
            if command == "search":
                command_parser.add_argument("--category", help="카테고리")
                command_parser.add_argument("--type", help="income 또는 expense")
                command_parser.add_argument("--keyword", help="메모에 들어간 글자")


            # update는 고칠 거래의 id를 받는다.
            if command == "update":
                command_parser.add_argument("id", help="수정할 거래 id")


            # list는 몇 건을 보여 줄지 정하는 --limit 옵션을 받는다.
            if command == "list":
                command_parser.add_argument(
                    "--limit",
                    type=int,
                    default=10,
                    help="보여 줄 거래 수 (기본값: 10)",
                )
    # category는 list 같은 두 번째 명령어를 더 받는다.
    category_parser = subparsers.add_parser(
        "category",
        help=COMMAND_DESCRIPTIONS["category"],
        description=COMMAND_DESCRIPTIONS["category"],
    )
    category_subparsers = category_parser.add_subparsers(
        dest="category_command",
        metavar="action",
    )

    # 현재는 category list만 구현한다.
    category_subparsers.add_parser(
        "list",
        help="등록된 카테고리 목록을 출력합니다.",
    )

    return parser


def main() -> int:
    """사용자 명령을 읽고 알맞은 기능을 실행한다."""

    parser = create_parser()
    args = parser.parse_args()

    # 명령어 없이 실행하면 전체 도움말을 보여 준다.
    if args.command is None:
        parser.print_help()
        return 0

    # py -m budget_app search를 처리한다. 조건에 맞는 거래만 보여 준다.
    if args.command == "search":
        for t in TransactionRepository(args.data_dir).iter_transactions():
            if args.category and t.category != args.category:
                continue
            if args.type and t.type != args.type:
                continue
            if args.keyword and args.keyword not in t.memo:
                continue
            print(f"{t.id}  {t.date}  {t.type}  {t.amount:,}원  {t.category}  {t.memo}")

        return 0

        # py -m budget_app add를 처리한다. 필요한 값을 하나씩 물어본다.
    if args.command == "add":
        transaction = Transaction(
            id=uuid.uuid4().hex[:8],
            type=input("수입/지출 (income/expense): ").strip(),
            date=input("날짜 (YYYY-MM-DD): ").strip(),
            amount=int(input("금액: ").strip()),
            category=input("카테고리: ").strip(),
            memo=input("메모 (없으면 엔터): ").strip(),
        )
        TransactionRepository(args.data_dir).add(transaction)
        print(f"저장 완료! (id: {transaction.id})")
        return 0

    # py -m budget_app update <id>를 처리한다. 엔터만 치면 기존 값을 유지한다.
    if args.command == "update":
        repository = TransactionRepository(args.data_dir)
        transactions = list(repository.iter_transactions())

        for i, t in enumerate(transactions):
            if t.id == args.id:
                amount = input(f"금액 [{t.amount}]: ").strip()
                category = input(f"카테고리 [{t.category}]: ").strip()
                memo = input(f"메모 [{t.memo}]: ").strip()

                transactions[i] = Transaction(
                    id=t.id,
                    type=t.type,
                    date=t.date,
                    amount=int(amount) if amount else t.amount,
                    category=category or t.category,
                    memo=memo or t.memo,
                    tags=t.tags,
                )
                repository.save_all(transactions)
                print(f"수정 완료! (id: {t.id})")
                return 0

        print(f"id {args.id}인 거래를 찾지 못했습니다.")
        return 1

    # py -m budget_app list를 처리한다. 최신 거래부터 limit개만 보여 준다.
    if args.command == "list":
        transactions = list(TransactionRepository(args.data_dir).iter_transactions())
        transactions.sort(key=lambda t: t.date, reverse=True)

        for t in transactions[: args.limit]:
            print(f"{t.id}  {t.date}  {t.type}  {t.amount:,}원  {t.category}  {t.memo}")
        return 0


    # py -m budget_app category list를 처리한다.
    if args.command == "category" and args.category_command == "list":
        repository = CategoryRepository(args.data_dir)

        # 카테고리를 한 개씩 출력한다.
        for category in repository.iter_categories():
            print(f"- {category}")

        return 0

    # 아직 구현하지 않은 명령은 안내 메시지를 보여 준다.
    print(f"[준비 중] '{args.command}' 기능은 다음 단계에서 구현합니다.")
    return 0