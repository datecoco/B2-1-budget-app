# 💰 나만의 파일 기반 용돈 기입장 (B2-1)

---

## 🔗 저장소 주소

https://github.com/datecoco/B2-1-budget-app

> 터미널에서 실행하는 CLI 프로그램이라 별도 배포 주소는 없습니다.

---

## ✨ 기능 목록

| 명령어 | 기능 | 예시 |
|---|---|---|
| `add` | 거래를 대화형으로 추가 (날짜 기반 id 자동 생성, 태그 입력) | `add` |
| `list` | 최신 거래 목록 조회 | `list --limit 5` |
| `search` | 카테고리·타입·메모·기간·태그로 검색 | `search --from 2026-11-01 --to 2026-11-30 --tag 외식` |
| `update` | 거래 수정 (엔터 치면 기존 값 유지) | `update 261116-1` |
| `delete` | 거래 삭제 (y/n 확인) | `delete 261116-1` |
| `summary` | 월별 수입·지출·잔액, 지출 TOP N | `summary --month 2026-11 --top 3` |
| `budget` | 월 예산 설정·조회, 사용률 표시 | `budget --month 2026-11 --amount 200000` |
| `import` | CSV 파일에서 거래 가져오기 (기본: 잘못된 줄만 건너뜀 / `--atomic`: 하나라도 틀리면 전체 취소) | `import sample.csv --atomic` |
| `export` | 거래를 CSV로 내보내기 | `export out.csv --month 2026-11` |
| `category` | 카테고리 목록·추가·삭제 (사용 중인 분류는 삭제 차단) | `category add hobby` |

---

## 🛠 사용 기술

- Python 3 (표준 라이브러리만 사용)
- `argparse` : 명령어와 옵션 처리
- `dataclasses` : 거래 데이터 모양 정의
- `json` / `csv` : 파일 저장, 가져오기·내보내기
- `pathlib` / `os` : 파일 경로, 안전한 파일 교체
- `unittest` / `subprocess` : 명령어 자동 테스트

---

## 📁 파일 구조

```
B2-1-budget-app/
├── budget_app/
│   ├── __init__.py
│   ├── __main__.py       # python3 -m budget_app 실행 시작점
│   ├── cli.py            # 명령어 처리
│   ├── models.py         # Transaction 데이터 모양과 검증
│   ├── repositories.py   # 파일 저장·읽기 (거래, 카테고리, 예산)
│   ├── errors.py         # 오류 처리 데코레이터 (handle_errors)
│   └── decorators.py     # 로그·시간 측정 데코레이터 (log_command, timed)
├── tests/
│   ├── __init__.py
│   ├── test_commands.py  # 모든 명령어를 실제로 실행해 보는 테스트
│   └── test_decorators.py # 로그 파일·시간 기록·종료 코드 유지 테스트
├── sample.csv            # import 시연용 CSV (정상 2줄 + 틀린 2줄)
├── data/                 # 저장 파일 (Git에 올리지 않음)
│   ├── transactions.jsonl
│   ├── categories.jsonl
│   ├── budgets.jsonl
│   └── budget.log        # 명령 실행 기록 (log_command, timed가 씀)
├── .gitignore
└── README.md
```

---

## 📚 주요 학습 내용

- **argparse 서브커맨드** : 명령어마다 다른 옵션 받기
- **파일 모드** : `"a"`(이어 쓰기)와 `"w"`(새로 쓰기)의 차이
- **안전한 파일 교체** : 임시 파일에 먼저 쓰고 `os.replace()`로 한 번에 바꾸기
- **제너레이터(`yield`)** : 파일을 한 줄씩 꺼내서 메모리 아끼기
- **타입 힌트** : 값의 종류를 표시하는 이름표 (강제는 아님)
- **데코레이터** : 함수에 오류 처리·로그 기록·시간 측정을 덧씌우기 (본 기능과 분리)
- **종료 코드** : 0 성공 / 1 입력 오류 / 2 파일 오류 / 130 사용자 중단

---

## 🔄 처리 흐름

```
명령어 입력 → argparse로 해석 → cli.py에서 명령어별 처리
          → repositories.py로 파일 읽기·쓰기 → 결과 출력
          (오류가 나면 errors.py가 받아서 안내 메시지 + 종료 코드)
          (시작·끝·걸린 시간은 decorators.py가 data/budget.log에 기록)
```

---

