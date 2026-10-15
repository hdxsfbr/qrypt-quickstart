#!/usr/bin/env python3
"""Fail CI if the built site links to a dead outbound URL.

Checks every http(s) href in site/*.html and absolute URLs in site/llms.txt.
Fails on HTTP 4xx.

SPA caveat: hosts like portal.qrypt.com always return HTTP 200 for the shell,
even for missing routes (e.g. /register shows an in-app 404). For those hosts
we only allow the known-good routes below; any other path fails even on 200.
"""
from __future__ import annotations

import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# Hosts that serve an SPA shell (HTTP 200 for every path). Only these paths
# are accepted as outbound links; anything else is treated as a dead SPA route.
# Verified with a headless browser on 2026-10-15:
#   /register              -> in-app 404
#   /signup                -> "contact sales" (no form)
#   /trial-signup          -> redirects to /trial (signup form)
#   /trial-signup-entropy  -> redirects to /trial (signup form)  <- preferred
#   /trial                 -> signup form
#   /login                 -> login form
SPA_ALLOWLIST = {
    "portal.qrypt.com": {
        "/",
        "/signup",
        "/trial-signup",
        "/trial-signup-entropy",
        "/trial",
        "/login",
    },
}

SKIP_HOSTS = {"example.com", "proxy.example.com", "localhost", "host.docker.internal"}
HREF_RE = re.compile(r"""href\s*=\s*["']([^"']+)["']""", re.I)
URL_RE = re.compile(r"""https?://[^\s<>"'\)\]]+""")


def urls_from_site() -> set[str]:
    found: set[str] = set()
    # User-facing pages only. Skip site/agent-sandbox/*.md placeholders
    # like http://host.docker.internal:... which are not real links.
    targets = list(SITE.glob("*.html")) + [SITE / "llms.txt"]
    for path in targets:
        if not path.exists():
            continue
        text = path.read_text(errors="ignore")
        if path.suffix.lower() == ".html":
            candidates = HREF_RE.findall(text)
        else:
            candidates = [u.rstrip(".,);") for u in URL_RE.findall(text)]
        for href in candidates:
            if not href.startswith(("http://", "https://")):
                continue
            found.add(href.split("#", 1)[0])
    return found


def check(url: str) -> str | None:
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower()
    path = parsed.path or "/"
    if host in SKIP_HOSTS or host.endswith(".example.com"):
        return None  # caller skips; kept for safety
    if host == "api-eus.qrypt.com":
        return None
    if host in SPA_ALLOWLIST:
        allowed = SPA_ALLOWLIST[host]
        norm = path.rstrip("/") or "/"
        allowed_norm = {p.rstrip("/") or "/" for p in allowed}
        if norm not in allowed_norm:
            return (
                f"SPA host {host} path {path!r} is not in the known-good "
                f"allowlist {sorted(allowed)}. (SPAs return HTTP 200 even "
                f"for missing pages, so status alone is not enough.)"
            )
    req = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "qrypt-quickstart-link-check/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            code = resp.getcode()
            resp.read(1024)
    except urllib.error.HTTPError as e:
        if 400 <= e.code < 500:
            return f"HTTP {e.code} for {url}"
        print(f"WARN: HTTP {e.code} for {url} (5xx, not failing)", file=sys.stderr)
        return None
    except Exception as e:
        return f"request failed for {url}: {e}"
    if 400 <= code < 500:
        return f"HTTP {code} for {url}"
    return None


def main() -> int:
    urls = sorted(urls_from_site())
    if not urls:
        print("No outbound URLs found in site/", file=sys.stderr)
        return 1
    errors = []
    checked = 0
    for url in urls:
        parsed = urllib.parse.urlparse(url)
        host = (parsed.hostname or "").lower()
        if host in SKIP_HOSTS or host.endswith(".example.com") or host == "api-eus.qrypt.com":
            print(f"skip  {url}")
            continue
        checked += 1
        err = check(url)
        if err:
            print(f"FAIL  {url}: {err}")
            errors.append(err)
        else:
            print(f"ok    {url}")
    print(f"Checked {checked} outbound URLs; {len(errors)} failure(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
