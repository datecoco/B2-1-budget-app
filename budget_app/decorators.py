"""로그 기록·시간 측정처럼 '본 기능과 상관없는 공통 작업'을 데코레이터로 모아 둔다.

errors.py의 handle_errors는 오류 처리, 이 파일은 기록(로그)과 시간 측정을 맡는다.
각자 한 가지 일만 하므로, main() 본문을 고치지 않고 위에 붙였다 뗐다 할 수 있다.

- log_command : 명령 시작/끝과 종료 코드를 <data-dir>/budget.log 파일에 남긴다.
- timed       : 명령이 걸린 시간을 재서 같은 로그 파일에 남긴다.
                BUDGET_DEBUG=1 환경 변수가 있으면 화면(stderr)에도 보여 준다.

로그는 화면(stdout)에 찍지 않는다. 화면 출력은 예전과 똑같이 유지된다.
"""

from __future__ import annotations

import argparse
import functools
import logging
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path

# 로그 파일 이름. --data-dir 폴더 안에 만든다. (기본: data/budget.log)
LOG_FILE_NAME = "budget.log"

# 이 프로그램 전용 로거. 다른 라이브러리 로그와 섞이지 않게 이름을 붙인다.
logger = logging.getLogger("budget_app")
logger.setLevel(logging.INFO)
# 루트 로거로 넘기지 않는다. (넘기면 화면에 찍힐 수 있다)
logger.propagate = False


def find_data_dir(argv: list[str]) -> str:
    """명령줄에서 --data-dir 값만 골라 읽는다. 없으면 기본값 'data'."""

    # 다른 옵션은 무시하고 --data-dir만 읽는 작은 파서다.
    # add_help=False: -h가 있어도 여기서는 도움말을 띄우지 않는다.
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--data-dir", default="data")
    known, _ = parser.parse_known_args(argv)
    return known.data_dir


def command_text(argv: list[str]) -> str:
    """로그에 남길 명령 문자열을 만든다. 예: 'list --limit 5'"""

    return " ".join(argv) if argv else "(명령 없음)"


def log_command(func: Callable[[], int]) -> Callable[[], int]:
    """명령 시작과 끝(종료 코드)을 로그 파일에 남긴다.

    로그 기록이 실패해도(폴더 권한 등) 명령 자체는 그대로 실행된다.
    """

    @functools.wraps(func)
    def wrapper() -> int:
        argv = sys.argv[1:]
        handler: logging.Handler | None = None

        # 1) 로그 파일 준비. 실패하면 로그 없이 진행한다.
        try:
            log_dir = Path(find_data_dir(argv))
            log_dir.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(log_dir / LOG_FILE_NAME, encoding="utf-8")
            handler.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            )
            logger.addHandler(handler)
            logger.info("시작: %s", command_text(argv))
        except Exception:
            handler = None

        # 2) 진짜 명령 실행. 종료 코드는 그대로 돌려준다.
        exit_code: int | None = None
        try:
            exit_code = func()
            return exit_code
        finally:
            # 3) 끝 기록 + 파일 닫기. 여기서 난 오류도 명령 결과를 바꾸지 않는다.
            try:
                if exit_code is None:
                    # --help처럼 SystemExit로 바로 끝난 경우 등
                    logger.info("끝: %s (종료 코드: 중간에 종료)", command_text(argv))
                else:
                    logger.info("끝: %s (종료 코드: %s)", command_text(argv), exit_code)
            except Exception:
                pass
            if handler is not None:
                logger.removeHandler(handler)
                handler.close()

    return wrapper


def timed(func: Callable[[], int]) -> Callable[[], int]:
    """명령이 걸린 시간을 재서 로그에 남긴다.

    BUDGET_DEBUG=1 이면 화면 오류 출력(stderr)에도 보여 준다.
    stdout은 건드리지 않는다.
    """

    @functools.wraps(func)
    def wrapper() -> int:
        # perf_counter: 시간 재기에 쓰는 정밀한 시계
        start = time.perf_counter()
        try:
            return func()
        finally:
            elapsed = time.perf_counter() - start
            try:
                logger.info("걸린 시간: %.4f초", elapsed)
                if os.environ.get("BUDGET_DEBUG") == "1":
                    print(f"[timing] {func.__name__}: {elapsed:.4f}초", file=sys.stderr)
            except Exception:
                pass

    return wrapper
