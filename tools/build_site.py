"""Fill site/*.tmpl.html with the real snippet files so docs never drift from code. Run: make site"""
import html, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
subs = {"{{PY}}": html.escape((root/"quickstart/python/quickstart.py").read_text()),
        "{{JS}}": html.escape((root/"quickstart/node/quickstart.mjs").read_text())}
for t in (root/"site").glob("*.tmpl.html"):
    out = t.read_text()
    for k, v in subs.items(): out = out.replace(k, v)
    (t.parent/t.name.replace(".tmpl", "")).write_text(out)
txt = (root/"site/llms.tmpl.txt").read_text()
for k, v in subs.items(): txt = txt.replace(k, html.unescape(v))
(root/"site/llms.txt").write_text(txt)