## 🖥 실행 예시 (실제 실행 결과)

아래는 빈 폴더(`data/demo`)에서 명령어를 차례대로 실행하고 **화면에 나온 그대로** 복사한 것입니다.
`add`·`update`·`delete`는 원래 질문에 하나씩 답하는 대화형인데, 기록을 남기려고 `printf`로 답을 한 번에 넣었습니다.
(그래서 질문과 결과가 한 줄에 이어서 보입니다. 직접 칠 때는 질문마다 입력하면 됩니다.)

```
$ printf "expense\n2026-11-16\n9000\nfood\n점심\n외식\n" | python3 -m budget_app --data-dir data/demo add
수입/지출 (income/expense): 날짜 (YYYY-MM-DD): 금액: 카테고리: 메모 (없으면 엔터): 태그 (쉼표로 구분, 없으면 엔터): 저장 완료! (id: 261116-1)


$ printf "income\n2026-11-01\n300000\nsalary\n용돈\n\n" | python3 -m budget_app --data-dir data/demo add
수입/지출 (income/expense): 날짜 (YYYY-MM-DD): 금액: 카테고리: 메모 (없으면 엔터): 태그 (쉼표로 구분, 없으면 엔터): 저장 완료! (id: 261101-1)


$ python3 -m budget_app --data-dir data/demo list
261116-1  2026-11-16  expense  9,000원  food  점심  #외식
261101-1  2026-11-01  income  300,000원  salary  용돈  

$ python3 -m budget_app --data-dir data/demo search --tag 외식
261116-1  2026-11-16  expense  9,000원  food  점심  #외식

$ python3 -m budget_app --data-dir data/demo summary --month 2026-11
[2026-11 요약]
수입: 300,000원
지출: 9,000원
잔액: 291,000원
지출 TOP 3:
  1. food 9,000원

$ python3 -m budget_app --data-dir data/demo budget --month 2026-11 --amount 200000
2026-11 예산을 200,000원으로 저장했습니다.

$ python3 -m budget_app --data-dir data/demo budget --month 2026-11
[2026-11 예산]
예산: 200,000원
지출: 9,000원
사용률: 4.5%

$ python3 -m budget_app --data-dir data/demo export data/demo/out.csv --month 2026-11
2건을 data/demo/out.csv로 내보냈습니다.

$ cat data/demo/out.csv
id,date,type,amount,category,memo
261116-1,2026-11-16,expense,9000,food,점심
261101-1,2026-11-01,income,300000,salary,용돈

$ python3 -m budget_app --data-dir data/demo import sample.csv
2건을 가져왔습니다.
  건너뜀 - 4번 줄: invalid literal for int() with base 10: 'abc'
  건너뜀 - 5번 줄: type은 income 또는 expense여야 합니다.

$ printf "12000\n\n저녁\n" | python3 -m budget_app --data-dir data/demo update 261116-1
금액 [9000]: 카테고리 [food]: 메모 [점심]: 수정 완료! (id: 261116-1)


$ printf "y\n" | python3 -m budget_app --data-dir data/demo delete 261101-2
id 261101-2 거래를 삭제할까요? (y/n): 삭제 완료! (id: 261101-2)


$ python3 -m budget_app --data-dir data/demo list
261116-1  2026-11-16  expense  12,000원  food  저녁  #외식
261102-1  2026-11-02  income  30,000원  용돈  엄마  
261101-1  2026-11-01  income  300,000원  salary  용돈
```

---

## 📥 import 정책: 부분 성공 vs `--atomic` 전체 취소

`import`는 먼저 **모든 줄을 검사만** 하고(이때는 파일에 아무것도 쓰지 않음), 그다음에 정책에 따라 저장합니다.

| 방식 | 명령 | 틀린 줄이 있을 때 | 종료 코드 |
|---|---|---|---|
| 부분 성공 (기본) | `import sample.csv` | 틀린 줄만 건너뛰고 올바른 줄은 저장, 건너뛴 줄 번호와 이유 출력 | 0 |
| 전체 취소 | `import sample.csv --atomic` | **한 건도 저장하지 않음**, 실패한 줄 번호와 이유 출력 | 1 |

