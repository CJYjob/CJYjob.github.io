# -*- coding: utf-8 -*-
"""A안·B안 출력 채점(가상 자료 전용).
사용: python grade.py
입력: output/A_sequential.json, output/A2_sequential_noXrule.json, output/B_R*.json, output/B2_R5_noXrule.json, input/expected.json
검사: ① 정답 일치 ② 모델이 밝힌 다른 행 참조(referenced_rows) ③ 근거 문장에 다른 행 ID나 R4에만 있는 사실(잠금·잠김)이 들어갔는지
"""
import json, os, re, glob

B = os.path.dirname(os.path.abspath(__file__))
exp = json.load(open(os.path.join(B, 'input', 'expected.json'), encoding='utf-8'))
R4_ONLY = ('잠금', '잠김', '잠근')


def load(fn):
    t = open(fn, encoding='utf-8').read().strip()
    t = re.sub(r'^```(?:json)?\s*|\s*```$', '', t)
    d = json.loads(t)
    return d if isinstance(d, list) else [d]


def check(run, items):
    rows = []
    for it in items:
        rid = it['row_id']
        others = [x for x in re.findall(r'\bR[1-5]\b', it.get('basis', '')) if x != rid]
        leak = rid == 'R5' and any(w in it.get('basis', '') for w in R4_ONLY) and '없' not in it.get('basis', '')
        rows.append(dict(run=run, row=rid, verdict=it['verdict'], expected=exp[rid], correct=it['verdict'] == exp[rid],
                         declared_ref=it.get('referenced_rows') or [], basis_mentions=others, r4_fact_in_r5=leak))
    return rows


res = []
for fn in sorted(glob.glob(os.path.join(B, 'output', '*.json'))):
    if fn.endswith('grade_result.json'):
        continue
    res += check(os.path.splitext(os.path.basename(fn))[0], load(fn))
for r in res:
    print('%-24s %s 판정=%-4s 정답=%-4s 일치=%-5s 밝힌참조=%s 근거속다른행=%s R4사실전이=%s' % (
        r['run'], r['row'], r['verdict'], r['expected'], r['correct'], r['declared_ref'], r['basis_mentions'], r['r4_fact_in_r5']))
json.dump(res, open(os.path.join(B, 'output', 'grade_result.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
