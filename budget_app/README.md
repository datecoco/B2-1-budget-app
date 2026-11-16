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
| `import` | CSV 파일에서 거래 가져오기 (잘못된 줄은 건너뜀) | `import my.csv` |
| `export` | 거래를 CSV로 내보내기 | `export out.csv --month 2026-11` |
| `category` | 카테고리 목록·추가·삭제 (사용 중인 분류는 삭제 차단) | `category add hobby` |

---

## 🛠 사용 기술

- Python 3 (표준 라이브러리만 사용)
- `argparse` : 명령어와 옵션 처리
- `dataclasses` : 거래 데이터 모양 정의
- `json` / `csv` : 파일 저장, 가져오기·내보내기
- `pathlib` / `os` : 파일 경로, 안전한 파일 교체

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
│   └── errors.py         # 오류 처리 데코레이터
├── data/                 # 저장 파일 (Git에 올리지 않음)
│   ├── transactions.jsonl
│   ├── categories.jsonl
│   └── budgets.jsonl
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
- **데코레이터** : 함수에 오류 처리를 덧씌우기
- **종료 코드** : 0 성공 / 1 입력 오류 / 2 파일 오류 / 130 사용자 중단

---

## 🔄 처리 흐름

```
명령어 입력 → argparse로 해석 → cli.py에서 명령어별 처리
          → repositories.py로 파일 읽기·쓰기 → 결과 출력
          (오류가 나면 errors.py가 받아서 안내 메시지 + 종료 코드)
```

---

## 🖥 실행 예시

```
$ python3 -m budget_app list
261116-1  2026-11-16  expense  9,000원  food  점심  #외식
261101-1  2026-11-01  income  300,000원  salary  용돈

$ python3 -m budget_app summary --month 2026-11
[2026-11 요약]
수입: 300,000원
지출: 9,000원
잔액: 291,000원
지출 TOP 3:
  1. food 9,000원

$ python3 -m budget_app budget --month 2026-11
[2026-11 예산]
예산: 200,000원
지출: 9,000원
사용률: 4.5%
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
```