- 헤더(첫 줄)가 `id,date,type,amount,category,memo`가 아니면 두 방식 모두 시작하지 않습니다.
- id는 검사가 끝난 뒤 **저장할 때 한 건씩** 만듭니다. 바로 앞에 저장한 거래까지 보고 번호를 정하므로 같은 날짜가 여러 줄이어도 `261101-1`, `261101-2`처럼 겹치지 않습니다.
- `--atomic`에서 틀린 줄이 있으면 저장 단계로 아예 넘어가지 않으므로, 되돌릴(롤백할) 것이 처음부터 생기지 않습니다.

시연용 파일 `sample.csv`(정상 2줄 + 금액이 글자인 줄 + type이 틀린 줄)로 실행한 실제 결과:

```
$ python3 -m budget_app --data-dir data/check import sample.csv
2건을 가져왔습니다.
  건너뜀 - 4번 줄: invalid literal for int() with base 10: 'abc'
  건너뜀 - 5번 줄: type은 income 또는 expense여야 합니다.

$ python3 -m budget_app --data-dir data/check2 import sample.csv --atomic
  실패 - 4번 줄: invalid literal for int() with base 10: 'abc'
  실패 - 5번 줄: type은 income 또는 expense여야 합니다.
--atomic 옵션이라 아무것도 가져오지 않았습니다. (0건)
```

> 4번 줄 메시지는 파이썬이 기본으로 내는 영어 메시지로, "금액이 숫자가 아니다"라는 뜻입니다.

---

## 🗂 저장 형식 선택: 왜 JSONL인가?

거래·카테고리·예산은 **JSONL**(한 줄에 JSON 하나)로 저장하고, **CSV**는 사람이 보거나 엑셀과 주고받는 `import` / `export`에만 씁니다.

| 비교 | JSONL (`transactions.jsonl`) | CSV |
|---|---|---|
| 한 건 추가 | 파일 끝에 한 줄만 붙이면 끝 (`"a"` 모드) → 빠름 | 마찬가지로 이어 쓰기는 가능 |
| 파일 일부가 깨졌을 때 | 그 **한 줄만** 문제, 나머지 줄은 그대로 읽힘 | 따옴표·쉼표 하나가 어긋나면 뒤쪽 칸이 밀려 해석될 수 있음 |
| 목록 값 (예: `tags: ["친구", "외식"]`) | JSON 배열 그대로 저장 | 한 칸에 목록을 넣으려면 `친구;외식`처럼 규칙을 따로 만들어야 함 |
| 숫자·문자 구분 | `amount: 9000`처럼 숫자로 저장 | 전부 글자라서 읽을 때마다 `int()` 변환 필요 |
| 한 줄씩 읽기 (제너레이터) | 줄 = 거래 한 건이라 `for line in file` + `yield`로 바로 처리 | 가능하지만 칸 순서(헤더)를 항상 맞춰야 함 |
| 사람이 보기 / 엑셀 | 불편함 | 엑셀·구글시트로 바로 열림 → **편함** |

**선택 근거**
1. 한 줄 = 한 건이라 추가가 싸고(이어 쓰기), 한 줄이 망가져도 그 줄만 영향을 받습니다.
2. `tags` 같은 목록 값을 자연스럽게 담을 수 있습니다.
3. `iter_transactions()`에서 한 줄씩 읽어 `yield`로 넘기는 스트리밍 처리와 잘 맞습니다.
4. 대신 사람이 보기 쉬운 CSV는 `export`(내보내기)와 `import`(가져오기)로 따로 제공합니다.

---

## 📈 대용량(10만 건) 성능 분석

### 측정 방법
- 거래 **100,000건**(파일 크기 약 13.8MB)을 만든 임시 폴더에서 각 명령을 3번씩 실행해 걸린 시간(중앙값)을 쟀습니다.
- 측정 환경: 리눅스 서버(Intel Xeon, 8코어), Python 3.9.25. 교육장 맥과 환경이 달라서 **숫자는 대략적인 참고용**입니다.
- 시간에는 파이썬이 켜지는 시간(약 0.05초)이 포함되어 있습니다.

| 명령 | 걸린 시간 (중앙값) | 최대 메모리 |
|---|---|---|
| `--help` (프로그램 시작만) | 0.05초 | 16MB |
| `list` | 0.78초 | 91MB |
| `search --keyword 점심` | 0.52초 | 18MB |
| `summary --month 2026-01` | 0.54초 | 18MB |
| `budget --month 2026-01` | 0.51초 | 18MB |
| `export` (10만 건 전부) | 0.60초 | 18MB |
| `add` (한 건) | 0.49초 | 18MB |
| `update` (한 건) | 0.81초 | 89MB |
| `delete` (한 건) | 0.75초 | 90MB |
| `import` 100줄 → 빈 데이터 | 0.06초 | 16MB |
| `import` 100줄 → 10만 건 데이터 | **42.13초** | 18MB |

