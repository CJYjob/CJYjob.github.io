"""BUGGY version: always reads as UTF-8 with errors="replace".

UTF-16 text then carries NUL bytes between letters, so matching fails
without any error message.
Usage: python checker_buggy.py <file>
"""
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
lines = [l.strip() for l in text.splitlines() if l.strip()]
hsts = "present" if any("strict-transport-security:" in l.lower() for l in lines) else "absent"
print(f"hsts={hsts}")
