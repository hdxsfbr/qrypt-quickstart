# Docs-shell design notes (reference: docs.qrypt.com)

Captured 2026-10-15 from https://docs.qrypt.com/eaas/ (`ref/eaas.html`, `ref/theme-mine.css`).
Reference files are kept for study only; no Qrypt asset is hotlinked or served by our site.

## What their docs are
- Hugo 0.154 + the "Learn" theme, customised in `theme-mine.css` (colours "taken from Qrypt branding guide").
- Layout: fixed **left sidebar** (logo + "Documentation", search box, nested topic list,
  footer links "Qrypt Website / Github Repo / Help & Support"), **content column** (`#body-inner`,
  max-width ~90rem, white on an off-white page), top bar with breadcrumbs. No on-page TOC.
- Sidebar topics: Quantum Entropy (On-Prem Appliance, RNG Tools, Qseed), DQKD Key Generation
  (Overview, Quickstarts, Qrypt SDK Quickstarts, NVIDIA Quantum Secure Gateway, API Reference,
  Qrypt SDK, Changelogs), Concepts (Key Generation Architecture, Key Entropy Size, OTP), FAQs.
- Active item: `--blue-10` (#eeeefc) background, navy text. Links in sidebar navy, 0.975rem, 0.75rem 1rem padding.
- Font: IBM Plex Sans (self-hosted). Headings navy; h1 1.6rem, h2 1.35rem, h3 1.1rem; body 0.975rem.
- Palette: navy #171628, navy-5 #fafafa (sidebar), navy-20 #d2d2d5 (borders), blue #5654e5,
  blue-10 #eeeefc, off-white #f1f1f1, orange-10 #ffecb7 (marks). Tables/ol/pre rounded 0.75rem.
- Logo: inline SVG wordmark (registered trademark) – **not copied**.

## Our shell (choices)
- Same skeleton: left sidebar (sticky on desktop, collapsible drawer on mobile behind a
  `Menu` button with `aria-expanded`), white content column, rounded tables.
- Neutral text mark "Qrypt Docs · Quickstart prototype" instead of their logo (trademark).
- Font: system stack instead of IBM Plex (no webfont download = Lighthouse budget).
- Palette: their navy/blue tokens; blue #5654e5 is 5.4:1 on white (AA).
- Sidebar items for pages we do not have link out to the real page on docs.qrypt.com
  (marked ↗, `rel=noopener`) – no 404s. Our pages: Quickstart, AI coding agents, Troubleshooting (+ anchors).
- Code blocks keep our Pygments dark theme + CSS line numbers (theirs is a light `pre`).
- Visible banner on every page: "Unofficial prototype – not affiliated with or endorsed by Qrypt".

## Result (c8fbca1, deployed)
- Screens: `screens/before-*.png` vs `screens/after-*.png`, plus `after-mobile-menu-open.png`.
- Lighthouse mobile ×10 on `/` at the time of this design pass: LCP 0.88–1.03 s (p95 1.03 s), accessibility 100. `/troubleshooting` single run: LCP 0.93 s, a11y 100. Latest numbers: `reports/lighthouse/feedback-batch/summary.json` (p95 1.32 s on `/`, 1.11 s on `/troubleshooting`).
- Inlined style.css 3.7 KB → 5.4 KB. Mobile menu tested: Enter opens + focuses first link, Escape closes + returns focus.
