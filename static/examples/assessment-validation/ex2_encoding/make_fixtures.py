"""Write the SAME synthetic header text in 5 encodings. All values are invented."""
import codecs
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, "fixtures")
shutil.rmtree(FX, ignore_errors=True)
os.makedirs(FX)

TEXT = ("HTTP/1.1 200 OK\r\n"
        "Server: ExampleHTTPD/1.2.3\r\n"
        "Strict-Transport-Security: max-age=31536000\r\n")
variants = {
    "utf8": TEXT.encode("utf-8"),
    "utf8_bom": codecs.BOM_UTF8 + TEXT.encode("utf-8"),
    # Windows PowerShell 5.1 redirection (>) writes UTF-16LE with this BOM by default.
    "utf16le_bom": codecs.BOM_UTF16_LE + TEXT.encode("utf-16-le"),
    "utf16be_bom": codecs.BOM_UTF16_BE + TEXT.encode("utf-16-be"),
    "utf16le_nobom": TEXT.encode("utf-16-le"),
}
for name, data in variants.items():
    with open(os.path.join(FX, name + ".txt"), "wb") as f:
        f.write(data)
    print(f"{name}.txt {len(data)} bytes head={data[:4].hex()}")
