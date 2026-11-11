# 공개 재현 예제 2종 — 빈 증적, 인코딩

> 이 예제들은 **과거 오류 유형을 설명하려고 새로 작성한 예제**입니다.
> - 실제 업무에서 쓴 점검 코드를 복사하거나 변형하지 않았습니다.
> - 함수 구조, 출력 형식, 항목 이름도 과거 구현과 다릅니다.
> - 입력은 모두 합성 값입니다(`ExampleHTTPD/1.2.3` 등 가상의 값).
> - 기준으로 삼은 것은 공개된 일반 원칙("수집하지 못한 것은 판단하지 않는다")과 공개 문서의 인코딩 사양(UTF-8, UTF-16 BOM)뿐입니다.

## 환경과 재현 절차

- 실제 실행 환경: Python 3.11.0, Windows. 외부 패키지와 네트워크는 쓰지 않습니다.
- 재현 순서:
  1. 이 폴더(`public-example`)로 이동합니다.
  2. `python -I run_examples.py`를 실행합니다.
  3. 실행 스크립트가 다음을 순서대로 합니다.
     - 각 예제의 `make_fixtures.py`로 합성 입력을 새로 만듭니다.
     - 오류판(`checker_buggy.py`)과 수정판(`checker_fixed.py`)을 사례마다 실행합니다.
     - 결과를 `expected.tsv`와 비교합니다.
     - 비교 결과를 `results/<예제>_result.txt`에 저장합니다.
  4. 종료코드는 수정판이 모든 사례에서 기대값과 같으면 0, 하나라도 다르면 1입니다.
- 개별 실행도 할 수 있습니다.
  - 예제 1: `python -I ex1_empty_evidence/checker_fixed.py ex1_empty_evidence/fixtures/empty`
  - 예제 2: `python -I ex2_encoding/checker_buggy.py ex2_encoding/fixtures/utf16le_bom.txt`
- 기대 출력(`expected.tsv`)은 코드를 처음 실행하기 전에 작성했습니다.

## 예제 1. 파일은 있는데 내용이 없다 (`ex1_empty_evidence`)

**오류 유형**
- 수집 결과 파일이 있기만 하면 상태를 `ok`로 기록합니다.
- 그러면 다음 단계는 빈 값을 실제 관측으로 읽습니다.
- 이 예제에서는 빈 파일이 "HSTS 헤더 없음(absent), 수집 정상(ok)"으로 나옵니다.
- 실제로는 아무것도 관측하지 못한 상태입니다.
- 항목에 따라 같은 오류가 거짓 양호(예: "디렉터리 목록 문자열 없음 → 양호")로도, 거짓 취약으로도 이어집니다.

**합성 입력** (`make_fixtures.py`가 생성)

| 사례 | headers.txt 내용 |
|---|---|
| good | 상태줄과 `Strict-Transport-Security: max-age=31536000` |
| bad | 상태줄과 `Server: ExampleHTTPD/1.2.3` |
| empty | 0바이트 파일 |
| blank | 공백과 줄바꿈만 있는 파일 |
| missing | 파일 없음 |

**수정 내용**: 공백을 뺀 유효한 줄이 하나도 없으면 `nodata`를 반환합니다(`checker_fixed.py`).

**실제 실행 결과** (집필 측에서 2026-11-11 재실행. 결과 파일은 해당 재실행판, `results/ex1_empty_evidence_result.txt`)

| 사례 | 기대 | 오류판 출력 | 수정판 출력 | 오류판 비교 | 수정판 비교 |
|---|---|---|---|---|---|
| good | present, ok | present, ok | present, ok | 일치 | 일치 |
| bad | absent, ok | absent, ok | absent, ok | 일치 | 일치 |
| empty | -, nodata | **absent, ok** | -, nodata | **불일치** | 일치 |
| blank | -, nodata | **absent, ok** | -, nodata | **불일치** | 일치 |
| missing | -, nodata | -, nodata | -, nodata | 일치 | 일치 |

