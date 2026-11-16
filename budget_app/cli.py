"""명령줄 입력을 받아 용돈 기입장 기능을 실행한다."""

from __future__ import annotations

import argparse
import csv

from budget_app.errors import handle_errors

from budget_app.models import Transaction
from budget_app.repositories import (
    BudgetRepository,
    CategoryRepository,
    TransactionRepository,
)


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


            # delete도 지울 거래의 id를 받는다.
            if command == "delete":
                command_parser.add_argument("id", help="삭제할 거래 id")

            # summary는 요약할 달과 TOP 몇 개를 보여 줄지 받는다.
            if command == "summary":
                command_parser.add_argument("--month", required=True, help="요약할 달 (YYYY-MM)")
                command_parser.add_argument("--top", type=int, default=3, help="지출 TOP N (기본값: 3)")

            # budget은 달을 받고, --amount를 주면 예산을 저장한다.
            if command == "budget":
                command_parser.add_argument("--month", required=True, help="예산 달 (YYYY-MM)")
                command_parser.add_argument("--amount", type=int, help="저장할 예산 금액")


            # import는 가져올 CSV 파일 경로를 받는다.
            if command == "import":
                command_parser.add_argument("file", help="가져올 CSV 파일")

            # export는 저장할 CSV 파일 경로와 선택 조건을 받는다.
            if command == "export":
                command_parser.add_argument("file", help="저장할 CSV 파일")
                command_parser.add_argument("--month", help="이 달만 내보내기 (YYYY-MM)")


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

    # category list: 등록된 카테고리 목록을 보여 준다.
    category_subparsers.add_parser(
        "list",
        help="등록된 카테고리 목록을 출력합니다.",
    )

    # category add <이름>: 새 카테고리를 추가한다.
    category_add_parser = category_subparsers.add_parser(
        "add",
        help="새 카테고리를 추가합니다.",
    )
    category_add_parser.add_argument("name", help="추가할 카테고리 이름")

    # category remove <이름>: 카테고리를 삭제한다.
    category_remove_parser = category_subparsers.add_parser(
        "remove",
        help="카테고리를 삭제합니다.",
    )
    category_remove_parser.add_argument("name", help="삭제할 카테고리 이름")

    return parser


# CSV 첫 줄(헤더)에 들어갈 칸 이름과 순서다.
CSV_HEADER = ["id", "date", "type", "amount", "category", "memo"]


def make_id(repository: TransactionRepository, date: str) -> str:
    """거래 날짜로 id를 만든다. 예: 2026-11-16의 첫 거래는 261116-1"""

    # "2026-11-16"에서 "-"를 빼고 앞의 "20"을 잘라 "261116"으로 만든다.
    prefix = date.replace("-", "")[2:]

    # 같은 날짜 id 중 가장 큰 번호를 찾는다.
    biggest = 0
    for t in repository.iter_transactions():
        if t.id.startswith(prefix + "-"):
            number = int(t.id.split("-")[1])
            biggest = max(biggest, number)

    # 가장 큰 번호에 1을 더해 겹치지 않게 한다.
    return f"{prefix}-{biggest + 1}"



