"""모든 명령어를 실제로 실행해 보고 결과를 확인하는 테스트.

실행 방법 (레포 맨 위 폴더에서):
    python3 -m unittest discover tests

진짜 data 폴더를 건드리지 않도록, 테스트마다 임시 폴더를 --data-dir로 쓴다.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# 레포 맨 위 폴더. 여기서 실행해야 budget_app 패키지를 찾을 수 있다.
PROJECT_DIR = Path(__file__).resolve().parent.parent
SAMPLE_CSV = PROJECT_DIR / "sample.csv"


class CommandTest(unittest.TestCase):
    """명령어를 하나씩 실행해서 종료 코드와 출력을 확인한다."""

    def setUp(self) -> None:
        # 테스트마다 새 임시 폴더를 만들고, 끝나면 자동으로 지운다.
        self.temp = tempfile.TemporaryDirectory()
        self.data_dir = os.path.join(self.temp.name, "data")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_app(self, *args: str, input_text: str = "") -> subprocess.CompletedProcess:
        """python3 -m budget_app --data-dir <임시폴더> ... 를 실행한다.

        add/update/delete처럼 질문하는 명령은 input_text로 답을 넣어 준다.
        """
        return subprocess.run(
            [sys.executable, "-m", "budget_app", "--data-dir", self.data_dir, *args],
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=PROJECT_DIR,
        )

    def add_sample(self) -> None:
        """테스트용 거래 2건을 add로 넣는다."""
        # 답 순서: 타입, 날짜, 금액, 카테고리, 메모, 태그
        self.run_app("add", input_text="expense\n2026-11-16\n9000\nfood\n점심\n외식\n")
        self.run_app("add", input_text="income\n2026-11-01\n300000\nsalary\n용돈\n\n")

    def test_add(self) -> None:
        result = self.run_app("add", input_text="expense\n2026-11-16\n9000\nfood\n점심\n외식\n")
        self.assertEqual(result.returncode, 0)
        self.assertIn("저장 완료! (id: 261116-1)", result.stdout)

        # 같은 날짜로 한 번 더 넣으면 번호가 2가 된다.
        result = self.run_app("add", input_text="expense\n2026-11-16\n3000\nfood\n간식\n\n")
        self.assertIn("저장 완료! (id: 261116-2)", result.stdout)

    def test_add_wrong_amount(self) -> None:
        # 금액이 0이면 입력 오류(종료 코드 1)가 나야 한다.
        result = self.run_app("add", input_text="expense\n2026-11-16\n0\nfood\n\n\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("입력 오류", result.stdout)

    def test_list(self) -> None:
        # 처음에는 거래가 없다는 안내가 나온다.
        result = self.run_app("list")
        self.assertEqual(result.returncode, 0)
        self.assertIn("아직 거래가 없습니다", result.stdout)

        # 추가한 뒤에는 최신 날짜가 먼저 나온다.
        self.add_sample()
        result = self.run_app("list")
        lines = result.stdout.strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].startswith("261116-1"))
        self.assertTrue(lines[1].startswith("261101-1"))

    def test_data_kept_after_rerun(self) -> None:
        # 프로그램을 따로따로 실행해도 파일에 저장된 거래가 남아 있다.
        self.add_sample()
        result = self.run_app("list", "--limit", "1")
        self.assertEqual(len(result.stdout.strip().splitlines()), 1)
        self.assertTrue(Path(self.data_dir, "transactions.jsonl").exists())

    def test_search(self) -> None:
        self.add_sample()
        result = self.run_app("search", "--tag", "외식")
        self.assertEqual(result.returncode, 0)
        self.assertIn("261116-1", result.stdout)
        self.assertNotIn("261101-1", result.stdout)

        result = self.run_app("search", "--type", "income", "--from", "2026-11-01", "--to", "2026-11-30")
        self.assertIn("261101-1", result.stdout)
        self.assertNotIn("261116-1", result.stdout)

    def test_summary(self) -> None:
        self.add_sample()
        result = self.run_app("summary", "--month", "2026-11")
        self.assertEqual(result.returncode, 0)
        self.assertIn("수입: 300,000원", result.stdout)
        self.assertIn("지출: 9,000원", result.stdout)
        self.assertIn("잔액: 291,000원", result.stdout)
        self.assertIn("1. food 9,000원", result.stdout)

    def test_budget(self) -> None:
        self.add_sample()
        result = self.run_app("budget", "--month", "2026-11", "--amount", "5000")
        self.assertEqual(result.returncode, 0)

        # 지출 9,000원 > 예산 5,000원이라 초과 경고가 나온다.
        result = self.run_app("budget", "--month", "2026-11")
        self.assertIn("사용률: 180.0%", result.stdout)
        self.assertIn("4,000원 초과", result.stdout)

    def test_category(self) -> None:
        self.add_sample()
        result = self.run_app("category", "add", "hobby")
        self.assertEqual(result.returncode, 0)
        self.assertIn("- hobby", self.run_app("category", "list").stdout)

        # 거래에서 쓰는 food는 지울 수 없다.
        result = self.run_app("category", "remove", "food")
        self.assertEqual(result.returncode, 1)
        self.assertIn("삭제할 수 없습니다", result.stdout)

    def test_update(self) -> None:
        self.add_sample()
        # 답 순서: 금액, 카테고리, 메모 (엔터만 치면 기존 값 유지)
        result = self.run_app("update", "261116-1", input_text="12000\n\n저녁\n")
        self.assertEqual(result.returncode, 0)
        self.assertIn("수정 완료! (id: 261116-1)", result.stdout)

        line = self.run_app("search", "--keyword", "저녁").stdout
        self.assertIn("12,000원", line)
        self.assertIn("food", line)

        # 없는 id는 종료 코드 1
        result = self.run_app("update", "999999-1", input_text="\n\n\n")
        self.assertEqual(result.returncode, 1)

    def test_delete(self) -> None:
        self.add_sample()

        # n이라고 답하면 지우지 않는다.
        result = self.run_app("delete", "261116-1", input_text="n\n")
        self.assertIn("삭제를 취소했습니다.", result.stdout)
        self.assertIn("261116-1", self.run_app("list").stdout)

        # y라고 답하면 지운다.
        result = self.run_app("delete", "261116-1", input_text="y\n")
        self.assertEqual(result.returncode, 0)
        self.assertIn("삭제 완료! (id: 261116-1)", result.stdout)
        self.assertNotIn("261116-1", self.run_app("list").stdout)

    def test_export(self) -> None:
        self.add_sample()
        out_file = os.path.join(self.temp.name, "out.csv")
        result = self.run_app("export", out_file, "--month", "2026-11")
        self.assertEqual(result.returncode, 0)
        self.assertIn("2건을", result.stdout)

        with open(out_file, encoding="utf-8") as file:
            lines = file.read().splitlines()
        self.assertEqual(lines[0], "id,date,type,amount,category,memo")
        self.assertEqual(len(lines), 3)

    def test_import_partial(self) -> None:
        # 기본(부분 성공): 올바른 2건만 들어가고 틀린 2줄은 건너뛴다.
        result = self.run_app("import", str(SAMPLE_CSV))
        self.assertEqual(result.returncode, 0)
        self.assertIn("2건을 가져왔습니다.", result.stdout)
        self.assertIn("건너뜀 - 4번 줄", result.stdout)
        self.assertIn("건너뜀 - 5번 줄", result.stdout)
        self.assertEqual(len(self.run_app("list").stdout.strip().splitlines()), 2)

    def test_import_atomic_rollback(self) -> None:
        # --atomic: 틀린 줄이 있으면 한 건도 저장하지 않고 종료 코드 1
        result = self.run_app("import", str(SAMPLE_CSV), "--atomic")
        self.assertEqual(result.returncode, 1)
        self.assertIn("아무것도 가져오지 않았습니다", result.stdout)
        self.assertIn("아직 거래가 없습니다", self.run_app("list").stdout)

    def test_import_atomic_clean(self) -> None:
        # --atomic이어도 모든 줄이 올바르면 전부 들어가고, 같은 날짜 id도 겹치지 않는다.
        clean_csv = os.path.join(self.temp.name, "clean.csv")
        with open(clean_csv, "w", encoding="utf-8", newline="") as file:
            file.write("id,date,type,amount,category,memo\n")
            file.write(",2026-11-01,expense,5000,food,점심\n")
            file.write(",2026-11-01,expense,3000,food,간식\n")
            file.write(",2026-11-02,income,30000,salary,용돈\n")

        result = self.run_app("import", clean_csv, "--atomic")
        self.assertEqual(result.returncode, 0)
        self.assertIn("3건을 가져왔습니다.", result.stdout)

        listed = self.run_app("list").stdout
        self.assertIn("261101-1", listed)
        self.assertIn("261101-2", listed)
        self.assertIn("261102-1", listed)

    def test_import_missing_file(self) -> None:
        # 없는 파일은 파일 오류(종료 코드 2)
        result = self.run_app("import", "no_such_file.csv")
        self.assertEqual(result.returncode, 2)
        self.assertIn("파일 오류", result.stdout)


if __name__ == "__main__":
    unittest.main()