- 각 checker의 종료코드는 모든 사례에서 0입니다.
- 요약
  - 오류판: 5건 중 2건이 기대와 다름
  - 수정판: 5건 중 0건이 기대와 다름
- 회귀 확인: good과 bad의 결과는 수정 전후가 같습니다.

## 예제 2. 같은 내용, 다른 인코딩 (`ex2_encoding`)

**오류 유형**
- 수집 도구가 텍스트를 UTF-16으로 저장했습니다. 예를 들어 Windows PowerShell 5.1의 `>` 리다이렉트는 기본값이 UTF-16LE입니다.
- 파서는 UTF-8로, 오류를 무시하는 모드로 읽었습니다.
- 그래서 글자 사이에 NUL 바이트가 끼어 문자열 매칭이 조용히 실패합니다.
- 오류 메시지는 나오지 않고 "없음"만 남습니다.

**합성 입력**: 똑같은 세 줄(상태줄, `Server`, `Strict-Transport-Security`)을 다섯 가지 인코딩으로 저장했습니다.

| 파일 | 크기(실측) | 앞 4바이트(실측) |
|---|---|---|
| utf8.txt | 90 | 48545450 |
| utf8_bom.txt | 93 | efbbbf48 |
| utf16le_bom.txt | 182 | fffe4800 |
| utf16be_bom.txt | 182 | feff0048 |
| utf16le_nobom.txt | 180 | 48005400 |

**수정 내용** (`checker_fixed.py`)
1. 파일을 바이트로 읽습니다.
2. BOM이 있으면 그것으로 UTF-8, UTF-16LE, UTF-16BE를 판별합니다.
3. BOM이 없는데 NUL 바이트 비율이 15%를 넘으면 UTF-16으로 보고, NUL 위치로 바이트 순서를 추정합니다.
4. 그 밖에는 UTF-8 엄격 모드로 읽고, 실패하면 관대 모드로 읽습니다.
5. 어떤 디코더를 썼는지 출력에 남깁니다.

**실제 실행 결과** (집필 측에서 2026-11-11 재실행. 결과 파일은 해당 재실행판, `results/ex2_encoding_result.txt`)

| 파일 | 기대 | 오류판 | 수정판(사용 디코더) | 오류판 비교 | 수정판 비교 |
|---|---|---|---|---|---|
| utf8 | present | present | present (utf-8) | 일치 | 일치 |
| utf8_bom | present | present | present (utf-8-sig) | 일치 | 일치 |
| utf16le_bom | present | **absent** | present (utf-16-le, BOM) | **불일치** | 일치 |
| utf16be_bom | present | **absent** | present (utf-16-be, BOM) | **불일치** | 일치 |
| utf16le_nobom | present | **absent** | present (utf-16-le, 추정) | **불일치** | 일치 |

- 각 checker의 종료코드는 모든 사례에서 0입니다.
- 요약
  - 오류판: 5건 중 3건이 기대와 다름
  - 수정판: 5건 중 0건이 기대와 다름
- 전체 실행 종료코드: 0 (`OVERALL PASS`)

## 이 예제가 보여 주지 않는 것

- NUL 비율 추정은 휴리스틱입니다. 짧은 파일이나 한글 위주의 BOM 없는 UTF-16에서는 틀릴 수 있습니다. 이 예제에는 그런 사례가 없습니다.
- 예제 2의 오류판은 UTF-8 BOM 파일을 우연히 통과했습니다. 검색어가 첫 줄에 있지 않았기 때문입니다. 첫 줄 매칭이라면 실패할 수 있습니다.
- 실제 서비스나 서버에는 실행하지 않았습니다. 모든 결과는 위 합성 입력에 대한 것입니다. 실제 업무에서 얼마나 개선됐는지를 나타내는 수치가 아닙니다.
- 운영 교훈은 두 가지입니다.
  - 수집 쪽에서 인코딩을 명시합니다.
  - 파서 쪽에서도 방어합니다.
  - 이 예제는 파서 쪽만 보여 줍니다.
