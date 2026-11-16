"""여러 명령에서 함께 쓰는 오류 처리 데코레이터를 모아 둔다."""

from __future__ import annotations

import functools
from collections.abc import Callable


def handle_errors(func: Callable[[], int]) -> Callable[[], int]:
    """오류가 나면 긴 에러 화면 대신 원인과 힌트를 보여 주고 종료 코드를 돌려준다.

    종료 코드: 0 성공 / 1 입력 오류 / 2 파일 오류 / 130 사용자가 중단
    """

    @functools.wraps(func)
    def wrapper() -> int:
        try:
            return func()
        except ValueError as error:
            print(f"입력 오류: {error}")
            print("힌트: 날짜는 YYYY-MM-DD, 금액은 0보다 큰 숫자로 입력하세요.")
            return 1
        except FileNotFoundError as error:
            print(f"파일 오류: '{error.filename}' 파일을 찾을 수 없습니다.")
            print("힌트: 파일 경로와 이름을 다시 확인하세요.")
            return 2
        except KeyboardInterrupt:
            print("\n사용자가 중단했습니다.")
            return 130

    return wrapper