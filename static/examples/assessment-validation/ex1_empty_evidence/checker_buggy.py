"""BUGGY version: treats "file exists" as "collected OK".

Usage: python checker_buggy.py <case_dir>
Output: hsts=<present|absent|-> TAB status=<ok|nodata>
"""
import os
import sys

path = os.path.join(sys.argv[1], "headers.txt")
if not os.path.exists(path):
    print("hsts=-\tstatus=nodata")
    sys.exit(0)
text = open(path, encoding="utf-8").read()
hsts = "present" if "strict-transport-security:" in text.lower() else "absent"
print(f"hsts={hsts}\tstatus=ok")  # BUG: an empty file is still reported as ok
