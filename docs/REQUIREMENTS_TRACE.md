# Requirements trace

Audit date: Oct 15, 2026 (PT). Every requirement from the portal brief (`docs/brief/portal_brief.txt`) and its attachment (`docs/brief/pm_developer_quickstart_onboarding.md`), checked against code, tests and measured results, not against our own claims.

**Status:** Met = done and evidenced. Partial = mostly done; the note says what differs. Missing = not done.
**Terms:** CI = continuous integration (tests that run automatically on every push). Mock server = a fake local copy of the API used in tests. LOC = lines of code. LCP = Largest Contentful Paint, Lighthouse's "page is visibly loaded" time. p95 = the value 95% of runs are at or below. RICE = Reach × Impact × Confidence ÷ Effort.

## Summary
- **Missing:** video demo (≤ 5 min). Stretch goals not done: third language, analytics, competitive teardown.
- **Partial:** keyboard-only and 200% zoom are built in but were not hand-tested; "every documented command runs as written" is tested for the snippets and `make check` but not for every command on the site (e.g. proxy setup, Windows paths).
- **Everything else is Met.**

## Core requirement 1: snippets
| Requirement | Status | Evidence | Notes |
|---|---|---|---|
| Two languages | Met | `quickstart/python/quickstart.py`, `quickstart/node/quickstart.mjs` | Python + Node |
| ≤ 25 LOC each, excl. comments/imports | Met | Counted Oct 15 (non-blank lines that aren't comments or imports): **Python 25, Node 25** | Exactly at the limit. The optional fingerprint (Oct 15) is a separate labeled block on the page, not in the core files (PRD §5) |
| Reads `QRYPT_API_KEY` from `.env` | Met | `load_dotenv()` (Py); `process.loadEnvFile` (Node 20.12+) | |
| Fetches 1 KiB (`GET api-eus.qrypt.com/api/v1/quantum-entropy?size=1`, both headers) | Met | `params={"size": 1}`; `?size=1`; `Accept` + `Authorization: Bearer` | |
| Base64 decode, take 32 bytes as AES-256 key | Met | `b64decode(...)[:32]`; `Buffer.from(..., "base64").subarray(0, 32)` | |
| AES-GCM encrypt + decrypt round trip | Met | `AESGCM` assert; `aes-256-gcm` cipher/decipher + `assert.equal` | |
| Prints success line, never the key | Met | `Success: AES-256-GCM round trip with a Qrypt key (not shown).` | Key never printed, logged or written to disk |
| Missing token → helpful message (where to get one, how to set it) | Met | `QRYPT_API_KEY is missing: add to .env. Token: portal.qrypt.com/trial-signup-entropy`; mock test asserts it | **Fixed in this audit** (`f93c412`): before, it didn't say where to get a token |
| CI runs both against a mock: success, 401, 429, 503 | Met | `.gitlab-ci.yml` → `mock/run_cases.sh`: 18/18 pass (also 403, 500, non-JSON, network error, missing token) | GitLab pipeline on every push |
| 401/403 explained, no tight retry loop | Met | Snippets exit once with a message, no retry. 403 message: "Token invalid OR monthly quota used" (live bad token returns 403, not 401) | |
| 503/500 → "try again shortly", non-zero exit | Met | `run_cases.sh` checks exit 1 + "Try again shortly" | |
| Snippet runtime < 3 s end to end, live, 5 runs | Met | Python max 0.77 s, Node max 0.55 s (`reports/snippet-runtime.txt`) | Measured in this audit |

## Core requirement 2: deployed site
| Requirement | Status | Evidence | Notes |
|---|---|---|---|
| Deployed URL loads | Met | https://qrypt-quickstart.pages.dev/, `/troubleshooting`, `/llms.txt`: all HTTP 200 (Oct 15) | Cloudflare Pages, deployed by CI from the repo |
| Single path "get a token" → "first key" | Met | Numbered steps on `site/index.html` | |
| Language tabs, copy buttons | Met | `role="tab"` tabs with arrow-key support (`site/app.js`); copy buttons with `aria-label` | |
| Stated time target | Met | "about 5 minutes" on the page | |
| Troubleshooting: 400, 401, 403, 429, 500, 503 as symptom → cause → fix | Met | `site/troubleshooting.html` table | Includes the real 403-for-bad-token behavior |
| Common mistakes: KiB not bytes, decode base64, don't loop | Met | "Common mistakes" list | |
| Environment issues: runtime version, missing `.env`, proxy/TLS | Met | "Environment issues" table + proxy commands | |
| Starter archive matches repo, no secrets | Met | `site/qrypt-quickstart-starter.zip` built by `make site`; CI `tools/check_starter.py` (13 files byte-equal, no `.env`/token); unzipped copy passes `make check` 18/18 (Oct 15) | Added after the Opus review: page referenced files in the private repo |
| Every documented command runs as written | Partial | `make check` and both snippets run in CI; agent runs followed the site commands 30/30 | Proxy and Windows commands not executed (no proxy available) |
| Site builds from the repo on push | Met | CI rebuilds `site/` and fails on drift; `pages-deploy` job | |

## Core requirement 3: PRD
| Requirement | Status | Evidence |
|---|---|---|
| Problem, personas + jobs-to-be-done | Met | `PRD.md` §1, §3 |
| Funnel: landing → token → first call → first key → return in 7 days | Met | §4 table, exact event names and definitions |
| Target + measurement per stage; engineer can instrument without questions | Met | §4: event, source, SQL-style definition, target per stage |
| Scope, out of scope, risks | Met | §5, §6, §8 |
| Explicit tradeoff not made (no SDK) | Met | §7, plus §7a (zero-install first) |
| Plain language, ~10-minute read | Met | Glossary at the top |

## Core requirement 4: agent-readiness
| Requirement | Status | Evidence | Notes |
|---|---|---|---|
| Only the URL + the brief's prompt, fresh environment, 5 runs | Met | `AGENT_READINESS.md` setup; prompt in `AI_USAGE.md` | Original rounds added one line saying where `.env` is; two-mode rounds use the URL + exact sentence only |
| Record success, wall-clock time, failure reason per run | Met | `agent-readiness/runs.csv`, `two_mode_runs.csv`, `cross_agent_runs.csv` | |
| Revise docs, repeat; both rounds logged | Met | Rounds 1→2→3→4 (docs v1–v4), then two-mode | |
| ≥ 4/5 after revision | Met | Every round 5/5 working; two-mode 30/30 across Cursor, Codex, Claude Code (`b52f699`, `5f2ee78`) | |
| Median ≤ 10 min | Met | Medians 30 s – 160 s | |
| Failure taxonomy mapped to doc fixes | Met | `AGENT_READINESS.md` taxonomy table | |
| No tokens in agent logs | Met | Committed logs scrubbed; repo + history scanned for the token prefix: 0 hits (Oct 15) | Rounds 1–3 leaked partial token into Cursor's *local* transcripts; disclosed. The token has not been rotated (owner's decision, test token) |

