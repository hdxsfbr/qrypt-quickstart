"""Build site/ from site-src/ templates and the real snippet files (run: make site).

- {{PY}} / {{JS}} are filled from quickstart/ so docs never drift from code.
- Every <pre><code data-lang="..."> block is syntax-highlighted here with
  Pygments: static HTML spans, no client-side JS. Lines are wrapped in
  <span class="line"> so CSS can number them; the numbers are CSS-generated
  and are never part of the copied text (copy uses textContent).
- The theme is checked for WCAG AA (>= 4.5:1) on every token colour.
"""
import html
import pathlib
import re
import sys

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

root = pathlib.Path(__file__).resolve().parent.parent
SNIPPETS = {"{{PY}}": root / "quickstart/python/quickstart.py",
            "{{JS}}": root / "quickstart/node/quickstart.mjs"}
LEXERS = {"python": "python", "js": "javascript", "bash": "bash",
          "env": "bash", "json": "json", "text": "text"}
BG = "#0d1117"
# Token colours (GitHub-dark based, tuned so each is >= 4.5:1 on BG).
THEME = {"": "#e6edf3", "c": "#9ba7b4", "k": "#ff7b72", "kc": "#79c0ff",
         "kd": "#ff7b72", "kr": "#ff7b72", "ne": "#ffa657", "kn": "#ff7b72", "o": "#ff7b72", "ow": "#ff7b72",
         "s": "#a5d6ff", "s1": "#a5d6ff", "s2": "#a5d6ff", "sa": "#a5d6ff",
         "si": "#ffa657", "se": "#79c0ff", "sb": "#a5d6ff", "dl": "#a5d6ff",
         "m": "#79c0ff", "mi": "#79c0ff", "mf": "#79c0ff", "nb": "#ffa657",
         "bp": "#ffa657", "nf": "#d2a8ff", "fm": "#d2a8ff", "nc": "#f0883e",
         "nn": "#e6edf3", "nv": "#ffa657", "no": "#79c0ff", "nt": "#7ee787",
         "na": "#79c0ff", "p": "#e6edf3", "err": "#ffa198"}


def luminance(hex_colour):
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
           for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def theme_css():
    bad = {t: round(contrast(c, BG), 2) for t, c in THEME.items()
           if contrast(c, BG) < 4.5}
    if bad:
        sys.exit(f"Theme colours below WCAG AA on {BG}: {bad}")
    rules = [f".hl{{background:{BG};color:{THEME['']}}}"]
    rules += [f".hl .{t}{{color:{c}}}" for t, c in THEME.items() if t]
    rules.append(".hl .c,.hl .c1,.hl .cm,.hl .ch,.hl .cs{color:%s;"
                 "font-style:italic}" % THEME["c"])
    return "\n".join(rules) + "\n"


def highlight_block(match):
    attrs, lang, code = match.group(1), match.group(2), match.group(3)
    source = html.unescape(code)
    lexer = get_lexer_by_name(LEXERS[lang])
    out = highlight(source, lexer, HtmlFormatter(nowrap=True))
    # Pygments maps unknown/"Text" tokens to no class: keep them as-is.
    lines = out.rstrip("\n").split("\n")
    body = "\n".join(f'<span class="line">{line}</span>' for line in lines)
    if source.endswith("\n"):
        body += "\n"  # keep the file's final newline so copy is exact
    return f'<pre class="hl" tabindex="0"><code{attrs}>{body}</code></pre>'


BLOCK = re.compile(r'<pre><code([^>]*data-lang="([a-z]+)"[^>]*)>(.*?)</code></pre>',
                   re.S)


def render(text):
    for marker, path in SNIPPETS.items():
        text = text.replace(marker, html.escape(path.read_text()))
    return BLOCK.sub(highlight_block, text)


(root / "site/highlight.css").write_text(theme_css())


def inline_css(html):
    # Inline both stylesheets: saves two render-blocking requests on mobile.
    for css in ("style.css", "highlight.css"):
        tag = f'<link rel="stylesheet" href="/{css}">'
        body = (root / "site" / css).read_text().strip()
        html = html.replace(tag, f"<style>{body}</style>")
    return html


for name in ("index.tmpl.html", "troubleshooting.tmpl.html"):
    src = root / "site-src" / name
    if src.exists():
        out_name = name.replace(".tmpl", "")
        page = inline_css(render(src.read_text()))
        (root / "site" / out_name).write_text(page)

txt = (root / "site-src/llms.tmpl.txt").read_text()
for marker, path in SNIPPETS.items():
    txt = txt.replace(marker, path.read_text())
(root / "site/llms.txt").write_text(txt)
