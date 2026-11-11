#!/usr/bin/env bash
# 공개 독립 예제 A — 설정파일 권한 점검에서 심볼릭 링크 '자체' 권한과 '링크 대상' 권한을 혼동하는 사례.
# 합성 입력만 사용. 회사/고객 코드 미인용. KISA 류 "설정파일 권한 640 이하" 통념을 가상 재현.
#
# 사용법: ./check_perm.sh <mode: bad|fixed> <설정파일경로>
#   bad   : stat 로 경로 자체의 권한을 읽음(심볼릭 링크면 링크 권한 777 을 읽어 상시 '취약' 오탐)
#   fixed : stat -L 로 '링크 대상'의 실제 권한을 읽음
# 판정 기준(가상): 그룹/기타 쓰기 비트가 없고 8진 권한이 640 이하이면 '양호', 아니면 '취약'
set -u
mode="${1:-fixed}"; target="${2:-}"
[ -n "$target" ] || { echo "ERROR: 설정파일 경로 필요"; exit 3; }
[ -e "$target" ] || { echo "수동진단: 대상 파일 없음(수집 실패)"; exit 2; }

if [ "$mode" = "bad" ]; then
  perm=$(stat -c '%a' "$target" 2>/dev/null)      # 링크면 링크 자체 권한
else
  perm=$(stat -L -c '%a' "$target" 2>/dev/null)   # 링크 대상의 실제 권한
fi
[ -n "$perm" ] || { echo "수동진단: 권한 확인 불가(stat)"; exit 2; }

# 8진 → 그룹/기타 쓰기 비트 검사 + 640 이하 여부
owo=$(( 8#$perm & 8#022 ))                         # 그룹/기타 쓰기 비트
if [ "$owo" -eq 0 ] && [ "$(( 8#$perm ))" -le "$(( 8#640 ))" ]; then
  echo "양호: 권한 ${perm} (mode=${mode})"; exit 0
else
  echo "취약: 권한 ${perm} - 그룹/기타 접근 과다 (mode=${mode})"; exit 1
fi