## Core requirement 5: backlog
| Requirement | Status | Evidence |
|---|---|---|
| ≥ 10 items from findings + own review | Met | `BACKLOG.md`: 21 items (17 open, 4 done), Oct 15 |
| RICE score + evidence each | Met | Scores rechecked arithmetically Oct 15 |

## Performance benchmarks
| Target | Status | Measured |
|---|---|---|
| Agent median ≤ 10 min | Met | 63–160 s per agent/mode |
| Agent success ≥ 4/5 | Met | 5/5 every round; feedback-batch check Claude 1/1, Cursor 1/1, 0 leaks |
| Site load < 1.5 s p95, mobile, 10 runs | Met | **Latest (Oct 15 ~4:10 PM CT, after feedback batch `41230b4`): index p95 LCP 1.32 s (1.18–1.32 s), troubleshooting 1.11 s (1.03–1.11 s), a11y 100 on all 20 runs** (`reports/lighthouse/feedback-batch/summary.json`). Earlier: **p95 LCP 1.03 s** (range 0.88–1.03 s) after the docs-shell redesign (c8fbca1), a11y 100; Lighthouse 12 mobile preset, Oct 15 ~11:40 AM PT (earlier pre-shell run: 0.95 s), `reports/lighthouse/summary.json`. Note: the first re-measure in this audit gave p95 **1.54 s (fail)**; inlining the CSS (`4c7e81c`) removed two blocking requests and fixed it |
| Lighthouse accessibility ≥ 95, report committed | Met | **100** in all 10 runs, `reports/lighthouse/run-*.report.html` |
| Snippet runtime < 3 s, 5 runs | Met | Live, Oct 15 ~11:05 AM PT: **Python 0.48–0.77 s, Node 0.45–0.55 s**, 5/5 success each (`reports/snippet-runtime.txt`, 10 KiB logged) |

## Edge cases, security, accuracy
| Requirement | Status | Evidence |
|---|---|---|
| Unit confusion impossible to miss | Met | KiB warnings on page, llms.txt, 400 message |
| Warn against printing/logging/committing keys and reusing entropy bytes | Met | Page + "Common mistakes" |
| Claims-to-source table; no superlatives | Met | `docs/claims-to-source.md` (27 claims + 6 observations; #24 trial-signup form, #25–27 Codex bwrap sandbox); grep for "unbreakable"/"perfectly secure": 0 |
| Fact-check count of AI-drafted claims | Met | `AI_USAGE.md`: 4 corrections |
| `.env` gitignored, `.env.example` committed | Met | `.gitignore`, `.env.example` |
| Keyboard only, 200% zoom, labelled copy buttons | Partial | Skip link, `:focus-visible`, arrow-key tabs, focusable scrollable code blocks, `aria-label` on copy buttons, Lighthouse a11y 100. Not hand-tested at 200% zoom with keyboard only |
| Analytics disclosed if used | Met (none used) | Footer: "No analytics or cookies" |
| Live usage ≤ 10 MB | Met | `reports/live-usage.log` lists the snippet/verify runs; agent rounds are estimated in `AGENT_READINESS.md` (~44 + ~80 + ~15 + ~40 KiB). Estimated total under 200 KiB, about 2% of the budget |

## Submission and docs
| Requirement | Status | Evidence |
|---|---|---|
| Repo with README, AI_USAGE, snippets, site source, CI | Met | GitLab (Andre's chosen destination instead of GitHub) |
| Grader quick-start < 5 min | Met | README "Grader path": `make check` ~1 min, no token |
| README: run snippets, build site, reproduce agent test | Met | Added in this audit (`bfae05f`) |
| One-line description ≤ 120 characters | Met | README top line (98 characters) |
| AI_USAGE with exact prompt and agent | Met | `AI_USAGE.md` |
| PRD, AGENT_READINESS (both rounds), BACKLOG, claims table | Met | Root + `docs/` |
| Video ≤ 5 min (fresh run, a 401, the funnel, one agent run) | **Missing** | Not recorded yet |

## Stretch
| Item | Status |
|---|---|
| `llms.txt` linked from site | Met |
| Third language | Missing (backlog #10) |
| Privacy-respecting analytics | Missing (specified in PRD §4, not wired; backlog #8) |
| Competitive teardown | Missing |
