# Backlog: 10 follow-ups, RICE-scored

**RICE = Reach × Impact × Confidence ÷ Effort.** Higher scores go first.
- **Reach:** new developers or agent sessions affected per quarter, out of the PRD's assumed 400 signups.
- **Impact:** 3 = huge, 2 = high, 1 = medium, 0.5 = low.
- **Confidence:** how sure we are, from 0 to 100%.
- **Effort:** person-weeks.

Evidence links point to `AGENT_READINESS.md`, `agent-readiness/runs.csv`, `docs/research.md` and `docs/claims-to-source.md`.

| # | Item | Reach | Impact | Conf. | Effort (wk) | **RICE** | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | ✅ **DONE (Oct 14–15): two-mode agent onboarding.** Quick Setup (default, no Docker) + Isolated Setup (`agent-sandbox/run.sh` + trusted `verify.sh`, agent never sees the token). Round 4 (older qrypt-run design) was 5/5 working, 0/5 leaks; new Isolated Setup is covered by `test-isolation.sh`. | 200 | 3 | 90% | 1 | **540** | Secret peek in 14/15 unrestricted runs; Docker optional for accessibility (PRD §7a) |
| 2 | **Ask Qrypt for short-lived or scoped tokens** (for example 1-hour test tokens) so a leaked transcript is low-risk | 400 | 2 | 50% | 4 | **100** | Up to 36 of 40 token characters reached transcripts (round 2) |
| 3 | **Ask Qrypt to return 401 for a wrong token** (keep 403 for quota only) | 400 | 2 | 90% | 1 | **720** | Live test: a bad token returned 403 "Forbidden or entropy quota reached" |
| 4 | **Ask Qrypt to send `Retry-After` / `X-RateLimit-*` headers** and to document the real 429 behavior | 150 | 2 | 80% | 1 | **240** | No rate-limit headers on any response. A 429 came back about 1 s after a single call, stricter than "30 per 10 s". |
| 5 | **Allow the default Python User-Agent** (or document the Cloudflare rule in the official docs) | 120 | 2 | 90% | 0.5 | **432** | `Python-urllib` got 403 "Error 1010" from Cloudflare. The other clients passed. |
| 6 | **Fix the official curl example** so it includes `Accept: application/json` | 400 | 0.5 | 100% | 0.1 | **2000** | docs.qrypt.com/eaas curl example compared with its own Request table |
| 7 | **Publish quota size and a usage endpoint or portal meter** | 300 | 1 | 70% | 2 | **105** | Quota size isn't documented anywhere, and a 403 is the only signal |
| 8 | **Wire up funnel instrumentation** (the events from PRD §4: `X-Qrypt-Client` header counting, a `src=qs` link parameter) | 400 | 2 | 60% | 3 | **160** | No funnel data exists today. The PRD specifies the events. |
| 9 | **Clean-machine agent test in CI** (a container with no home-directory configs, run monthly) | 50 | 1 | 80% | 1 | **40** | Our runs read the user's home skills and MCP tools, and found pre-installed packages |
| 10 | **Third-language snippet (Go) and an official-docs link to this quickstart** | 100 | 1 | 50% | 1 | **50** | The brief lists it as a stretch goal. Developers in other languages hit the same base64 and KiB gotchas. |

| 11 | **Say "no key-derived output"** in the docs and snippets: no fingerprints or hashes of the key. Print only the success line. | 100 | 0.5 | 70% | 0.1 | **350** | Claude Code printed a 16-hex SHA-256 fingerprint of the key in 3 runs |
| 12 | **Ship `QRYPT-SANDBOX-README.txt`-style hints with any restricted setup.** Agents read the folder listing before the docs. | 100 | 1 | 80% | 0.1 | ✅ done (`42c864f`) | Claude gave up 1/5 runs without the hint and succeeded 5/5 with it |

Items #11 and #12 came from the cross-agent rounds (Codex and Claude Code). The key-to-disk finding (Codex 5/5) was fixed directly in the docs (`8985bbd`) and is not a backlog item.

**Sorted by score:** #6 (2000), #1 (960), #3 (720), #5 (432), #4 (240), #8 (160), #7 (105), #2 (100), #10 (50), #9 (40).
**Recommendation:** #1 is done (`agent-sandbox/`, see AGENT_READINESS.md round 4). Do #6 this week, since it's cheap. #3, #5 and #4 are asks for Qrypt (Sean Neal) and can go in one email.

| 13 | **Disposable / short-lived tokens in Quick Setup UX** — deep-link to portal trial with "test token" framing | 200 | 2 | 50% | 1 | **200** | Quick Setup cannot stop agents reading `.env`; disposable tokens are the residual control |
| 14 | ✅ **DONE (Oct 15): Wired Isolated + Quick Setup into the harness.** `run_quick_setup.sh` (two-phase) and `run_isolated_setup.sh` (hashed image `92cd0628f7f0` + host verify.sh). Cursor 5/5 each. See AGENT_READINESS.md two-mode section. | 50 | 2 | 90% | 1 | **90** | Eval complete; Codex/Claude on new modes still outstanding |
| 15 | **Windows path notes for Isolated Setup** (Docker Desktop bind mounts, `%USERPROFILE%\.config\qrypt\.env`) | 80 | 1 | 60% | 0.5 | **96** | Current docs are macOS/Linux-first |

| 16 | **Docs: tell agents not to probe `~/.env` or other home secret paths** during Quick Setup | 100 | 0.5 | 80% | 0.1 | **400** | Claude Code `ls ~/.env` in 2/5 Quick runs (no leak) |

**Added Oct 15 (two-mode redesign):** #13–15. #16 from Claude Quick home-path probes. Recommendation: keep #6 (curl Accept header) as the cheapest Qrypt-side ask; #13 is the top residual risk for Quick Setup users.
