---
title: "빈 증적과 인코딩: 실행 성공 뒤의 오류를 재현하다"
date: 2026-11-11
lastmod: 2026-11-11
draft: false
description: "합성 입력 10개로 오류판과 수정판을 비교한다. 빈 파일과 UTF-16을 정상 수집으로 오해하는 경로를 확인하는 독립 예제."
categories: ["security", "ai", "development"]
ShowToc: true
---

## 과거 사건과 공개 실험을 구분한다

[대표 글](/portfolio/security/ai-assessment-workflow/)에서 다룬 실제 작업에서는 빈 증적의 처리 오류와 UTF-16 수집 결과를 파서가 제대로 읽지 못한 문제가 있었다. 여기서는 회사 코드를 공개하지 않고 같은 오류 유형을 설명하는 프로그램을 새로 작성했다. 아래 결과는 이 합성 예제의 시험값이다.

[코드·입력·실행 결과 ZIP](/examples/assessment-validation.zip)을 내려받아 압축을 풀고 실행한다. Python 표준 라이브러리만 사용하며 네트워크나 실제 서버에 접근하지 않는다.

```text
python -I run_examples.py
```

## 1. 빈 파일을 유효한 관측으로 처리하는 문제

오류판은 파일이 있으면 수집 상태를 `ok`로 기록한다. 빈 파일에도 헤더가 없다는 결과가 나오지만 실제로는 아무것도 관측하지 못했다. 수정판은 유효한 줄이 없거나 파일이 없으면 `nodata`를 반환한다.

| 합성 입력 | 기대 결과 | 오류판 | 수정판 |
| --- | --- | --- | --- |
| 헤더가 있는 정상 응답 | present, ok | 일치 | 일치 |
| 헤더가 없는 유효 응답 | absent, ok | 일치 | 일치 |
| 0바이트 | -, nodata | absent, ok | 일치 |
| 공백·줄바꿈뿐 | -, nodata | absent, ok | 일치 |
| 파일 없음 | -, nodata | 일치 | 일치 |

오류판의 불일치는 5개 중 2개, 수정판은 0개다. 정상 응답과 헤더가 없는 유효 응답의 결과는 유지된다. 수집 실패와 확인 결과를 같은 상태로 만들지 않는 것이 수정의 목적이다.

## 2. 같은 텍스트가 다른 바이트로 저장되는 문제

Windows PowerShell 5.1의 리다이렉트와 PowerShell 6 이상의 기본 출력 인코딩은 다르다. [Microsoft 인코딩 문서](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-5.1)를 기준으로 수집·분석 도구가 어떤 바이트를 주고받는지 확인해야 한다.

이 예제는 동일한 HTTP 형태의 가상 텍스트를 UTF-8, UTF-8 BOM, UTF-16LE BOM, UTF-16BE BOM, UTF-16LE BOM 없음으로 저장한다. UTF-8로 오류를 무시하며 읽는 오류판은 UTF-16 세 파일에서 검색어를 찾지 못한다. 수정판은 BOM과 바이트 분포로 디코더를 고르고 사용한 디코더를 출력한다.

| 인코딩 | 오류판의 검색 결과 | 수정판의 검색 결과 |
| --- | --- | --- |
| UTF-8 / UTF-8 BOM | present | present |
| UTF-16LE BOM | absent | present |
| UTF-16BE BOM | absent | present |
| UTF-16LE BOM 없음 | absent | present |

오류판의 불일치는 5개 중 3개, 수정판은 0개다. [Python codecs 문서](https://docs.python.org/3/library/codecs.html)의 엄격한 디코딩과 오류 처리 방식을 함께 참고할 수 있다.

## 결과가 보장하는 범위

이 프로그램이 모든 인코딩을 알아내는 것은 아니다. BOM 없는 UTF-16 추정은 짧은 입력과 한글 중심 입력에서 추가 검증이 필요하다. 모르는 인코딩을 관대한 디코딩으로 읽으면 오류를 숨길 수 있으므로 운영용 수집에서는 인코딩을 명시하고, 판별에 실패한 입력을 별도로 남기는 편이 낫다.

검증 프로그램은 수정판이 기대값과 다르면 실패로 종료한다. 개별 파서가 종료코드 0을 반환하는 것과 결과가 기대값에 맞는 것은 다른 조건이다.

- [시험 설명 원문](/examples/assessment-validation/EXAMPLES.md)
- [빈 증적 실제 실행 출력](/examples/assessment-validation/results/ex1_empty_evidence_result.txt)
- [인코딩 실제 실행 출력](/examples/assessment-validation/results/ex2_encoding_result.txt)