### 찾은 병목 (실제 코드 기준)

1. **`cli.py`의 `make_id()` – 가장 큰 병목**
   id 하나를 만들 때마다 `iter_transactions()`로 파일 전체(10만 줄)를 처음부터 읽습니다. `add`가 0.5초 걸리는 이유이고, `import`는 줄마다 이걸 반복해서 **100줄에 42초**가 걸렸습니다. (빈 데이터에서는 0.06초) 즉 가져오는 줄 수 × 전체 거래 수만큼 일이 늘어납니다.
2. **`cli.py`의 `list` 처리 – 전체를 메모리에 올려 정렬**
   `list(...iter_transactions())`로 10만 건을 모두 리스트에 담고 `sort()`합니다. 최신 10건만 보여 주는데도 메모리가 91MB까지 올라갑니다. (제너레이터로 흘려 보내는 `search`/`summary`는 18MB)
3. **`update`/`delete` + `repositories.py`의 `TransactionRepository.save_all()` – 한 건 고치려고 파일 전체를 다시 씀**
   10만 건을 모두 읽어 리스트로 만든 뒤(약 90MB), 한 건만 바꾸고 13.8MB 파일 전체를 임시 파일에 새로 써서 교체합니다.
4. **`repositories.py`의 `iter_transactions()` – 매번 전체 읽기 + 검사**
   `search`/`summary`/`budget`/`export`는 메모리는 아끼지만, 조건과 상관없이 10만 줄을 모두 `json.loads()`하고 `Transaction` 검사(`__post_init__`의 날짜 정규식, `date.fromisoformat`)를 거칩니다. 그래서 어떤 조회든 약 0.5초가 바닥입니다.

### 개선 방안

| 병목 | 개선안 |
|---|---|
| `make_id()` 전체 스캔 | 날짜별 마지막 번호를 `last_ids.json` 같은 작은 파일에 따로 저장하거나, `import`에서는 파일을 **한 번만** 읽어 날짜별 최대 번호 딕셔너리를 만든 뒤 메모리에서 번호를 이어 붙이기 |
| `import` 한 줄씩 저장 | 검사가 끝난 거래를 모아 **한 번에 이어 쓰기**(배치 쓰기, 파일 한 번만 열기) |
| `list` 전체 정렬 | `heapq.nlargest(limit, ...)`로 최신 N건만 들고 있기 → 메모리를 N건 크기로 줄임 |
| 전체 읽기 (`search`, `summary` 등) | **월별 파일 나누기** (`transactions-2026-11.jsonl`) → `summary --month 2026-11`은 그 달 파일만 읽음 |
| `update`/`delete` 전체 다시 쓰기 | 월별 파일로 나누면 그 달 파일만 다시 쓰면 됨. 또는 **id → 파일 위치(offset) 색인**을 두고 해당 줄을 바로 찾기 |
| 위 문제 전체 | 데이터가 더 커지면 표준 라이브러리 **`sqlite3`**(SQLite)로 옮기기: id·날짜에 인덱스를 걸면 검색·수정·삭제가 파일 전체를 읽지 않아도 됨 |

---

## 🎀 데코레이터: 공통 관심사 분리

"명령을 처리하는 일"과 "모든 명령에 똑같이 필요한 일(오류 처리, 기록, 시간 재기)"을 나눴습니다.
공통 일은 데코레이터 3개로 만들어 `main()` 위에 붙였고, `main()` 본문에는 섞지 않았습니다.

| 데코레이터 | 파일 | 하는 일 |
| --- | --- | --- |
| `handle_errors` | `errors.py` | 오류를 잡아 안내 문구를 보여 주고 종료 코드(1 / 2 / 130)로 바꿈 |
| `log_command` | `decorators.py` | 명령 시작·끝과 **최종 종료 코드**를 `<data-dir>/budget.log`에 기록 (`logging` 모듈) |
| `timed` | `decorators.py` | `time.perf_counter()`로 실행 시간을 재서 같은 로그에 기록. `BUDGET_DEBUG=1`이면 stderr에도 표시 |

