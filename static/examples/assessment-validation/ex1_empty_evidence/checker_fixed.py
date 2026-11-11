"""FIXED version: a file with no usable lines is "nodata", not "ok".

Usage: python checker_fixed.py <case_dir>
Output: hsts=<present|absent|-> TAB status=<ok|nodata>
"""
import os
import sys

path = os.path.join(sys.argv[1], "headers.txt")
if not os.path.exists(path):
    print("hsts=-\tstatus=nodata")
    sys.exit(0)
lines = [l.strip() for l in open(path, encoding="utf-8") if l.strip()]
if not lines:  # FIX: file exists but holds nothing -> cannot judge
    print("hsts=-\tstatus=nodata")
    sys.exit(0)
hsts = "present" if any(l.lower().startswith("strict-transport-security:") for l in lines) else "absent"
print(f"hsts={hsts}\tstatus=ok")
