"""Keyboard-only and 200%-zoom check of the live Qrypt quickstart site (Playwright + Chrome)."""
import sys
from playwright.sync_api import sync_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else "https://qrypt-quickstart.pages.dev"
out = []
def log(ok, msg): out.append(("PASS " if ok else "FAIL ") + msg)
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    for path in ["/", "/troubleshooting"]:
        # 200% zoom on a 1280x800 window == 640x400 CSS px at device scale 2
        for w, h, label in [(640, 400, "200% zoom"), (320, 256, "400% zoom / 320 px reflow")]:
            ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=2)
            pg = ctx.new_page(); pg.goto(BASE + path, wait_until="networkidle")
            r = pg.evaluate("""() => {const s=document.scrollingElement;
              const pres=[...document.querySelectorAll('pre')];
              const bad=pres.filter(e=>e.scrollWidth>e.clientWidth+1 && !(e.tabIndex>=0 || e.closest('[tabindex]')));
              const small=pres.filter(e=>parseFloat(getComputedStyle(e).fontSize)<12);
              return {hs:s.scrollWidth-s.clientWidth, pres:pres.length, bad:bad.length, small:small.length};}""")
            log(r["hs"] <= 1, f"{path} {label}: no horizontal page scroll (overflow {r['hs']} px)")
            log(r["bad"] == 0, f"{path} {label}: {r['pres']} code blocks; wide ones are keyboard-scrollable (unfocusable wide: {r['bad']})")
            log(r["small"] == 0, f"{path} {label}: code font >= 12 px (smaller: {r['small']})")
            ctx.close()
        ctx = b.new_context(viewport={"width": 1280, "height": 800}, permissions=["clipboard-read", "clipboard-write"])
        pg = ctx.new_page(); pg.goto(BASE + path, wait_until="networkidle")
        r = pg.evaluate("""() => {const c=[...document.querySelectorAll('button')].filter(x=>/copy/i.test(x.textContent));
            return {n:c.length, unl:c.filter(x=>!(x.getAttribute('aria-label')||'').trim()).length};}""")
        log(r["unl"] == 0, f"{path}: {r['n']} copy buttons, all with aria-label (missing: {r['unl']})")
        seen, nofocusring = [], 0
        for _ in range(250):
            pg.keyboard.press("Tab")
            info = pg.evaluate("""() => {const e=document.activeElement; if(!e||e===document.body) return null;
              const cs=getComputedStyle(e); const ring = cs.outlineStyle!=='none' && parseFloat(cs.outlineWidth)>0 || cs.boxShadow!=='none';
              return {tag:e.tagName, role:e.getAttribute('role')||'', label:(e.getAttribute('aria-label')||e.textContent||'').trim().slice(0,40), ring};}""")
            if not info: break
            key = (info["tag"], info["role"], info["label"])
            if seen and key == seen[0]: break
            seen.append(key); nofocusring += 0 if info["ring"] else 1
        log(len(seen) > 5 and seen[0][2].lower().startswith("skip"), f"{path}: Tab reaches {len(seen)} stops; first is '{seen[0][2] if seen else ''}'")
        log(nofocusring == 0, f"{path}: visible focus indicator on every Tab stop (without: {nofocusring})")
        if path == "/":
            tabs = [s for s in seen if s[1] == "tab"]; copies = [s for s in seen if "copy" in s[2].lower()]
            log(len(tabs) >= 1, f"/: language tab reachable by Tab ({len(tabs)} tab stop(s), roving tabindex)")
            log(len(copies) >= 3, f"/: copy buttons reachable by Tab ({len(copies)})")
            pg.focus("[role=tab][aria-selected=true]")
            before = pg.evaluate("document.activeElement.textContent.trim()")
            pg.keyboard.press("ArrowRight")
            after = pg.evaluate("[document.activeElement.textContent.trim(), document.activeElement.getAttribute('aria-selected')]")
            log(after[0] != before and after[1] == "true", f"/: ArrowRight moves from {before} tab to {after[0]} tab and selects it")
            pg.keyboard.press("Home"); home = pg.evaluate("document.activeElement.textContent.trim()")
            log(home == before, f"/: Home returns to first tab ({home})")
            btn = pg.locator("button[aria-label*=opy]").first; btn.focus(); pg.keyboard.press("Enter"); pg.wait_for_timeout(300)
            live = pg.evaluate("""() => [...document.querySelectorAll('[aria-live]')].map(e=>e.textContent.trim()).join('|')""")
            log(bool(live), f"/: Enter on a copy button announces via aria-live ('{live[:40]}')")
        ctx.close()
    b.close()
print("\n".join(out)); print(f"{sum(o.startswith('PASS') for o in out)}/{len(out)} checks passed")