@handle_errors

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
        repository = TransactionRepository(args.data_dir)

        type_ = input("수입/지출 (income/expense): ").strip()
        date = input("날짜 (YYYY-MM-DD): ").strip()
        amount = int(input("금액: ").strip())
        category = input("카테고리: ").strip()
        memo = input("메모 (없으면 엔터): ").strip()

        transaction = Transaction(
            id=make_id(repository, date),
            type=type_,
            date=date,
            amount=amount,
            category=category,
            memo=memo,
        )
        repository.add(transaction)
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


    # py -m budget_app delete <id>를 처리한다. 지우기 전에 한 번 더 확인한다.
    if args.command == "delete":
        repository = TransactionRepository(args.data_dir)
        transactions = list(repository.iter_transactions())

        # 지울 id가 아닌 거래만 남긴다.
        remaining = [t for t in transactions if t.id != args.id]

        if len(remaining) == len(transactions):
            print(f"id {args.id}인 거래를 찾지 못했습니다.")
            return 1

        answer = input(f"id {args.id} 거래를 삭제할까요? (y/n): ").strip()
        if answer != "y":
            print("삭제를 취소했습니다.")
            return 0

        repository.save_all(remaining)
        print(f"삭제 완료! (id: {args.id})")
        return 0



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

    # py -m budget_app category add <이름>을 처리한다.
    if args.command == "category" and args.category_command == "add":
        repository = CategoryRepository(args.data_dir)

        # 이미 있는 이름이면 또 넣지 않는다.
        if args.name in repository.iter_categories():
            print(f"'{args.name}' 카테고리는 이미 있습니다.")
            return 1

        repository.add(args.name)
        print(f"'{args.name}' 카테고리를 추가했습니다.")
        return 0

    # py -m budget_app category remove <이름>을 처리한다.
    if args.command == "category" and args.category_command == "remove":
        repository = CategoryRepository(args.data_dir)

        if repository.remove(args.name):
            print(f"'{args.name}' 카테고리를 삭제했습니다.")
            return 0

        print(f"'{args.name}' 카테고리를 찾지 못했습니다.")
        return 1

    # py -m budget_app summary --month YYYY-MM을 처리한다.
    if args.command == "summary":
        income = 0
        expense = 0
        by_category = {}

        for t in TransactionRepository(args.data_dir).iter_transactions():
            # 날짜가 "2026-11"로 시작하는 거래만 센다.
            if not t.date.startswith(args.month):
                continue

            if t.type == "income":
                income += t.amount
            else:
                expense += t.amount
                # 카테고리별 지출을 딕셔너리에 더한다.
                by_category[t.category] = by_category.get(t.category, 0) + t.amount

        print(f"[{args.month} 요약]")
        print(f"수입: {income:,}원")
        print(f"지출: {expense:,}원")
        print(f"잔액: {income - expense:,}원")

        # 지출이 큰 카테고리부터 정렬해서 top개만 보여 준다.
        ranking = sorted(by_category.items(), key=lambda item: item[1], reverse=True)
        print(f"지출 TOP {args.top}:")
        for rank, (category, amount) in enumerate(ranking[: args.top], start=1):
            print(f"  {rank}. {category} {amount:,}원")

        return 0


    # py -m budget_app budget --month YYYY-MM [--amount 금액]을 처리한다.
    if args.command == "budget":
        repository = BudgetRepository(args.data_dir)

        # --amount를 주면 예산을 저장한다.
        if args.amount is not None:
            repository.set(args.month, args.amount)
            print(f"{args.month} 예산을 {args.amount:,}원으로 저장했습니다.")
            return 0

        # --amount가 없으면 예산과 사용률을 보여 준다.
        budget = repository.load().get(args.month)
        if budget is None:
            print(f"{args.month} 예산이 없습니다. --amount로 먼저 저장하세요.")
            return 1

        spent = 0
        for t in TransactionRepository(args.data_dir).iter_transactions():
            if t.date.startswith(args.month) and t.type == "expense":
                spent += t.amount

        rate = spent / budget * 100
        print(f"[{args.month} 예산]")
        print(f"예산: {budget:,}원")
        print(f"지출: {spent:,}원")
        print(f"사용률: {rate:.1f}%")

        if spent > budget:
            print(f"⚠️ 예산을 {spent - budget:,}원 초과했습니다!")

        return 0


    # py -m budget_app export 파일.csv [--month YYYY-MM]을 처리한다.
    if args.command == "export":
        count = 0
        # newline=""은 CSV 줄바꿈이 두 번 들어가지 않게 막는다.
        with open(args.file, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)

            for t in TransactionRepository(args.data_dir).iter_transactions():
                if args.month and not t.date.startswith(args.month):
                    continue
                writer.writerow([t.id, t.date, t.type, t.amount, t.category, t.memo])
                count += 1

        print(f"{count}건을 {args.file}로 내보냈습니다.")
        return 0

    # py -m budget_app import 파일.csv를 처리한다. 잘못된 줄은 건너뛴다.
    if args.command == "import":
        repository = TransactionRepository(args.data_dir)
        success = 0
        failures = []

        with open(args.file, "r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            # 헤더가 약속한 형식과 다르면 아예 시작하지 않는다.
            if reader.fieldnames != CSV_HEADER:
                print(f"CSV 헤더가 다릅니다. 첫 줄은 {','.join(CSV_HEADER)} 이어야 합니다.")
                return 1

            # 2부터 세는 이유: 1번 줄은 헤더라서.
            for line_number, row in enumerate(reader, start=2):
                try:
                    transaction = Transaction(
                        id=make_id(repository, row["date"]),
                        type=row["type"],
                        date=row["date"],
                        amount=int(row["amount"]),
                        category=row["category"],
                        memo=row["memo"],
                    )
                except ValueError as error:
                    failures.append(f"{line_number}번 줄: {error}")
                    continue

                repository.add(transaction)
                success += 1

        print(f"{success}건을 가져왔습니다.")
        for failure in failures:
            print(f"  건너뜀 - {failure}")
        return 0


    # 아직 구현하지 않은 명령은 안내 메시지를 보여 준다.
    print(f"[준비 중] '{args.command}' 기능은 다음 단계에서 구현합니다.")
    return 0