"""명령줄 입력을 받아 용돈 기입장 기능을 실행한다.

이 파일의 역할은 사용자가 입력한 명령을 해석하는 것이다.
예: ``py -m budget_app list --limit 3``
실제 거래 저장·검색 같은 기능은 나중에 별도 파일로 분리한다.
"""

# 타입 힌트를 현재 파이썬 버전과 더 유연하게 사용할 수 있게 해 준다.
from __future__ import annotations

# argparse는 파이썬에 기본으로 들어있는 '명령어와 옵션 해석' 도구다.
import argparse


# 프로그램이 제공할 명령어와, 각 명령어의 짧은 설명을 딕셔너리로 정리한다.
# 키(key)는 실제 입력할 명령어이고, 값(value)은 --help 화면에 보일 설명이다.
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
    """프로그램의 명령줄 사용법을 정의해 parser 객체로 반환한다."""

    # 전체 프로그램의 기본 도움말을 만든다.
    # prog: 도움말에 보여 줄 실행 명령어
    # description: 프로그램 설명
    parser = argparse.ArgumentParser(
        prog="py -m budget_app",
        description="나만의 파일 기반 용돈 기입장",
    )

    # 모든 명령어가 함께 사용할 저장 폴더 옵션이다.
    # 사용자가 생략하면 data 폴더를 기본값으로 사용한다.
    # 예: py -m budget_app --data-dir my_data list
    parser.add_argument(
        "--data-dir",
        default="data",
        help="저장 파일 폴더 (기본값: data)",
    )

    # add, list처럼 '하위 명령어'를 등록할 준비를 한다.
    # dest="command"는 사용자가 입력한 명령어가 args.command에 저장된다는 뜻이다.
    # metavar는 도움말 화면에서 명령어 자리에 보여 줄 글자다.
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    # 위 딕셔너리를 순회하며 각 하위 명령어를 등록한다.
    # 아직 기능 구현 전이므로 사용법과 설명만 먼저 만들어 둔 상태다.
    for command, description in COMMAND_DESCRIPTIONS.items():
        subparsers.add_parser(command, help=description, description=description)

    # 완성된 parser를 main()에 돌려준다.
    return parser


def main() -> int:
    """명령을 해석하고, 현재는 준비 중 안내 메시지를 출력한다.

    반환값 0은 정상 종료를 의미한다.
    """
    # 위 함수에서 정의한 명령어 규칙을 가져온다.
    parser = create_parser()

    # 터미널에 입력한 내용을 분석한다.
    # 예를 들어 list를 입력했다면 args.command 값은 "list"가 된다.
    args = parser.parse_args()

    # 명령어 없이 실행했다면 오류 대신 전체 도움말을 보여 준다.
    if args.command is None:
        parser.print_help()
        return 0

    # 각 기능은 다음 단계에서 이 위치에 연결해 구현한다.
    print(f"[준비 중] '{args.command}' 기능은 다음 단계에서 구현합니다.")
    return 0
