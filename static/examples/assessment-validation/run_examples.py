"""Run both examples.

Regenerates fixtures, runs the buggy and fixed checkers on every case,
compares with expected.tsv and writes results/<example>_result.txt.
Exit code: 0 if every FIXED output matches expected, otherwise 1.
The BUGGY version is expected to mismatch on some cases; that is the point.
"""
import datetime
import os
import platform
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")
os.makedirs(OUT, exist_ok=True)
PY = sys.executable


def run(args):
    p = subprocess.run([PY, "-I"] + args, capture_output=True, text=True, encoding="utf-8")
    return p.stdout.strip(), p.returncode


def load_expected(path):
    exp = {}
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        key, val = line.rstrip("\n").split("\t", 1)
        exp[key] = val
    return exp


def example(name, target_of, compare_first_field_only):
    d = os.path.join(HERE, name)
    gen_out, gen_rc = run([os.path.join(d, "make_fixtures.py")])
    exp = load_expected(os.path.join(d, "expected.tsv"))
    rows, fixed_bad, buggy_bad = [], 0, 0
    for case, want in exp.items():
        target = target_of(d, case)
        res = {}
        for ver in ("buggy", "fixed"):
            out, rc = run([os.path.join(d, f"checker_{ver}.py"), target])
            got = out.split("\t")[0] if compare_first_field_only else out
            res[ver] = (out, rc, "MATCH" if (got == want and rc == 0) else "DIFF")
        fixed_bad += res["fixed"][2] != "MATCH"
        buggy_bad += res["buggy"][2] != "MATCH"
        rows.append((case, want, res))

    lines = [
        f"# {name} - actual run output",
        f"# time={datetime.datetime.now().isoformat(timespec='seconds')}",
        f"# python={platform.python_version()} os={platform.platform()}",
        f"# make_fixtures exit={gen_rc}",
    ]
    lines += ["#   " + l for l in gen_out.splitlines()]
    lines += ["", "case\texpected\tbuggy_out\tbuggy_exit\tbuggy_vs_expected\tfixed_out\tfixed_exit\tfixed_vs_expected"]
    for case, want, r in rows:
        lines.append("\t".join([
            case, want,
            r["buggy"][0], str(r["buggy"][1]), r["buggy"][2],
            r["fixed"][0], str(r["fixed"][1]), r["fixed"][2],
        ]))
    lines += ["", f"SUMMARY buggy_mismatch={buggy_bad}/{len(rows)} fixed_mismatch={fixed_bad}/{len(rows)}"]
    text = "\n".join(lines) + "\n"
    with open(os.path.join(OUT, f"{name}_result.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    return fixed_bad


fails = example("ex1_empty_evidence", lambda d, c: os.path.join(d, "fixtures", c), False)
fails += example("ex2_encoding", lambda d, c: os.path.join(d, "fixtures", c + ".txt"), True)
print("OVERALL " + ("PASS" if fails == 0 else "FAIL"))
sys.exit(0 if fails == 0 else 1)
