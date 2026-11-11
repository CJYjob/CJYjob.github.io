# -*- coding: utf-8 -*-
"""가상 행으로 A안·B안 판정 프롬프트를 만든다(가상 자료 전용).
사용: python build_prompts.py
출력: prompts/A_sequential.txt, prompts/B_R1.txt ... prompts/B_R5.txt, prompts/manifest.json
"""
import json, os, hashlib

B = os.path.dirname(os.path.abspath(__file__))
crit = open(os.path.join(B, 'input', 'criteria.md'), encoding='utf-8').read()
rows = json.load(open(os.path.join(B, 'input', 'rows.json'), encoding='utf-8'))

RULE = ("당신은 취약점 점검 판정자입니다. 파일을 읽거나 도구를 쓰지 말고, 아래 글만 보고 답하세요.\n"
        "출력은 JSON만 쓰세요. 다른 설명은 쓰지 마세요.\n")
SCHEMA_ONE = ('형식: {"row_id": "...", "verdict": "양호|취약|수동진단", '
              '"basis": "판정 근거 한두 문장", "referenced_rows": ["판정에 쓴 다른 행 ID, 없으면 빈 배열"]}\n')


def row_text(r):
    return (f"### 행 {r['row_id']}\n- 대상: {r['host']}\n- 코드: {r['code']} {r['item']}\n"
            f"- 수집 결과:\n```\n{r['collected']}\n```\n- 담당자 답변: {r['answer'] or '(없음)'}\n"
            f"- 증적 설명: {r['evidence_note'] or '(없음)'}\n")


out = {}
# A안: 한 실행에 모든 행을 순서대로
a = (RULE + "아래 행들을 R1부터 순서대로 하나씩 판정하세요.\n"
     '형식: [{"row_id": ..., "verdict": ..., "basis": ..., "referenced_rows": [...]}, ...] (행 순서대로)\n\n'
     + crit + "\n\n## 판정할 행\n\n" + "\n".join(row_text(r) for r in rows))
out['A_sequential.txt'] = a
# B안: 행마다 그 행과 공개 기준만
for r in rows:
    out[f"B_{r['row_id']}.txt"] = RULE + SCHEMA_ONE + "\n" + crit + "\n\n## 판정할 행\n\n" + row_text(r)

os.makedirs(os.path.join(B, 'prompts'), exist_ok=True)
man = {}
for fn, t in out.items():
    open(os.path.join(B, 'prompts', fn), 'w', encoding='utf-8').write(t)
    ids = [r['row_id'] for r in rows if f"### 행 {r['row_id']}" in t]
    man[fn] = {'sha256': hashlib.sha256(t.encode('utf-8')).hexdigest()[:16], 'rows_in_prompt': ids}
json.dump(man, open(os.path.join(B, 'prompts', 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in man.items():
    print(k, v)
