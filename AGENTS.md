# Guidance for AI coding agents

This repository has two onboarding modes. Prefer **Quick Setup** unless the human asks for Isolated Setup.

Humans should paste only a short request plus links to the quickstart and `llms.txt`.
All rules below (and in `llms.txt`) apply even when the paste-prompt does not repeat them.

## Quick Setup (default, no Docker)
1. Read https://qrypt-quickstart.pages.dev/llms.txt and the quickstart page.
2. Pick Python or Node; use the official snippets in `quickstart/`.
3. Install deps; run mocked tests (`make check` in this repo, or point `QRYPT_BASE_URL` at `mock/server.py`).
4. Ask the human to create `.env` with `QRYPT_API_KEY` themselves. Never ask them to paste the token into chat, prompts, CLI args or source.
5. Never read, print or dump `.env` or environment variables. Never enable verbose HTTP logging of Authorization headers.
6. After the human confirms `.env` is set, run the example. Keep the key in memory only.
7. Report the success line only. Remind the human to review the session for credential exposure and to rotate any exposed or potentially compromised credentials (including unrelated ones).

These rules are behavioral safeguards. They do **not** stop an unrestricted agent from reading files. Disposable tokens and Isolated Setup exist for that.

## Isolated Setup (Docker)
- Human runs `agent-sandbox/run.sh <clean-project> <agent-command>`. The project must not contain `.env`.
- You (the agent) have no `QRYPT_API_KEY`. Implement and mock-test only.
- Human runs `agent-sandbox/verify.sh --env <secret-path>` on the host. That runs **fixed** snippets from this repo, not your code, with the real token. Output is sanitized PASS/FAIL.
- Do not ask for the token. Do not try to read secrets from the host.

## Manual developer path
Humans who are not using an agent should follow the numbered steps on the quickstart page (token → `.env` → snippet → run). `make check` needs no token.
