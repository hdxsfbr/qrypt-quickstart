# Requirements trace

Audit date: **Oct 18, 2026** (final pre-submission pass; previous pass Oct 15). Every line of the portal brief (`docs/brief/portal_brief.txt`) and its attachment (`docs/brief/pm_developer_quickstart_onboarding.md`) is checked against code, tests and measured results, not against our own claims.

**Status:** Met = done and evidenced. Partial = mostly done; the note says what differs. Missing = not done. **Andre** = only Andre can do it.
**Terms:** CI = continuous integration (tests that run automatically on every push). Mock server = a fake local copy of the API used in tests. LOC = lines of code. LCP = Largest Contentful Paint, Lighthouse's "page is visibly loaded" time. p95 = the value 95% of runs are at or below. RICE = Reach × Impact × Confidence ÷ Effort. PRD = product requirements document.

## Summary
- **Not done by us, needs Andre:**
  1. The brief asks for a **GitHub repository**. The code is on GitLab (`labs.gauntletai.com/andrebatista/qrypt-quickstart`), and that project is **private**. Graders can't open it unless Andre adds them, changes its visibility, or mirrors it to GitHub.
  2. The **demo video** exists (3:21, under the 5-minute cap), but it isn't uploaded yet, so there's no video URL.
- **Stretch goals not done:** a third language, wired-up analytics (fully specified in `docs/PRD-funnel-metrics.md`, not built), and a competitive teardown.
- **Partial:**
  - Not every command on the site was run as written. The proxy, Windows and Codex-on-Ubuntu commands weren't run in this audit.
  - The Docker isolation test passes on hdx-lab (12/12, Oct 18), but CI skips it because the runner has no Docker.
  - The agent test didn't give agents *only* the URL plus the brief's sentence in every round: rounds 1–4 added one line saying where `.env` was, and the 10 Codex runs in the 30/30 headline used the site's short prompt.
- **Fixed in this pass:** see "Changes in this audit" at the end.
- **Everything else is Met.**

