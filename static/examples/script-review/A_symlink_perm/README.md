# 심볼릭링크 권한 조회 — 합성 예제

회사의 실제 코드가 아닌 독립 예제다. 예제의 가상 권한 규칙은 운영용 보안 기준이 아니다.

`run_output.txt`는 최초 Windows/MSYS 환경의 결과로 링크 권한 차이가 재현되지 않았다. `linux-verification.txt`는 이후 WSL Ubuntu 20.04에서 새 임시 파일로 재검증한 결과다. 링크 자체 777을 읽는 오류판은 종료 1, 대상 640을 읽는 수정판은 종료 0, 없는 파일은 종료 2였다.

Linux에서 640 권한의 가상 파일을 만들고 링크를 만든 뒤 `bash check_perm.sh bad LINK`와 `bash check_perm.sh fixed LINK`로 비교한다. `samples/link.cnf`는 Windows 전달 과정에서 링크가 일반 파일로 바뀔 수 있으므로 재현 시 링크를 직접 생성해야 한다. 실제 설정 경로에 실행하지 않는다.