```python
@log_command    # 3. 가장 바깥: handle_errors가 정한 최종 종료 코드를 기록
@timed          # 2. 오류 처리까지 포함한 전체 시간을 잼
@handle_errors  # 1. 가장 안쪽: 오류 → 안내 문구 + 종료 코드
def main() -> int:
```

- 로그와 시간은 **화면(stdout)에 찍지 않습니다.** 그래서 위 실행 예시의 화면 출력은 그대로입니다.
- 세 데코레이터 모두 종료 코드를 바꾸지 않고 그대로 돌려줍니다.
- 로그 파일을 못 만들어도(권한 문제 등) 명령은 정상 실행됩니다.

```bash
# 실행 기록 보기
cat data/budget.log

# 걸린 시간을 화면에서 바로 보기 (stderr로 출력)
BUDGET_DEBUG=1 python3 -m budget_app list
```

```
2026-11-17 14:56:14,518 [INFO] 시작: --data-dir data/dec import 없는파일.csv
2026-11-17 14:56:14,520 [INFO] 걸린 시간: 0.0017초
2026-11-17 14:56:14,520 [INFO] 끝: --data-dir data/dec import 없는파일.csv (종료 코드: 2)
```

---

## 🖐 수동 테스트 (직접 실행해 보기)

저장소 폴더(`B2-1-budget-app`)에서 **A부터 순서대로**, 코드 블록을 복사해 터미널에 붙여 넣으면 됩니다. 출력이 아래와 같아야 합니다.

> **알아 두기**
> - `--data-dir data/check`는 연습용 폴더입니다. 명령어(`add`, `list` 등) **앞에** 둡니다. 안 쓰면 `data/`에 저장됩니다.
> - 항상 저장소 폴더에서 실행하세요. `data/check` 안에 들어갔다면 `cd ../..`로 나오고, `pwd`로 경로 끝이 `B2-1-budget-app`인지 확인하세요.
> - `echo $?`는 바로 전 명령의 종료 코드입니다. 0이면 성공, 아니면 오류입니다. 오류가 난 명령 **바로 다음**에 치세요.
> - `|`(파이프)는 `printf` 답을 키보드 입력처럼 넘깁니다. 맥에서는 영어 입력으로 바꾼 뒤 `Shift` + `\`(엔터 위, `₩`로 보이기도 함)를 누르면 됩니다.

`add`·`update`·`delete`는 대화형입니다. `printf` 없이 명령만 실행한 뒤 직접 입력해도 됩니다. 파이프로 실행하면 질문과 결과가 한 줄로 이어져 보입니다.
id는 날짜로 만듭니다. `2026-11-16`의 첫 거래는 `261116-1`입니다. `update`와 `delete`에는 `list`에 나온 id를 쓰세요.

### A. 준비 (시연 폴더 비우기)

시연용 폴더를 지우고, 빈 상태인지 확인합니다. 폴더가 없어도 오류는 나지 않습니다.

```bash
rm -rf data/check
python3 -m budget_app --data-dir data/check list
```

```
아직 거래가 없습니다. add로 첫 거래를 추가해 보세요.
```

### B. 거래 추가 (add)

지출과 수입을 한 건씩 추가합니다. 질문 순서는 수입/지출 → 날짜 → 금액 → 카테고리 → 메모 → 태그입니다. 태그가 없으면 엔터입니다.

```bash
printf 'expense\n2026-11-16\n9000\n식비\n점심\n외식\n' | python3 -m budget_app --data-dir data/check add
```

```
수입/지출 (income/expense): 날짜 (YYYY-MM-DD): 금액: 카테고리: 메모 (없으면 엔터): 태그 (쉼표로 구분, 없으면 엔터): 저장 완료! (id: 261116-1)
```

```bash
printf 'income\n2026-11-01\n300000\n용돈\n월급\n\n' | python3 -m budget_app --data-dir data/check add
```

```
수입/지출 (income/expense): 날짜 (YYYY-MM-DD): 금액: 카테고리: 메모 (없으면 엔터): 태그 (쉼표로 구분, 없으면 엔터): 저장 완료! (id: 261101-1)
```

### C. 목록·저장 유지 (list)

같은 명령을 두 번 실행해서, 프로그램을 다시 켜도 데이터가 남는지 확인합니다.

```bash
python3 -m budget_app --data-dir data/check list
python3 -m budget_app --data-dir data/check list
```

```
261116-1  2026-11-16  expense  9,000원  식비  점심  #외식
261101-1  2026-11-01  income  300,000원  용돈  월급  
261116-1  2026-11-16  expense  9,000원  식비  점심  #외식
261101-1  2026-11-01  income  300,000원  용돈  월급  
```

### D. 검색 (search)

메모 키워드와 태그로 찾습니다. (`--category`, `--type`, `--from`, `--to`도 쓸 수 있습니다.)

```bash
python3 -m budget_app --data-dir data/check search --keyword 점심
python3 -m budget_app --data-dir data/check search --tag 외식
```

```
261116-1  2026-11-16  expense  9,000원  식비  점심  #외식
261116-1  2026-11-16  expense  9,000원  식비  점심  #외식
```

### E. 수정 (update)

`261116-1`의 금액을 12,000원, 메모를 `저녁`으로 바꿉니다. 카테고리는 엔터로 유지합니다.

```bash
printf '12000\n\n저녁\n' | python3 -m budget_app --data-dir data/check update 261116-1
python3 -m budget_app --data-dir data/check list
```

```
금액 [9000]: 카테고리 [식비]: 메모 [점심]: 수정 완료! (id: 261116-1)
261116-1  2026-11-16  expense  12,000원  식비  저녁  #외식
261101-1  2026-11-01  income  300,000원  용돈  월급  
```

### F. 월별 요약 (summary)

2026년 11월 수입·지출 요약입니다.

```bash
python3 -m budget_app --data-dir data/check summary --month 2026-11
```

```
[2026-11 요약]
수입: 300,000원
지출: 12,000원
잔액: 288,000원
지출 TOP 3:
  1. 식비 12,000원
