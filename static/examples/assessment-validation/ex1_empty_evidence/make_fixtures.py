"""Create synthetic fixtures for example 1. All values are invented."""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, "fixtures")
shutil.rmtree(FX, ignore_errors=True)

cases = {
    "good": "HTTP/1.1 200 OK\nStrict-Transport-Security: max-age=31536000\n",
    "bad": "HTTP/1.1 200 OK\nServer: ExampleHTTPD/1.2.3\n",
    "empty": "",            # file exists, 0 bytes
    "blank": "\n   \n\n",   # file exists, whitespace only
    "missing": None,        # no file at all
}
for name, body in cases.items():
    d = os.path.join(FX, name)
    os.makedirs(d)
    if body is not None:
        with open(os.path.join(d, "headers.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
print("fixtures written: " + ", ".join(cases))
