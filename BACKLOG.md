# Backlog: 21 items (16 open, 5 done), RICE-scored

**RICE = Reach × Impact × Confidence ÷ Effort.** Higher scores go first.
- **Reach:** new developers or agent sessions affected per quarter, out of the PRD's assumed 400 signups.
- **Impact:** 3 = huge, 2 = high, 1 = medium, 0.5 = low.
- **Confidence:** how sure we are, from 0 to 100%.
- **Effort:** person-weeks.

Items are numbered in the order we found them; the open table is sorted by RICE score. Funnel instrumentation (#8) is specified in `docs/PRD-funnel-metrics.md`. Evidence links point to `AGENT_READINESS.md`, `agent-readiness/runs.csv`, `docs/research.md` and `docs/claims-to-source.md`.

## Open items, highest RICE first
| # | Item | Reach | Impact | Conf. | Effort (wk) | **RICE** | Evidence |
|---|---|---|---|---|---|---|---|
| 6 | **Fix the official curl example** so it includes `Accept: application/json` | 400 | 0.5 | 100% | 0.1 | **2000** | docs.qrypt.com/eaas curl example compared with its own Request table |
| 18 | **Python: catch a missing `random` field** (`KeyError`/`IndexError`) with the same friendly non-JSON message | 400 | 0.5 | 90% | 0.1 | **1800** | Opus review, Oct 15: `except (requests.RequestException, ValueError)` misses `resp.json()["random"][0]` on an unexpected body. Must stay within 25 lines. |
| 19 | **Tip: one `size=1` call gives 1 KiB = 32 separate 32-byte keys** from distinct slices (`raw[i*32:(i+1)*32]`), instead of one call per key | 200 | 0.5 | 80% | 0.1 | **800** | Opus review, Oct 15. Also cuts 429 risk. |
| 3 | **Ask Qrypt to return 401 for a wrong token** (keep 403 for quota only) | 400 | 2 | 90% | 1 | **720** | Live test: a bad token returned 403 "Forbidden or entropy quota reached" |
| 20 | **Move the agent modes (Quick/Isolated) to their own page** so the 5-minute human path is shorter | 400 | 1 | 60% | 0.5 | **480** | Opus review, Oct 15: the human page feels heavy below step 4 |
| 5 | **Allow the default Python User-Agent** (or document the Cloudflare rule in the official docs) | 120 | 2 | 90% | 0.5 | **432** | `Python-urllib` got 403 "Error 1010" from Cloudflare. The other clients passed. |
| 16 | **Docs: tell agents not to probe `~/.env` or other home secret paths** during Quick Setup | 100 | 0.5 | 80% | 0.1 | **400** | Claude Code `ls ~/.env` in 2/5 Quick runs (no leak) |
| 11 | **Say "no unprompted key-derived output"** to agents: print only the success line. Since Oct 15 the page has an *optional, human-opted-in* 8-hex fingerprint block; llms.txt tells agents to add it only if asked and never print more. | 100 | 0.5 | 70% | 0.1 | **350** | Claude Code printed a 16-hex SHA-256 fingerprint of the key in 3 runs |
| 4 | **Ask Qrypt to send `Retry-After` / `X-RateLimit-*` headers** and to document the real 429 behavior | 150 | 2 | 80% | 1 | **240** | No rate-limit headers on any response. A 429 came back about 1 s after a single call, stricter than "30 per 10 s". |
| 13 | **Disposable / short-lived tokens in Quick Setup UX** — deep-link to portal trial with "test token" framing | 200 | 2 | 50% | 1 | **200** | Quick Setup cannot stop agents reading `.env`; disposable tokens are the residual control |
| 8 | **Wire up funnel instrumentation** (the events from PRD §4: `X-Qrypt-Client` header counting, a `src=qs` link parameter) | 400 | 2 | 60% | 3 | **160** | No funnel data exists today. The PRD specifies the events. |
| 7 | **Publish quota size and a usage endpoint or portal meter** | 300 | 1 | 70% | 2 | **105** | Quota size isn't documented anywhere, and a 403 is the only signal |
| 2 | **Ask Qrypt for short-lived or scoped tokens** (for example 1-hour test tokens) so a leaked transcript is low-risk | 400 | 2 | 50% | 4 | **100** | Up to 36 of 40 token characters reached transcripts (round 2) |
| 15 | **Windows path notes for Isolated Setup** (Docker Desktop bind mounts, `%USERPROFILE%\.config\qrypt\.env`) | 80 | 1 | 60% | 0.5 | **96** | Current docs are macOS/Linux-first |
| 10 | **Third-language snippet (Go) and an official-docs link to this quickstart** | 100 | 1 | 50% | 1 | **50** | The brief lists it as a stretch goal. Developers in other languages hit the same base64 and KiB gotchas. |
| 9 | **Clean-machine agent test in CI** (a container with no home-directory configs, run monthly) | 50 | 1 | 80% | 1 | **40** | Our runs read the user's home skills and MCP tools, and found pre-installed packages |

## Done
| # | Item | Reach | Impact | Conf. | Effort (wk) | **RICE** | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | ✅ **DONE (Oct 14–15): two-mode agent onboarding.** Quick Setup (default, no Docker) + Isolated Setup (`agent-sandbox/run.sh` + trusted `verify.sh`, agent never sees the token). Round 4 (older qrypt-run design) was 5/5 working, 0/5 leaks; new Isolated Setup is covered by `test-isolation.sh`. | 200 | 3 | 90% | 1 | **540** | Secret peek in 14/15 unrestricted runs; Docker optional for accessibility (PRD §7a) |
| 12 | **Ship `QRYPT-SANDBOX-README.txt`-style hints with any restricted setup.** Agents read the folder listing before the docs. | 100 | 1 | 80% | 0.1 | ✅ done (`42c864f`) | Claude gave up 1/5 runs without the hint and succeeded 5/5 with it |
| 14 | ✅ **DONE (Oct 15): Wired Isolated + Quick Setup into the harness.** `run_quick_setup.sh` (two-phase) and `run_isolated_setup.sh` (hashed image `92cd0628f7f0` + host verify.sh). Cursor 5/5 each. See AGENT_READINESS.md two-mode section. | 50 | 2 | 90% | 1 | **90** | Eval complete for Cursor, Codex and Claude Code: 30/30 working, 0/30 leaks |
| 17 | ✅ **DONE (Oct 15): Rerun Codex with its sandbox on.** Quick 5/5 with Codex sandbox on (`workspace-write`, network on, approvals never), Isolated 5/5 inside the Docker sandbox; 0/10 leaks (AGENT_READINESS, "Codex sandbox-on rerun") | 100 | 1 | 80% | 0.2 | **400** | Earlier runs used the bypass flag before AppArmor allowed bubblewrap |
| 21 | ✅ **DONE (Oct 15): Starter archive download.** `/qrypt-quickstart-starter.zip` holds the snippets, mock + tests, `requirements.txt`, `.env.example`, `AGENTS.md`, `Makefile` and `agent-sandbox/` (replaces 5 one-by-one downloads). Built by `make site`; CI `tools/check_starter.py` checks byte equality and no `.env`/token. | 400 | 1 | 90% | 0.3 | **1200** | Opus review: page referenced files in a private repo |

**Where they came from:** #1–10 from the first agent rounds and our live API review; #11–12 from the Codex and Claude Code rounds; #13–15 from the two-mode redesign; #16 from Claude probing `~/.env` (a home-folder file check, no contents shown) in 2 of 5 Quick runs; #17 from the Codex sandbox follow-up; #18–21 from the Oct 15 "Opus review" of the site and snippets (see each item's evidence). The key-to-disk finding (Codex 5/5) was fixed directly in the docs (`8985bbd`) and is not a backlog item.

**Recommendation:** do #6 this week (fix the official curl example; cheapest). Send #3, #5 and #4 to Qrypt (Sean Neal) in one email. #16 and #11 are 1-hour doc edits. #13 (disposable tokens) is the main remaining risk for Quick Setup users.
