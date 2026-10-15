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

## Agent-readiness test subject
- **Agent:** Cursor CLI `cursor-agent` `2026.10.01-e373342`, model "Auto", headless (`-p --force --trust`).
- **Exact prompt** (identical for all 15 runs):
  ```
  Quickstart docs: https://qrypt-quickstart.pages.dev/
  A .env file containing QRYPT_API_KEY is already in the current directory.

  Generate an AES-256 key using Qrypt quantum entropy in a new project
  ```
- **Brief's prompt:** "Generate an AES-256 key using Qrypt quantum entropy in a new project". We kept that sentence word for word and only added the URL and the location of `.env`.
