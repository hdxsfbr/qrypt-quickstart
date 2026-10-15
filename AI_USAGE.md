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
Redesigned agent docs and `agent-sandbox/` so Quick Setup (no Docker) is the default and Isolated Setup keeps the real token off the agent container. Trusted live verification is `agent-sandbox/verify.sh`, which runs fixed snippets from this repo — never agent-modifiable code — and prints only sanitized PASS/FAIL. Historical agent-readiness rounds 1–4 (including the older `qrypt-run` design) are preserved in `AGENT_READINESS.md` and were not re-run as part of this change; Butler owns follow-up evals (`BACKLOG` #14).