## Core requirement 1: snippets
| Brief line | Status | Evidence | Notes |
|---|---|---|---|
| "Working quickstart snippets (two languages)" | Met | `quickstart/python/quickstart.py`, `quickstart/node/quickstart.mjs` | Python + Node |
| "≤ 25 lines of code each (excluding comments and imports)" | Met | Re-counted Oct 18 (non-blank lines that aren't comments or `import`/`from` lines): **Python 25, Node 25** | At the limit. The optional fingerprint and the production HKDF note are separate labeled blocks on the page, not in the core files |
| "reads `QRYPT_API_KEY` from `.env`" | Met | `load_dotenv()` (Python); `process.loadEnvFile(".env")` (Node 20.12+) | |
| "fetches 1 KiB of entropy" | Met | `params={"size": 1}`; `?size=1`; headers `Accept: application/json` and `Authorization: Bearer` | |
| "takes 32 bytes as an AES-256 key" | Met | `b64decode(...)[:32]`; `Buffer.from(..., "base64").subarray(0, 32)` | Decoded before slicing |
| "encrypts and decrypts a sample string with AES-GCM" | Met | `AESGCM` round trip + `assert`; `aes-256-gcm` cipher/decipher + `assert.equal` | |
| "prints a clear success line, never the key itself" | Met | `Success: AES-256-GCM round trip with a Qrypt key (not shown).` | Key never printed, logged or written to disk |
| "CI runs both against a mock server" | Met | `.gitlab-ci.yml` job `snippets` → `mock/run_cases.sh` | Runs on every push |
| "each handles a missing token with a helpful message" | Met | `QRYPT_API_KEY is missing: add to .env. Token: portal.qrypt.com/trial-signup-entropy`; mock case asserts it | Says where to get a token and how to set it |
| "tested in CI against a mock server for the success path and for 401, 429, and 503" | Met | **18/18** mock cases pass (fresh clone, Oct 18): success, 401, 403, 429, 500, 503, non-JSON, network error, missing token × 2 languages | Last green CI before this pass: pipeline 56419 (`c4b98b1`) |
| Edge: "Missing or expired token: specific, actionable message … docs cover the 401 case" | Met | Snippet messages; troubleshooting 401 row | Live: a bad token returns 403, not 401; documented |
| Edge: "429 and 403 … snippets do not retry in a tight loop" | Met | No retry code in either snippet; 429 message says wait 10 s or more and never loop | |
| Edge: "503, 500: exit cleanly with a 'try again shortly' message and a non-zero exit code" | Met | Mock cases assert exit 1 + "Try again shortly" | |
| Edge: "the snippet requests only what it needs" | Met | `size=1` (1 KiB) | |
| "Snippet runtime < 3 s end to end, 5 runs" | Met | Live, Oct 15 ~11:05 AM PT: **Python 0.48–0.77 s, Node 0.45–0.55 s**, 5/5 each (`reports/snippet-runtime.txt`) | Not re-run (snippets unchanged since) |

## Core requirement 2: deployed site
| Brief line | Status | Evidence | Notes |
|---|---|---|---|
| "deployed URL loads" | Met | https://qrypt-quickstart.pages.dev/, `/troubleshooting`, `/llms.txt`, starter zip: HTTP 200 after the Oct 18 deploy (see the live check at the end) | Cloudflare Pages, deployed by CI from `main` |
| "A single path from 'get a token' to 'first key'" | Met | Numbered steps 1–4 on `site/index.html` | |
| "language tabs, copy buttons" | Met | `role="tab"` tabs (arrow keys, Home/End); 16 copy buttons on `/`, 4 on `/troubleshooting`, all with `aria-label` | |
| "a stated time target" | Met | "Time: about 5 minutes" | |
| "troubleshooting page covering every error code (400, 401, 403, 429, 500, 503) as symptom → likely cause → fix" | Met | `site/troubleshooting.html` table | Includes the real 403-for-bad-token behavior |
| "common mistakes (size is KiB not bytes; base64 must be decoded; don't loop requests faster than the rate limit)" | Met | "Common mistakes" list + "Things that trip people up" on `/` | |
| Edge: "missing runtime version, missing `.env` file, and corporate proxy/TLS errors with a fix for each" | Met | "Environment issues" table + proxy commands for Python, Node 24+, Node 20/22 | |
| "every documented command runs as written" | Partial | `make check`, both snippets, the starter-zip path and Quick/Isolated Setup were run by agents (30/30) and in the demo recording | Proxy and Windows commands not run (no proxy available); Codex AppArmor commands run once by Andre on hdx-lab, not re-run here |
| "the site builds from the repo on push" | Met | CI rebuilds `site/` from `site-src/` + `quickstart/` and fails on any drift; `pages-deploy` job | Since Oct 18 the build also refreshes the served `site/agent-sandbox/` copies, so drift there is caught too (`038fc9b`) |
| Starter archive (our addition) | Met | `tools/check_starter.py` in CI: 13 files byte-equal to the repo, no `.env` or token | |

## Core requirement 3: onboarding PRD
| Brief line | Status | Evidence |
|---|---|---|
| "Problem, personas and jobs-to-be-done" | Met | `PRD.md` §1, §3 |
| "the activation funnel (landing → token created → first successful call → first key → return within 7 days)" | Met | `PRD.md` §4 (summary); full spec in `docs/PRD-funnel-metrics.md` §4–§5 |
| "a target for each stage" | Met | Every stage has one, all labeled **placeholders**, with the method for setting real ones after 4 weeks of baseline (`docs/PRD-funnel-metrics.md` §7) |
| "how each stage would be measured" | Met | Event name, trigger, emitter (site / edge / portal / gateway / daily job), properties and SQL sketch (`docs/PRD-funnel-metrics.md` §5–§6) |
| "scope, out-of-scope, risks" | Met | `PRD.md` §5, §6, §8; funnel risks in `docs/PRD-funnel-metrics.md` §14 |
| "the tradeoff you are explicitly not making (e.g. 'no full SDK this quarter, and why')" | Met | `PRD.md` §7 (no SDK), plus §7a (zero-install agent onboarding first) |
| "an engineer could build instrumentation from the metrics section without asking you a question" | Met | `docs/PRD-funnel-metrics.md`: event dictionary, identifiers, `ua_class` rules, formulas, privacy rules, CI tests, phases. What's left open is Qrypt's side (its §15) |
| "plain, direct language a busy engineering lead can read in 10 minutes" | Met | Glossaries at the top of both PRDs; `PRD.md` about 10 min, funnel PRD about 12 min |
| Instrumentation actually built | Not required (stretch) | Only the snippet header (`X-Qrypt-Client`) exists; the site has no analytics. Stated plainly in both PRDs |

## Core requirement 4: agent-readiness test
| Brief line | Status | Evidence | Notes |
|---|---|---|---|
| "Give an AI coding agent only your quickstart URL … and the prompt 'Generate an AES-256 key using Qrypt quantum entropy in a new project'" | Partial | `AGENT_READINESS.md` "Which prompt each round used"; prompts in `AI_USAGE.md` | Rounds 1–4 added one line saying `.env` was already there. The two-mode eval used the URL + the brief's sentence for Cursor and Claude Code (20 runs). The 10 Codex runs in the 30/30 headline used the site's short prompt; earlier Codex runs with the brief's sentence were also 10/10 (sandbox off) |
| "in a fresh environment, 5 times" | Met | New temp folder per run with a scrubbed environment; Isolated runs in a fresh container | Limitation stated: a clean folder, not a clean machine (`BACKLOG.md` #9) |
| "Record success/failure, wall-clock time, and the failure reason for each run" | Met | `agent-readiness/runs.csv`, `cross_agent_runs.csv`, `two_mode_runs.csv` | |
| "revise the docs, and repeat … both rounds are logged" | Met | Rounds 1→2→3→4 (docs v1–v4), then the two-mode eval, short-prompt round and feedback-batch check | |
| "≥ 4 of 5 runs succeed after revision" | Met | Every round 5/5 working; two-mode **30/30 working, 0/30 token leaks** across Cursor, Codex (sandbox on) and Claude Code | Strict "no token characters in transcripts" only met from round 4 on; reported as it happened |
| "Agent time-to-first-key: median ≤ 10 min" | Met | Two-mode medians **42–160 s** per agent and mode; rounds 1–4 medians 30–41 s | |
| "Agent failure taxonomy … with the doc change that addressed it" | Met | `AGENT_READINESS.md` taxonomy table | |
| "Include the exact prompt and agent used" | Met | `AI_USAGE.md` (agent names, versions, flags, prompts) | |
| Reproducible from the repo | Met | `agent-readiness/run_*.sh`; README section | **Fixed Oct 18** (`a4310ab`): the scripts had the short prompt hard-coded since Oct 15, so they no longer reproduced the logged rounds. Defaults restored; `PROMPT_STYLE=short` opts in. Round-4 scripts need the old, removed sandbox image (stated) |
| "No tokens … in agent-run logs" | Met | Committed logs scrubbed; full token and 12-character prefix: **0 hits** in all git history and the working tree (Oct 18) | Rounds 1–3 leaked partial token characters into Cursor's *local* transcripts; disclosed. The test token wasn't rotated (Andre's decision) |

## Core requirement 5: backlog
| Brief line | Status | Evidence |
|---|---|---|
| "10 follow-up items drawn from your agent-readiness findings and your own review" | Met | `BACKLOG.md`: 21 items (16 open, 5 done), source of each listed |
| "each with a RICE (or equivalent) score and the evidence behind it" | Met | Every row has R, I, C, E, score and evidence; open table sorted by score; recommendation gives the order. **Fixed Oct 18:** #17 sat in the open table and #21 sat outside any table; PRD counts disagreed (16 vs 17 open) |

## Performance benchmarks
| Target | Status | Measured |
|---|---|---|
| Agent median ≤ 10 min | Met | 42–160 s (two-mode), 30–41 s (rounds 1–4) |
| Agent success ≥ 4/5 | Met | 5/5 every round; 30/30 two-mode |
| "Quickstart site load < 1.5 s p95 on mobile, Lighthouse (mobile preset), 10 runs" | Met | Latest, Oct 15 ~4:10 PM CT after `41230b4`: **`/` p95 LCP 1.32 s** (1.18–1.32 s), **`/troubleshooting` 1.11 s** (1.03–1.11 s), `reports/lighthouse/feedback-batch/summary.json`. Not re-run Oct 18: the only page change in this pass is one line in `llms.txt`, a plain-text file Lighthouse doesn't measure |
| "Lighthouse accessibility ≥ 95, report committed" | Met | **100** in all 20 runs (feedback batch) and all 10 earlier runs (`reports/lighthouse/`) |
| "Snippet runtime < 3 s, 5 runs" | Met | Python 0.48–0.77 s, Node 0.45–0.55 s |

## Edge cases, security, privacy, accuracy
| Brief line | Status | Evidence |
|---|---|---|
| "Unit confusion: … impossible to miss that size is KiB" | Met | KiB warnings on `/`, troubleshooting 400 row, `llms.txt`, snippet 400 message |
| "Key handling: docs warn against printing, logging, or committing keys and against reusing the same entropy bytes" | Met | "Things that trip people up", "Common mistakes", `llms.txt` secrets section |
| "Claims accuracy: … traceable to the official docs … claims-to-source table" | Met | `docs/claims-to-source.md` (27 claims + 6 live observations) |
| "No marketing superlatives such as 'unbreakable' or 'perfectly secure'" | Met | Search of site, docs and README: 0 hits |
| "report how many AI-drafted claims you had to correct" | Met | `AI_USAGE.md`: 4 corrections |
| Not presented as Qrypt's product (our check) | Met | "Unofficial prototype. Not affiliated with or endorsed by Qrypt" banner and footer on every page; **added Oct 18** to `llms.txt`, `README.md` and `PRD.md` |
| "Accessibility: keyboard only, code blocks readable at 200% zoom, copy buttons have accessible labels" | Met | **New Oct 18:** automated check of the live site, **23/23 pass** (`tools/a11y_check.py`, `reports/a11y-keyboard-zoom.txt`): no sideways page scrolling at 200% or 400% zoom, wide code blocks keyboard-scrollable, code text ≥ 12 px, Tab order starts at "Skip to content", a visible focus ring on every stop, arrow/Home keys on tabs, copy buttons labeled and announced. Not tested with a screen reader |
| "`QRYPT_API_KEY` in `.env` only; `.env` in `.gitignore`; ship a committed `.env.example`" | Met | `.gitignore`, `.env.example`; no `.env` tracked |
| "No tokens visible in screenshots, recordings, or agent-run logs" | Met | Demo video frames OCR-checked (`docs/demo-script.md`); log scan above |
| "Generated keys: never printed, logged, or written to disk" | Met | Snippets; `llms.txt` rule against key files |
| "Analytics (if used): no cookies or personal identifiers; disclose it on the site" | Met (none used) | Footer: "No analytics or cookies"; `site/app.js` makes no network calls |
| "keep total live usage ≤ 10 MB (10,240 KiB)" | Met | `reports/live-usage.log`: 35 KiB logged call by call, plus an estimated ~2–4 KiB for the demo recordings; agent rounds estimated in `AGENT_READINESS.md` (~44 + ~80 + ~15 + ~40 KiB). Total under 200 KiB, about 2% of the budget. **0 bytes used in this audit** |
| Isolated Setup boundaries (our addition) | Partial | `make isolation`: **12/12 PASS** on hdx-lab, Oct 18. CI skips it because runner #282 has no Docker (pipeline 56419 log: "skip isolation (no docker)") |

## Submission requirements
| Brief line | Status | Evidence / value |
|---|---|---|
| "GitHub repository with README, `AI_USAGE.md`, snippets, site source, and CI" | **Partial — Andre** | All the contents are there, but the repo is on **GitLab** (https://labs.gauntletai.com/andrebatista/qrypt-quickstart) and is **private**. Andre: give graders access, or mirror to GitHub |
| "Deployed quickstart site URL" | Met | https://qrypt-quickstart.pages.dev/ |
| "`PRD.md`" | Met | `PRD.md` + `docs/PRD-funnel-metrics.md` |
| "`AGENT_READINESS.md` (both rounds)" | Met | All rounds |
| "`BACKLOG.md` or a linked spreadsheet" | Met | `BACKLOG.md` |
| "the claims-to-source table" | Met | `docs/claims-to-source.md` |
| "Grader quick-start in the README: set a token, run each snippet, and see the success line in under 5 minutes" | Met | README "Grader path": `make check` (about 1 min, no token), then `make live-py` / `make live-js` with a token |
| "README documents how to run the snippets, build the site, and reproduce the agent-readiness test" | Met | README sections "Grader path", "Build the site", "Reproduce the agent-readiness test" |
| "one-line project description (≤ 120 characters)" | Met | README: "Quickstart, docs and agent-tested onboarding that turn Qrypt quantum entropy into an AES-256 key." (97 characters) |
| "Video demo (≤ 5 min) showing: a fresh run of the quickstart, one troubleshooting path (e.g. a 401), the funnel in the PRD, and one agent-readiness run" | **Partial — Andre** | `qrypt-demo-v4.mp4`, **3:21**: fresh run (s3), missing-token + 401 (s4), Claude Code Quick Setup run (s5), results (s6), funnel (s7); scene list in `docs/demo-script.md`. Not uploaded yet: no URL |
| "AI Usage Log" (portal deliverable) | Met | `AI_USAGE.md` |
| "Deployment Guide" (portal deliverable) | Met | README "Build the site" + `.gitlab-ci.yml` (`pages-deploy`) |
| "Test Results" (portal deliverable) | Met | `reports/`, `agent-readiness/*.csv`, `docs/qa/`, CI pipelines |

## Stretch
| Item | Status |
|---|---|
| "`llms.txt` … linked from the site" | Met (page head, sidebar, agent section) |
| "Third-language quickstart" | Missing (`BACKLOG.md` #10) |
| "Privacy-respecting analytics wired to the funnel stages you can observe on the site" | Missing: specified in `docs/PRD-funnel-metrics.md` §9 Phase 1, not built (`BACKLOG.md` #8) |
| "Competitive teardown" | Missing |

## Known limitations we are leaving as they are
- `agent-sandbox/Dockerfile` has a comment saying the mock server is available in the image, but the image doesn't contain it; agents get it from the starter archive. We didn't edit the comment, because any edit changes the image tag (`92cd0628f7f0`) that the recorded runs refer to.
- Quick Setup safety depends on the agent following instructions (`PRD.md` §7a); only Isolated Setup physically blocks access.
- The agent-sandbox container has open internet access, and `SANDBOX_DOCKER_ARGS` can undo the isolation if misused (documented in `agent-sandbox/README.md`).

## Changes in this audit (Oct 18)
| Commit | Change |
|---|---|
| `a4310ab` | Agent-readiness scripts default back to the brief's prompt; `PROMPT_STYLE=short` opts in to the short one |
| `2e6788b` | New `docs/PRD-funnel-metrics.md` |
| `abed9a9` | Keyboard and zoom check of the live site (`tools/a11y_check.py`, `reports/a11y-keyboard-zoom.txt`) |
| `f9d6079` | `PRD.md`: links the funnel PRD, labels every target as a placeholder, visit ID no longer stored in the browser, `/` instead of `/quickstart`, says plainly that no analytics ship; `BACKLOG.md`: Done table and counts fixed |
| `e626b8d` | `AGENT_READINESS.md`: which prompt each round used, reproduce notes; `AI_USAGE.md`: funnel PRD, demo video, this audit |
| `aa9a993` | `README.md`: unofficial notice, mock case count, `make isolation`, funnel PRD, video, layout |
| `038fc9b` | Site build refreshes the served `agent-sandbox/` copies (the served README was stale) |
| `159e7a2` | Unofficial notice in `llms.txt`; sandbox README's mock-test step matches the image (no `make`); site and starter archive rebuilt |
| `4a4d62c` | Leak-probe follow-up note, dated design-note numbers, live-usage log entries |
| this commit | This trace |
