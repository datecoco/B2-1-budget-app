"""log_command / timed 데코레이터가 제대로 붙어 있는지 확인하는 테스트.

실행 방법 (레포 맨 위 폴더에서):
    python3 -m unittest discover tests
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

# 거래가 없을 때 list가 보여 주는 문구 (데코레이터를 붙이기 전과 같아야 한다)
EMPTY_LIST = "아직 거래가 없습니다. add로 첫 거래를 추가해 보세요.\n"


class DecoratorTest(unittest.TestCase):
    """로그 파일, 시간 기록, 화면 출력, 종료 코드를 확인한다."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.data_dir = os.path.join(self.temp.name, "data")
        self.log_path = Path(self.data_dir) / "budget.log"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_app(
        self, *args: str, input_text: str = "", debug: bool = False
    ) -> subprocess.CompletedProcess:
        """임시 폴더를 --data-dir로 써서 프로그램을 실행한다."""
        env = dict(os.environ)
        env.pop("BUDGET_DEBUG", None)
        if debug:
            env["BUDGET_DEBUG"] = "1"
        return subprocess.run(
            [sys.executable, "-m", "budget_app", "--data-dir", self.data_dir, *args],
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=PROJECT_DIR,
            env=env,
        )

    def read_log(self) -> str:
        return self.log_path.read_text(encoding="utf-8")

    def test_log_file_has_start_and_end(self) -> None:
        result = self.run_app("list")
        self.assertEqual(result.returncode, 0)
        log = self.read_log()
        self.assertIn("시작: --data-dir", log)
        self.assertIn("list", log)
        self.assertIn("(종료 코드: 0)", log)

    def test_timing_is_recorded(self) -> None:
        self.run_app("list")
        self.assertIn("걸린 시간:", self.read_log())

    def test_stdout_unchanged(self) -> None:
        # 로그와 시간은 화면(stdout)에 나오지 않아야 한다.
        result = self.run_app("list")
        self.assertEqual(result.stdout, EMPTY_LIST)
        self.assertEqual(result.stderr, "")

    def test_debug_timing_goes_to_stderr_only(self) -> None:
        result = self.run_app("list", debug=True)
        self.assertEqual(result.stdout, EMPTY_LIST)
        self.assertIn("[timing] main:", result.stderr)

    def test_exit_codes_preserved(self) -> None:
        # 파일 오류는 2, 로그에도 종료 코드 2가 남아야 한다.
        result = self.run_app("import", "없는파일.csv")
        self.assertEqual(result.returncode, 2)
        self.assertIn("(종료 코드: 2)", self.read_log())

        # 입력 오류(금액이 0)는 1
        result = self.run_app("add", input_text="expense\n2026-11-16\n0\nfood\n\n\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("(종료 코드: 1)", self.read_log())

    def test_log_appends(self) -> None:
        # 실행할 때마다 기록이 이어서 쌓인다.
        self.run_app("list")
        self.run_app("summary")
        self.assertEqual(self.read_log().count("시작:"), 2)


if __name__ == "__main__":
    unittest.main()
