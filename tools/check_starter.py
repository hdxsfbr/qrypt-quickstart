#!/usr/bin/env python3
"""CI: the starter zip must match the repo files byte for byte and hold no secrets."""
import pathlib
import re
import sys
import zipfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
src = (ROOT / "tools/build_site.py").read_text()
STARTER = eval(re.search(r"STARTER = (\[.*?\])", src, re.S).group(1))
z = zipfile.ZipFile(ROOT / "site/qrypt-quickstart-starter.zip")
names = z.namelist()
errors = []
want = ["qrypt-quickstart/" + r for r in STARTER]
if sorted(names) != sorted(want):
    errors.append(f"file list differs: {sorted(set(names) ^ set(want))}")
for n in names:
    base = n.rsplit("/", 1)[-1]
    if base.startswith(".env") and base != ".env.example":
        errors.append(f"secret-looking file in archive: {n}")
    data = z.read(n)
    rel = n.split("/", 1)[1]
    if (ROOT / rel).exists() and data != (ROOT / rel).read_bytes():
        errors.append(f"{rel} differs from the repo version")
    text = data.decode("utf-8", "replace")
    # Any QRYPT_API_KEY= assignment must be empty or an obvious placeholder.
    for m in re.finditer(r"QRYPT_API_KEY=([^\s\"'`]*)", text):
        val = m.group(1)
        if val and not re.fullmatch(r"(\.\.\.|<\w*|\$\{?\w+\}?|paste-your-token-here|mock-token-not-secret(\\n)?|should-never-enter|fake)", val):
            errors.append(f"{rel}: QRYPT_API_KEY has a non-placeholder value")
    if re.search(r"eyJ[A-Za-z0-9_-]{20,}", text):
        errors.append(f"{rel}: looks like a JWT/token")
if errors:
    sys.exit("starter archive check FAILED:\n- " + "\n- ".join(errors))
print(f"starter archive OK: {len(names)} files match the repo, no .env or token")
