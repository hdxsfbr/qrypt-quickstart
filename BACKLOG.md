# Backlog: 10 follow-ups, RICE-scored

**RICE = Reach × Impact × Confidence ÷ Effort.** Higher scores go first.
- **Reach:** new developers or agent sessions affected per quarter, out of the PRD's assumed 400 signups.
- **Impact:** 3 = huge, 2 = high, 1 = medium, 0.5 = low.
- **Confidence:** how sure we are, from 0 to 100%.
- **Effort:** person-weeks.

Evidence links point to `AGENT_READINESS.md`, `agent-readiness/runs.csv`, `docs/research.md` and `docs/claims-to-source.md`.

| # | Item | Reach | Impact | Conf. | Effort (wk) | **RICE** | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | **Agent mode without a token on disk:** recommend `export QRYPT_API_KEY` from a secret manager, or a `.env` the agent can't read (an ignore rule in `.cursorignore`/`.claudeignore`), and document it for each agent | 200 | 3 | 80% | 0.5 | **960** | A secret peek in 14 of 15 runs, despite two doc revisions |
| 2 | **Ask Qrypt for short-lived or scoped tokens** (for example 1-hour test tokens) so a leaked transcript is low-risk | 400 | 2 | 50% | 4 | **100** | Up to 36 of 40 token characters reached transcripts (round 2) |
| 3 | **Ask Qrypt to return 401 for a wrong token** (keep 403 for quota only) | 400 | 2 | 90% | 1 | **720** | Live test: a bad token returned 403 "Forbidden or entropy quota reached" |
| 4 | **Ask Qrypt to send `Retry-After` / `X-RateLimit-*` headers** and to document the real 429 behavior | 150 | 2 | 80% | 1 | **240** | No rate-limit headers on any response. A 429 came back about 1 s after a single call, stricter than "30 per 10 s". |
| 5 | **Allow the default Python User-Agent** (or document the Cloudflare rule in the official docs) | 120 | 2 | 90% | 0.5 | **432** | `Python-urllib` got 403 "Error 1010" from Cloudflare. The other clients passed. |
| 6 | **Fix the official curl example** so it includes `Accept: application/json` | 400 | 0.5 | 100% | 0.1 | **2000** | docs.qrypt.com/eaas curl example compared with its own Request table |
| 7 | **Publish quota size and a usage endpoint or portal meter** | 300 | 1 | 70% | 2 | **105** | Quota size isn't documented anywhere, and a 403 is the only signal |
| 8 | **Wire up funnel instrumentation** (the events from PRD §4: `X-Qrypt-Client` header counting, a `src=qs` link parameter) | 400 | 2 | 60% | 3 | **160** | No funnel data exists today. The PRD specifies the events. |
| 9 | **Clean-machine agent test in CI** (a container with no home-directory configs, run monthly) | 50 | 1 | 80% | 1 | **40** | Our runs read the user's home skills and MCP tools, and found pre-installed packages |
| 10 | **Third-language snippet (Go) and an official-docs link to this quickstart** | 100 | 1 | 50% | 1 | **50** | The brief lists it as a stretch goal. Developers in other languages hit the same base64 and KiB gotchas. |

**Sorted by score:** #6 (2000), #1 (960), #3 (720), #5 (432), #4 (240), #8 (160), #7 (105), #2 (100), #10 (50), #9 (40).
**Recommendation:** do #6 and #1 this week, since both are cheap. #3, #5 and #4 are asks for Qrypt (Sean Neal) and can go in one email.
