#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공개 독립 예제 B — 미지원 장비를 '항목별 판정'과 섞지 않고 '장비 단위'로 고지하는 사례.
※ 이것은 '지원 범위 표시를 개선하는 새 예제'다. 과거 산출물에서 전후 수정이 확인되지 않았으므로
   과거 결함의 재현이 아니라, 지원 범위 고지 방식을 개선한 신규 설계로 제시한다.

핵심 구분(설계 의도):
  - 오분류(misclassification)      : 지원 장비를 미지원으로 잘못 보는 것 → 결함
  - 지원 범위 고지 부족(opaque)    : 미지원인데 '항목별 수동진단'으로 흩어 표기 → 개선 대상(결함 아님, 가독성 문제)
  - 안전한 판정 보류(safe hold)    : 미지원 장비를 장비 단위 '지원범위 외(수동확인)' 1건으로 고지 → 권장

사용법: python classify.py <mode: legacy|improved> <config.txt> [config2.txt ...]
  legacy   : 미지원 장비도 항목별로 N-01..N-03 전부 '수동진단' 으로 흩어 출력
  improved : 미지원 장비는 장비 단위 '지원범위 외(수동확인)' 1건으로 고지, 사유 포함
입력 config 는 합성 텍스트. 공개 가능한 항목 코드(N-01..N-03) 형식만 가상 사용.
"""
import sys, json, re

try:
    sys.stdout.reconfigure(encoding="utf-8")  # 콘솔 코드페이지와 무관하게 UTF-8 출력
except Exception:
    pass

ITEMS = ["ITEM-01", "ITEM-02", "ITEM-03"]  # 가상의 공개 항목 집합

def is_supported(text):
    # 지원 파서가 아는 문법 키워드가 있을 때만 True. (지원 여부 판단이지 벤더 낙인이 아님)
    return bool(re.search(r'(?mi)^\s*(enable secret|line vty|security passwords)', text))

def analyze_supported(text):
    out = {}
    out["ITEM-01"] = "양호" if re.search(r'(?mi)^\s*enable secret', text) else "취약"
    out["ITEM-02"] = "양호" if re.search(r'(?mi)^\s*security passwords min-length', text) else "취약"
    out["ITEM-03"] = "양호" if re.search(r'(?mi)^\s*service password-encryption', text) else "취약"
    return out

def run(mode, paths):
    report = []
    for p in paths:
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as e:
            report.append({"device": p, "collection": "수집실패", "reason": str(e)})
            continue
        if is_supported(text):
            report.append({"device": p, "support": "지원", "items": analyze_supported(text)})
        else:
            if mode == "legacy":
                # 미지원인데 항목별로 흩어 '수동진단' → 지원범위 문제가 항목 결과에 묻힘
                report.append({"device": p, "items": {k: "수동진단" for k in ITEMS}})
            else:
                # 장비 단위 1건으로 지원범위 외 고지(안전한 판정 보류)
                report.append({"device": p, "support": "지원범위 외",
                               "judgement": "수동확인", "items": {},
                               "reason": "예제 파서가 인식하는 문법을 확인하지 못함 — 제품 식별과 수동 확인 필요"})
    return report

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python classify.py <legacy|improved> <config...>"); sys.exit(3)
    mode = sys.argv[1]; paths = sys.argv[2:]
    rep = run(mode, paths)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    # 종료코드: 미지원/수집실패가 하나라도 있으면 2(검토 필요), 전부 지원이면 0
    flagged = any(("support" in r and r.get("support") != "지원") or "collection" in r for r in rep)
    sys.exit(2 if flagged else 0)
