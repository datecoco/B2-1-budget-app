"""명령줄 입력을 받아 용돈 기입장 기능을 실행한다."""

from __future__ import annotations

import argparse

from budget_app.repositories import CategoryRepository


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
            subparsers.add_parser(
                command,
                help=description,
                description=description,
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