```

### G. 예산 (budget)

`--amount` 없이 달만 주면 조회, 붙이면 저장입니다. 예산이 없으면 종료 코드 1이 나옵니다.

```bash
python3 -m budget_app --data-dir data/check budget --month 2026-11
echo $?
python3 -m budget_app --data-dir data/check budget --month 2026-11 --amount 200000
python3 -m budget_app --data-dir data/check budget --month 2026-11
```

```
2026-11 예산이 없습니다. --amount로 먼저 저장하세요.
1
2026-11 예산을 200,000원으로 저장했습니다.
[2026-11 예산]
예산: 200,000원
지출: 12,000원
사용률: 6.0%
```

### H. 카테고리 (category)

처음 실행하면 기본 카테고리(`food`, `transport`, `rent`, `salary`, `etc`)가 생깁니다. 삭제 명령어는 `remove`이지 `delete`가 아닙니다. `간식`은 추가했다가 지우고, 거래에서 쓰는 `식비`는 지우지 못합니다.

```bash
python3 -m budget_app --data-dir data/check category list
python3 -m budget_app --data-dir data/check category add 간식
python3 -m budget_app --data-dir data/check category add 식비
python3 -m budget_app --data-dir data/check category list
python3 -m budget_app --data-dir data/check category remove 간식
python3 -m budget_app --data-dir data/check category list
python3 -m budget_app --data-dir data/check category remove 식비
echo $?
```

```
- food
- transport
- rent
- salary
- etc
'간식' 카테고리를 추가했습니다.
'식비' 카테고리를 추가했습니다.
- food
- transport
- rent
- salary
- etc
- 간식
- 식비
'간식' 카테고리를 삭제했습니다.
- food
- transport
- rent
- salary
- etc
- 식비
'식비' 카테고리는 거래 1건에서 쓰고 있어서 삭제할 수 없습니다.
1
```

### I. 내보내기 (export)

2026년 11월 거래를 CSV 파일로 내보냅니다.

```bash
python3 -m budget_app --data-dir data/check export data/check/out.csv --month 2026-11
```

```
2건을 data/check/out.csv로 내보냈습니다.
```

### J. 스키마 (CSV 헤더)

내보낸 파일의 첫 줄이 스키마(`CSV_HEADER`)인 `id,date,type,amount,category,memo`인지 확인합니다. 헤더가 다른 파일은 거부되고 종료 코드 1입니다.

```bash
cat data/check/out.csv
```

```
id,date,type,amount,category,memo
261116-1,2026-11-16,expense,12000,식비,저녁
261101-1,2026-11-01,income,300000,용돈,월급
```

```bash
printf 'date,amount,memo\n2026-11-05,1000,x\n' > data/check/bad.csv
python3 -m budget_app --data-dir data/check import data/check/bad.csv
echo $?
```

```
CSV 헤더가 다릅니다. 첫 줄은 id,date,type,amount,category,memo 이어야 합니다.
1
```

### K. 가져오기 (import, --atomic)

`sample.csv`의 올바른 줄만 저장되고, 틀린 줄은 건너뜁니다. 같은 파일을 두 번 import하면 거래가 한 번 더 들어가므로 **한 번만** 실행하세요. `--atomic`은 틀린 줄이 있으면 한 건도 저장하지 않고 종료 코드 1입니다.

```bash
cat sample.csv
python3 -m budget_app --data-dir data/check import sample.csv
```

```
id,date,type,amount,category,memo
,2026-11-01,expense,5000,식비,점심
,2026-11-02,income,30000,용돈,엄마
,2026-11-03,expense,abc,식비,금액이 글자
,2026-11-04,bonus,1000,용돈,type이 틀림
2건을 가져왔습니다.
  건너뜀 - 4번 줄: invalid literal for int() with base 10: 'abc'
  건너뜀 - 5번 줄: type은 income 또는 expense여야 합니다.
