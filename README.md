# Qrypt quantum entropy quickstart

Turn 1 KiB of Qrypt quantum entropy into an AES-256-GCM key in Python or Node, in about 5 minutes.

## Grader path (under 5 minutes)
1. `make check` installs Python deps and runs **both snippets against the mock server** for success, 401, 403, 429, 500, 503 and a missing token. No token needed.
2. Optional, real API (1 KiB each): `cp .env.example quickstart/python/.env` (and/or `quickstart/node/.env`), paste your token, then `make live-py` / `make live-js`.
3. Docs site: `site/` (deployed to Cloudflare Pages by CI); agent docs at `site/llms.txt`.

Requirements: Python 3.9+, Node 20.12+.

## Layout
- `quickstart/python`, `quickstart/node` — the snippets (≤25 lines excluding comments/imports)
- `mock/` — stdlib mock of the entropy API + `run_cases.sh`
- `site/` — static docs (deployed); `site-src/` templates are filled from the snippets by `make site`
- `tools/lighthouse.sh` — 10 mobile Lighthouse runs; reports in `reports/lighthouse/`
- `.gitlab-ci.yml` — mock tests on every push; Pages deploy on main (needs masked `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`)
- `PRD.md`, `docs/` — PRD, research, claims-to-source

Tokens are never printed; `.env` is gitignored.
