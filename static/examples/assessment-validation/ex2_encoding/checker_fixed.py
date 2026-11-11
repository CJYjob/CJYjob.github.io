"""FIXED version: read bytes, detect the encoding, then match.

Order: BOM (UTF-8 / UTF-16LE / UTF-16BE) -> NUL-ratio guess for BOM-less
UTF-16 -> strict UTF-8 -> lenient UTF-8. Prints which decoder was used.
Usage: python checker_fixed.py <file>
"""
import codecs
import sys


def decode(data):
    if data.startswith(codecs.BOM_UTF8):
        return data[3:].decode("utf-8", "replace"), "utf-8-sig"
    if data.startswith(codecs.BOM_UTF16_LE):
        return data[2:].decode("utf-16-le", "replace"), "utf-16-le(bom)"
    if data.startswith(codecs.BOM_UTF16_BE):
        return data[2:].decode("utf-16-be", "replace"), "utf-16-be(bom)"
    if data and data.count(0) / len(data) > 0.15:
        odd_nul = data[1::2].count(0)
        even_nul = data[0::2].count(0)
        enc = "utf-16-le" if odd_nul >= even_nul else "utf-16-be"
        return data.decode(enc, "replace"), enc + "(guess)"
    try:
        return data.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return data.decode("utf-8", "replace"), "utf-8(lenient)"


data = open(sys.argv[1], "rb").read()
text, used = decode(data)
lines = [l.strip() for l in text.splitlines() if l.strip()]
hsts = "present" if any(l.lower().startswith("strict-transport-security:") for l in lines) else "absent"
print(f"hsts={hsts}\tdecoder={used}")