```

```bash
python3 -m budget_app --data-dir data/check list
```

```
261116-1  2026-11-16  expense  12,000원  식비  저녁  #외식
261102-1  2026-11-02  income  30,000원  용돈  엄마  
261101-1  2026-11-01  income  300,000원  용돈  월급  
261101-2  2026-11-01  expense  5,000원  식비  점심  
```

```bash
python3 -m budget_app --data-dir data/check import sample.csv --atomic
echo $?
```

```
  실패 - 4번 줄: invalid literal for int() with base 10: 'abc'
  실패 - 5번 줄: type은 income 또는 expense여야 합니다.
--atomic 옵션이라 아무것도 가져오지 않았습니다. (0건)
1
```

### L. 삭제 (delete)

K에서 가져온 `261102-1`(용돈/엄마)을 지웁니다. id가 다르면 `list`에서 복사하세요.

```bash
printf 'y\n' | python3 -m budget_app --data-dir data/check delete 261102-1
python3 -m budget_app --data-dir data/check list
```

```
id 261102-1 거래를 삭제할까요? (y/n): 삭제 완료! (id: 261102-1)
261116-1  2026-11-16  expense  12,000원  식비  저녁  #외식
261101-1  2026-11-01  income  300,000원  용돈  월급  
261101-2  2026-11-01  expense  5,000원  식비  점심  
```

### M. 오류 처리 (스택트레이스 없음, 종료 코드)

`errors.py`의 `handle_errors`(9–31줄)가 오류를 잡아, `Traceback` 없이 짧은 메시지와 힌트를 보여 줍니다. 파일 오류는 2, 입력 오류는 1입니다. 입력 오류 메시지에 파이썬 기본 영어 문구가 섞일 수 있지만, 스택트레이스는 아닙니다.

```bash
python3 -m budget_app --data-dir data/check import nofile.csv
echo $?
```

```
파일 오류: 'nofile.csv' 파일을 찾을 수 없습니다.
힌트: 파일 경로와 이름을 다시 확인하세요.
2
```

```bash
printf 'expense\n2026-11-20\nabc\n식비\n테스트\n\n' | python3 -m budget_app --data-dir data/check add
echo $?
```

```
수입/지출 (income/expense): 날짜 (YYYY-MM-DD): 금액: 입력 오류: invalid literal for int() with base 10: 'abc'
힌트: 날짜는 YYYY-MM-DD, 금액은 0보다 큰 숫자로 입력하세요.
1
```

---

## ▶️ 실행 방법

```bash
# 1. 저장소 받기
git clone https://github.com/datecoco/B2-1-budget-app.git
cd B2-1-budget-app

# 2. 도움말 보기
python3 -m budget_app --help

# 3. 거래 추가
python3 -m budget_app add

# 4. 테스트용 폴더를 따로 쓰고 싶을 때 (--data-dir은 명령어 앞에)
python3 -m budget_app --data-dir data/check list

# 5. 시연용 CSV 가져오기 (부분 성공 / 전체 취소)
python3 -m budget_app --data-dir data/check import sample.csv
python3 -m budget_app --data-dir data/check import sample.csv --atomic

```
