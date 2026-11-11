# 미지원 입력을 장비 단위로 고지하는 새 예제

회사 원본 코드와 설정을 사용하지 않았다. 과거 수정의 재현이 아니라 지원 범위 표시를 개선하는 새로운 예제다. 실제 제품 식별기나 KISA 판정 도구가 아니다. ITEM-01 등은 가상 항목이다.

```text
python -I classify.py legacy samples/supported.cfg samples/unsupported.cfg
python -I classify.py improved samples/supported.cfg samples/unsupported.cfg
python -I classify.py improved samples/missing.cfg
```

기존 표현은 미지원 입력도 항목별 수동진단으로 출력하고 종료 0, 개선 표현은 장비 단위 보류·빈 항목 목록·종료 2, 읽기 실패는 수집 실패·종료 2다. `verification.json`은 현재 코드로 재실행한 결과다.

키워드 미검출만으로 실제 벤더를 확정하지 않으며 제품 식별과 수동 확인이 필요하다. 이 예제만으로 실제 장비를 진단하지 않는다.
