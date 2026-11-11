"""Synthetic example; not the private research platform's implementation."""
import json
import statistics
from pathlib import Path

def evaluate(baseline, candidate):
    for key in ('revision', 'seconds', 'seed'):
        if baseline.get(key) != candidate.get(key):
            return 'REJECT_CONDITIONS'
    for row in (baseline, candidate):
        values = row.get('coverage')
        if not isinstance(values, list) or len(values) < 3:
            return 'HOLD_MISSING_DATA'
        if any(type(v) not in (int, float) or not (0 <= v < float('inf')) for v in values):
            return 'HOLD_INVALID_DATA'
    return 'PASS' if statistics.median(candidate['coverage']) > statistics.median(baseline['coverage']) else 'BLOCK'

if __name__ == '__main__':
    baseline = dict(revision='synthetic-v1', seconds=60, seed=7, coverage=[100, 110, 120])
    cases = [
        ('condition_mismatch', {**baseline, 'revision':'synthetic-v2'}, 'REJECT_CONDITIONS'),
        ('missing', {**baseline, 'coverage':[]}, 'HOLD_MISSING_DATA'),
        ('regression', {**baseline, 'coverage':[50, 60, 70]}, 'BLOCK'),
        ('improvement', {**baseline, 'coverage':[130, 140, 150]}, 'PASS'),
    ]
    results=[]
    for name, candidate, expected in cases:
        actual=evaluate(baseline,candidate)
        results.append(dict(case=name,expected=expected,actual=actual,passed=actual==expected))
    Path('results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print(json.dumps(results,indent=2))
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
