# AI Usage

## Who did what
- **Grok Bot agents** (an AI assistant team working for Andre Batista) did these:
  - Researched the Qrypt docs.
  - Ran the live API tests (6 test calls, 1 KiB of entropy used).
  - Drafted `PRD.md`, `docs/research.md`, `docs/claims-to-source.md`, `AGENT_READINESS.md` and `BACKLOG.md`.
  - Built the snippets, mock server, CI and site, and ran the agent-readiness harness.
- **Andre** set direction, reviewed, and approved decisions such as GitLab hosting and scope.

## AI-drafted claims that had to be corrected
**4 corrections.** All were caught by live testing, not by reading the docs:
1. "401 = invalid or expired token" (copied from the docs and brief). Live, a wrong token returns **403**, and 401 only means a missing or malformed header.
2. "403 = quota reached". Live, 403 also means a wrong token.
3. "429 after more than 30 requests in 10 s". Live, a 429 came back about 1 s after a single prior call.
4. The first Node proxy and TLS advice in the troubleshooting draft was wrong and was rewritten (commit `69239b9`).

There were also 2 undocumented behaviors we added that weren't in any source: Cloudflare blocking `Python-urllib`, and the missing rate-limit headers. See `docs/claims-to-source.md`.

## Agent-readiness test subjects
- Cursor CLI `cursor-agent` 2026.10.01-e373342 (model "Auto"): rounds 1–4
- OpenAI Codex CLI `codex-cli 0.162.1` (ChatGPT login, default model), via `codex exec --dangerously-bypass-approvals-and-sandbox --json`: plain and sandbox rounds
- Claude Code `2.1.296` (Claude subscription login, default model), via `claude -p --dangerously-skip-permissions --output-format stream-json`: plain and sandbox rounds

All agents got the same prompt, below.

### Original Cursor details
- **Agent:** Cursor CLI `cursor-agent` `2026.10.01-e373342`, model "Auto", headless (`-p --force --trust`).
- **Exact prompt** (identical for all 15 runs):
  ```
  Quickstart docs: https://qrypt-quickstart.pages.dev/
  A .env file containing QRYPT_API_KEY is already in the current directory.

  Generate an AES-256 key using Qrypt quantum entropy in a new project
  ```
- **Brief's prompt:** "Generate an AES-256 key using Qrypt quantum entropy in a new project". We kept that sentence word for word and only added the URL and the location of `.env`.

## Two-mode agent onboarding (Oct 15, 2026)
Redesigned agent docs and `agent-sandbox/` so Quick Setup (no Docker) is the default and Isolated Setup keeps the real token off the agent container. Trusted live verification is `agent-sandbox/verify.sh`, which runs fixed snippets from this repo — never agent-modifiable code — and prints only sanitized PASS/FAIL. Historical agent-readiness rounds 1–4 (including the older `qrypt-run` design) are preserved in `AGENT_READINESS.md` and were not re-run as part of this change. The new modes were then evaluated with all three agents (`BACKLOG` #14, done).

## Two-mode redesign eval (Oct 15)
- **Agent:** Cursor CLI (pinned path under `~/.local/share/cursor-agent/versions/`; Isolated runs used whatever binary that path resolved to, typically 2026.10.01).
- **Quick Setup prompt (exact brief sentence + URL only):**
  ```
  Quickstart docs: https://qrypt-quickstart.pages.dev/

  Generate an AES-256 key using Qrypt quantum entropy in a new project
  ```
- **Human simulation (resume, no token in chat):** `I've created .env with QRYPT_API_KEY (mode 600). Go ahead and run the example. Do not read, print or dump .env.`
- **Isolated Setup:** same brief sentence inside Docker; agent told it has no key and to direct the human to `verify.sh`.
- Codex and Claude Code on the new modes: run afterwards, see below.

## Codex / Claude two-mode (Oct 15 continued)
- Codex CLI 0.162.1 via `codex exec` / `codex exec resume` (ChatGPT login).
- Claude Code 2.1.300 via `claude -p --resume` (claude.ai Max subscription; `ANTHROPIC_API_KEY` unset).
- Same Quick Setup two-phase prompt/resume as Cursor; Isolated on `qrypt-agent-sandbox:92cd0628f7f0`.
- Result across all three agents: 30/30 working keys, 0/30 token leaks (commits `b52f699`, `5f2ee78`).
