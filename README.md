# Qrypt quantum entropy quickstart

Turn 1 KiB of Qrypt quantum entropy into an AES-256-GCM key in Python or Node, in about 5 minutes.

**Site:** https://qrypt-quickstart.pages.dev/ · Agent docs: `/llms.txt` · Agent guide: `AGENTS.md`

## Grader path (under 5 minutes)
1. `make check` — install Python deps and run **both snippets against the mock** (success, 401, 403, 429, 500, 503, network/non-JSON, missing token). No token needed.
2. Optional live (1 KiB each): put a token in `quickstart/python/.env` and/or `quickstart/node/.env`, then `make live-py` / `make live-js`.
3. Docs site: `site/` (Cloudflare Pages via CI).

Requirements: Python 3.9+, Node 20.12+.

## Using an AI coding agent?
Two modes — details on the site and in `AGENTS.md`:

| | Quick Setup (default) | Isolated Setup |
|---|---|---|
| Docker | No | Yes (`agent-sandbox/`) |
| Agent sees your token | Possible (behavioral rules only) | No — token stays on the host |
| Live verify | Agent runs the example after you set `.env` | You run `agent-sandbox/verify.sh --env …` |

```bash
# Isolated Setup (token kept outside the project):
mkdir -p ~/.config/qrypt   # put QRYPT_API_KEY there, chmod 600
agent-sandbox/run.sh ~/qrypt-demo your-agent-command
agent-sandbox/verify.sh --env ~/.config/qrypt/.env
agent-sandbox/test-isolation.sh   # no real token; proves the boundaries
```

## Layout
- `quickstart/python`, `quickstart/node` — snippets (≤25 lines excl. comments/imports)
- `mock/` — stdlib mock API + `run_cases.sh`
- `agent-sandbox/` — Isolated Setup (Docker + trusted `verify.sh`)
- `site/` — static docs; `site-src/` templates filled by `make site`
- `AGENTS.md`, `PRD.md`, `AGENT_READINESS.md`, `BACKLOG.md`, `AI_USAGE.md`

Tokens are never printed; `.env` is gitignored.
