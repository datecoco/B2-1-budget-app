# 실제 명령줄 처리 함수(main)는 cli.py에 모아 둔다.
# 이렇게 분리하면 실행 시작점과 명령 처리 코드를 각각 깔끔하게 관리할 수 있다.
from budget_app.cli import main


# ``py -m budget_app``으로 실행했을 때만 아래 블록이 동작한다.
if __name__ == "__main__":
    # main()의 반환값(0: 성공, 0 이외: 오류)을 프로그램 종료 코드로 사용한다.
    raise SystemExit(main())
