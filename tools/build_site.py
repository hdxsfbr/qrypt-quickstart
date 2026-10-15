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


NOBREAK_MAX = 32  # longer tokens may still wrap, so they never overflow a 390 px screen


def nobreak(m):
    """Keep a short file/path token (e.g. agent-sandbox/, QRYPT-ISOLATED.txt) on one line. Markup only."""
    tok = m.group(0)
    return f'<span class="nb">{tok}</span>' if len(tok) <= NOBREAK_MAX else tok


def nobreak_inline(m):
    body = m.group(1)
    if "<" in body:
        return m.group(0)
    return "<code>" + re.sub(r"\S+", lambda t: nobreak(t) if re.search(r"\w[-/]|[-/]\w", t.group(0)) else t.group(0), body) + "</code>"


def highlight_block(match):
    attrs, lang, code = match.group(1), match.group(2), match.group(3)
    source = html.unescape(code)
    lexer = get_lexer_by_name(LEXERS[lang])
    out = highlight(source, lexer, HtmlFormatter(nowrap=True))
    # Pygments maps unknown/"Text" tokens to no class: keep them as-is.
    if lang == "text":  # prose prompts: keep each URL unbroken (markup only; copied text is unchanged)
        out = re.sub(r"https?://[^\s<]+", lambda m: f'<span class="url">{m.group(0)}</span>', out)
        out = re.sub(r"(?<![\w/.~>-])[\w.~/-]*\w[-/][\w.~/-]*\w(?![^<]*</span>)", nobreak, out)
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
    text = re.sub(r"<code>(.*?)</code>", nobreak_inline, text, flags=re.S)  # inline code only (blocks carry attributes)
    return BLOCK.sub(highlight_block, text)


(root / "site/highlight.css").write_text(theme_css())


def inline_css(html):
    # Inline both stylesheets: saves two render-blocking requests on mobile.
    for css in ("style.css", "highlight.css"):
        tag = f'<link rel="stylesheet" href="/{css}">'
        body = (root / "site" / css).read_text().strip()
        html = html.replace(tag, f"<style>{body}</style>")
    return html


# ---- Docs shell (non-functional look-alike of docs.qrypt.com; see docs/design/NOTES.md)
REAL = "https://docs.qrypt.com"
OURS = [("/", "Quickstart", [("#h-token", "Get a token"), ("#h-env", "Save it in .env"),
                             ("#h-run", "Run the snippet"), ("#h-prod", "For production"), ("#h-trip", "Common pitfalls"),
                             ("#h-agent", "AI coding agents")]),
        ("/troubleshooting", "Troubleshooting", [("#codes", "HTTP status codes"),
                                                 ("#mistakes", "Common mistakes"),
                                                 ("#env", "Environment issues"),
                                                 ("#agent", "AI agent modes"),
                                                 ("#codex-bwrap", "Codex sandbox error"),
                                                 ("#proxy", "Proxy and TLS")])]
THEIRS = [("Quantum Entropy reference", "/eaas/"), ("RNG Tools", "/eaas/rngd/"),
          ("Qseed", "/eaas/pkcs11/"), ("DQKD Key Generation", "/sdk/"),
          ("FAQs", "/faqs/")]


def shell_top(path):
    items = []
    for href, label, kids in OURS:
        on = href == path
        cur = ' aria-current="page"' if on else ""
        sub = "".join(f'<li><a href="{href if not on else ""}{a}">{l}</a></li>'
                      for a, l in kids)
        items.append(f'<li{" class=on" if on else ""}><a href="{href}"{cur}>'
                     f'{label}</a><ul>{sub}</ul></li>')
    ext = "".join(f'<li><a class="ext" href="{REAL}{h}" rel="noopener">{l}'
                  f'<span class="sr"> (official Qrypt docs)</span></a></li>'
                  for l, h in THEIRS)
    return ('<a class="skip" href="#main">Skip to content</a>'
            '<p class="unoff" role="note">Unofficial prototype. Not affiliated '
            'with or endorsed by Qrypt.</p>'
            '<div class="wrap"><header class="top"><a class="mark" href="/">'
            '<b>Qrypt</b> Docs <small>quickstart prototype</small></a>'
            '<button class="menu" aria-controls="sidebar" aria-expanded="false">'
            'Menu</button></header>'
            '<nav id="sidebar" aria-label="Documentation"><ul class="topics">'
            + "".join(items) + '</ul><p class="grp">Official Qrypt docs</p>'
            '<ul class="topics">' + ext + '</ul>'
            '<p class="grp"><a href="/llms.txt">llms.txt</a></p></nav>'
            '<main id="main">')


BOTTOM = ('</main><footer class="foot"><p>Unofficial prototype built on the '
          'public API docs; not a Qrypt product and not endorsed by Qrypt. '
          'API reference: <a href="https://docs.qrypt.com/eaas/">docs.qrypt.com'
          '/eaas</a>. No analytics or cookies.</p></footer></div>')


for name in ("index.tmpl.html", "troubleshooting.tmpl.html"):
    src = root / "site-src" / name
    if src.exists():
        out_name = name.replace(".tmpl", "")
        path = "/" if out_name == "index.html" else "/" + out_name[:-5]
        text = src.read_text().replace("{{TOP}}", shell_top(path))
        page = inline_css(render(text.replace("{{BOTTOM}}", BOTTOM)))
        (root / "site" / out_name).write_text(page)

txt = (root / "site-src/llms.tmpl.txt").read_text()
for marker, path in SNIPPETS.items():
    txt = txt.replace(marker, path.read_text())
(root / "site/llms.txt").write_text(txt)

# ---- Starter archive: exact copies of repo files, deterministic bytes (CI diffs site/).
STARTER = ["AGENTS.md", "Makefile", ".env.example",
           "quickstart/python/quickstart.py", "quickstart/python/requirements.txt",
           "quickstart/node/quickstart.mjs", "mock/server.py", "mock/run_cases.sh",
           "agent-sandbox/Dockerfile", "agent-sandbox/README.md", "agent-sandbox/run.sh",
           "agent-sandbox/verify.sh", "agent-sandbox/test-isolation.sh"]


def build_starter():
    import os
    import zipfile
    out = root / "site/qrypt-quickstart-starter.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in STARTER:
            src = root / rel
            info = zipfile.ZipInfo("qrypt-quickstart/" + rel, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if os.access(src, os.X_OK) else 0o644
            info.external_attr = (0o100000 | mode) << 16
            z.writestr(info, src.read_bytes())


build_starter()
