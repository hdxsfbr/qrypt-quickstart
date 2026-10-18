# PRD: Onboarding funnel and success metrics

Owner: Andre Batista (PM) · Status: v1.0 · Date: Oct 18, 2026 · Reading time: about 12 minutes
Companion to [`PRD.md`](../PRD.md) §4, which summarizes the funnel. This document is the full specification: an engineer should be able to build the instrumentation from it without asking a question.
This is an unofficial prototype. It is not made by, affiliated with or endorsed by Qrypt. Anything marked **Qrypt-side** needs Qrypt's agreement and engineering time.

## Status at a glance (what exists today vs what is planned)
| Piece | Status | Evidence |
|---|---|---|
| Snippets tag their API calls with `X-Qrypt-Client: quickstart-py/1.0` or `quickstart-js/1.0` (and `User-Agent: qrypt-quickstart/1.0`) | **Implemented** | `quickstart/python/quickstart.py`, `quickstart/node/quickstart.mjs`. `agent-sandbox/verify.sh` runs these same files, so it sends the same tags. |
| Site analytics | **None.** No beacon, no cookies, no local storage. The footer says "No analytics or cookies." | `site/app.js` makes no network calls; `tools/build_site.py` footer text |
| `?src=qs` attribution on the "Get a token" link | **Planned, not built.** The link is a plain `https://portal.qrypt.com/trial-signup-entropy`. | `site/index.html` |
| Portal and API-gateway events (stages 2–5) | **Planned, Qrypt-side.** We have no access to Qrypt's portal or gateway logs. | — |
| Dashboards, batch jobs | **Planned** | — |
| Agent-readiness measurements (our only measured "funnel" data, for AI agents under test conditions) | **Measured** | `AGENT_READINESS.md`, `agent-readiness/*.csv` |

**No real funnel numbers exist yet.** Every target below is a **placeholder** until there are 4 weeks of baseline data.

## Glossary
- **Funnel:** the ordered steps from first visit to a working key, with how many people make it from each step to the next.
- **Activation:** the moment a new developer gets real value. Here: **a working AES-256 key made from Qrypt entropy** (stage 4, `first_key`).
- **North Star metric:** the single number the team tries to grow. **Guardrail metric:** a number that must not get worse while we grow the North Star.
- **Cohort:** a group counted together, e.g. "tokens created in the week of Nov 2".
- **Median / p90:** the middle value / the value 90% of cases are at or below.
- **Beacon:** a tiny, fire-and-forget HTTP request a web page sends to record an event.
- **Edge log:** a record kept by the hosting network (Cloudflare) for each request, including requests from tools that don't run JavaScript, such as AI agents fetching `/llms.txt`.
- **UA (User-Agent):** the name a client sends to identify itself, e.g. `curl/8.5`.
- **HMAC:** a keyed hash. With a secret key held by the server, a hashed ID can't be reversed or guessed by trying every ID.
- **GPC / DNT:** Global Privacy Control and Do Not Track, browser signals that the user doesn't want to be tracked.
- **KiB:** 1,024 bytes. **UTC:** universal time; all timestamps are stored in UTC.

## 1. Problem
For a developer product, time-to-first-success predicts adoption: developers who fail in their first session rarely come back, and tickets from avoidable mistakes are pure cost (brief, Business Context). Today nobody can say how many developers who land on a Qrypt quickstart get a working key, where the rest drop off, or whether a docs change helped. Many of these developers work through AI coding agents, which leave no trace in a browser analytics tool.

## 2. Goals and non-goals
**Goals**
1. Measure every stage of the funnel the brief defines: landing → token created → first successful call → first key → return within 7 days.
2. Give each stage an exact event definition, a formula and a target (placeholder until baseline).
3. Separate humans from AI agents, Python from Node, and Quick from Isolated Setup as far as the data allows, and say plainly where it can't.
4. Do it without cookies or personal identifiers, and disclose it on the site (brief, Security, Privacy & Compliance).
5. Make docs changes testable: every docs release is checked against the funnel and the agent-readiness test.

**Non-goals**
- Tracking individuals, building user profiles, or joining with ad or marketing data.
- Collecting anything about the generated key (not even a hash) or the token value.
- Adding a network call to the snippets. The only signal from the snippet is the request header it already sends.
- Building the Qrypt-side pipeline ourselves. We specify it; Qrypt decides and builds it.

## 3. Who uses this and for what decision
| Reader | Question this answers |
|---|---|
| Engineering lead | What to build, where each event is emitted, how to test it |
| PM (owner) | Which stage loses the most developers, so what to fix next (feeds `BACKLOG.md`) |
| Support | Which errors new developers hit before their first success, and whether tickets fall |
| Sales / go-to-market | How many evaluators reach a working key, how fast, in which language |

## 4. Funnel stages
| # | Stage | Event | Emitted by | Exists today? |
|---|---|---|---|---|
| 1 | Landing | `qs_page_view` (browsers), `qs_doc_fetch` (non-browser fetches) | Site beacon; site edge function | No |
| 2 | Token created | `token_created` | Qrypt portal backend (**Qrypt-side**) | No |
| 3 | First successful call | `first_200` (derived) | Daily job over API-gateway logs (**Qrypt-side**) | No |
| 4 | First key (**activation**) | `first_key` (derived) | Same daily job; relies on the snippet header, which **is** implemented | Header only |
| 5 | Return within 7 days | `return_7d` (derived) | Same daily job | No |

### Activation definition
A token is **activated** when the API returns HTTP 200 to a request that carries `X-Qrypt-Client: quickstart-py/1.0` or `quickstart-js/1.0`. The snippets only print their success line after that 200 and a local AES-GCM encrypt/decrypt round trip, and the round trip can't realistically fail once the 200 arrives, so the tagged 200 is the closest observable stand-in for "a working key" that needs no extra call and sends nothing about the key. Known gaps: an agent that writes its own code instead of copying the snippet drops the header (undercount), and a 200 followed by a local crash would be counted (rare).

The brief's illustrative business case uses a different ratio, **signup → first successful call**. We report it too (metric M3 below), so both definitions are covered.

## 5. Event dictionary
**Common envelope** (every event): `event` (string), `ts_utc` (ISO 8601, server time), `schema_version` (int, starts at 1), `source` (`site`, `edge`, `portal`, `gateway`, `job`). Events are append-only; the dedup key is listed per event.

**Identifiers (no personal data):**
- `visit_id`: 128-bit random value (`crypto.randomUUID()`) made **in memory on each page load**. It is **not** stored in a cookie, `localStorage` or `sessionStorage`, so it can't follow anyone across visits. (This replaces the earlier `localStorage` ID idea in `PRD.md` v1.1.)
- `token_hash`: `HMAC-SHA-256(server_secret, token_id)`, first 16 hex characters. Computed by Qrypt from the token's **ID**, never from the token value. Our side never sees token IDs or values.
- Stage 1 → 2 join: the "Get a token" link becomes `https://portal.qrypt.com/trial-signup-entropy?src=qs&qs_visit=<visit_id>`. The portal keeps `qs_visit` with the first token it issues for that signup.

### Stage 1: Landing
| Event | Trigger | Properties | Dedup key |
|---|---|---|---|
| `qs_page_view` | Browser loads `/` or `/troubleshooting` and JavaScript runs. Sent once per load with `navigator.sendBeacon` to `POST /e`. | `visit_id`; `path` (`/` or `/troubleshooting`); `anchor` (URL fragment, e.g. `#codex-bwrap`, or null); `referrer_domain` (domain only, e.g. `google.com`, or `direct`); `ua_class` (set by the server, see below) | `visit_id` + `path` |
| `qs_doc_fetch` | Any request for `/llms.txt`, `/`, `/troubleshooting` or `/qrypt-quickstart-starter.zip`, counted at the edge, whether or not JavaScript runs. This is how AI agents are seen. | `path`; `ua_class`; `status`; `bytes` | none (raw request count) |

### Supporting site events (diagnostics, not stages)
All sent to `POST /e` with `visit_id` and `path`.
| Event | Trigger | Extra properties |
|---|---|---|
| `qs_tab_select` | User picks the Python or Node tab | `lang` (`py`, `js`) |
| `qs_copy_click` | Any copy button | `block_id` (the code block's id, e.g. `py-install`, `py-snippet`, `js-snippet`, `env-line`, `prompt-quick`, `prompt-isolated`), `lang` |
| `qs_signup_click` | Click on the "Get a token" link | none |
| `qs_starter_click` | Click on the starter-archive link | none |

### Stage 2: Token created (Qrypt-side)
| Event | Trigger | Properties | Dedup key |
|---|---|---|---|
| `token_created` | Portal issues an **Entropy** access token | `token_hash`; `is_first_token_for_account` (bool); `signup_source` (`qs` if the signup URL had `src=qs`, else `other`); `signup_visit_id` (the `qs_visit` value, or null); `plan` (`trial`, `paid`, …) | `token_hash` |

### Stage 3–5: derived daily from gateway logs (Qrypt-side)
Input: one row per request to `/api/v1/quantum-entropy`: `ts_utc`, `token_hash`, `status`, `size`, `client_tag` (the `X-Qrypt-Client` value, or null), `ua_class`. Rows for tokens older than 30 days can be dropped from this job.

| Event | Definition | Properties |
|---|---|---|
| `first_200` | The earliest request with `status = 200` for a `token_hash` | `client_tag`; `size`; `seconds_since_token_created`; `errors_before` (count of non-200s for that token before it, by status: 400, 401, 403, 429, 500, 503) |
| `first_key` | The earliest `status = 200` request whose `client_tag` is `quickstart-py/1.0` or `quickstart-js/1.0` | `lang` (`py` or `js`, from the tag); `seconds_since_token_created`; `seconds_since_first_page_view` (only when the token joins to a `visit_id`) |
| `return_7d` | Any `status = 200` request for the same `token_hash` more than 24 hours and at most 7 days after `first_200`, whose `client_tag` is **not** a quickstart tag (i.e. the developer's own integration) | `first_return_ts_utc`; `calls_in_window` |

SQL sketch (any SQL warehouse):
```sql
-- first_200 and first_key per token
SELECT token_hash,
       MIN(ts_utc) FILTER (WHERE status = 200)                                  AS first_200_ts,
       MIN(ts_utc) FILTER (WHERE status = 200
                             AND client_tag IN ('quickstart-py/1.0','quickstart-js/1.0')) AS first_key_ts
FROM gateway_requests GROUP BY token_hash;

-- return_7d
SELECT f.token_hash, MIN(g.ts_utc) AS first_return_ts
FROM first_calls f JOIN gateway_requests g USING (token_hash)
WHERE g.status = 200
  AND (g.client_tag IS NULL OR g.client_tag NOT LIKE 'quickstart-%')
  AND g.ts_utc >  f.first_200_ts + INTERVAL '24 hours'
  AND g.ts_utc <= f.first_200_ts + INTERVAL '7 days'
GROUP BY f.token_hash;
```

### `ua_class` rules (server-side only)
Set from the `User-Agent` on the server; the raw UA string is not stored.
- `agent`: matches a maintained list of AI-agent and AI-fetcher patterns (for example `ChatGPT-User`, `Claude-User`, `Perplexity-User`, and the UAs our own harness observes for Cursor, Codex and Claude Code; the list lives in the repo and is reviewed monthly).
- `tool`: `curl`, `Wget`, `python-requests`, `node`/`undici`, `Go-http-client` and similar.
- `bot`: search and crawler bots (`Googlebot`, `bingbot`, …). Excluded from all funnel metrics.
- `human`: a mainstream browser UA **and** the beacon fired (JavaScript ran).
- `unknown`: everything else.

## 6. Metrics and formulas
All rates are computed per weekly cohort (Monday 00:00 UTC). `bot` traffic is excluded everywhere.

**North Star — weekly activated tokens:** the number of tokens created in the week that reach `first_key` within 24 hours of `token_created`.

| ID | Metric | Formula |
|---|---|---|
| M1 | Landing engagement | human `visit_id`s on `/` with at least one of `qs_copy_click`, `qs_tab_select`, `qs_signup_click`, `qs_starter_click` ÷ human `visit_id`s on `/` |
| M2 | Landing → token | distinct `signup_visit_id` on `token_created` ÷ human `visit_id`s on `/` (same week). Sub-metric M2b: ÷ `visit_id`s with `qs_signup_click` |
| M3 | Token → first successful call (the brief's "signup → first call") | tokens with `first_200` within 24 h of `token_created` ÷ tokens created |
| M4 | First call → first key | tokens with `first_key` ÷ tokens with `first_200` |
| M5 | Return within 7 days | tokens with `return_7d` ÷ tokens with `first_key` |
| M6 | Time to first key (landing) | median and p90 of `first_key.ts − earliest qs_page_view.ts` for tokens that join to a `visit_id` |
| M7 | Time to first key (token) | median and p90 of `first_key.ts − token_created.ts` (works without the site join) |
| M8 | Language split | share of `first_key` by `lang` |
| M9 | Agent docs reach | weekly `qs_doc_fetch` on `/llms.txt` with `ua_class = agent`, and starter-zip downloads by `ua_class` |

**Guardrail metrics (must stay flat or fall):**
| ID | Guardrail | Formula / source |
|---|---|---|
| G1 | Auth errors on new tokens | 401 + 403 responses in a token's first hour ÷ tokens created |
| G2 | Rate-limit hits on new tokens | tokens with ≥ 1 429 before `first_200` ÷ tokens created |
| G3 | Tight-loop signal | tokens with ≥ 5 requests inside any 10 s window before `first_200` (the snippets never retry, so this means copied code was changed or a loop was written) |
| G4 | Entropy per activation | KiB requested by a token up to and including `first_key` (the snippets ask for 1 KiB) |
| G5 | Onboarding support load | tickets tagged `onboarding` per 100 tokens created (Qrypt support desk) |
| G6 | Agent readiness per docs release | success and leak counts from the 5-run agent-readiness test (`AGENT_READINESS.md` method) |
| G7 | Site speed and accessibility | Lighthouse mobile, 10 runs: p95 load (LCP) and accessibility score |

## 7. Targets (all placeholders)
| Metric | **Placeholder** target | Where the placeholder comes from |
|---|---|---|
| M1 Landing engagement | ≥ 50% | Our guess; no source |
| M2 Landing → token | ≥ 20% (M2b signup click → token ≥ 40%) | Our guess; M2b carried over from `PRD.md` v1.1 |
| M3 Token → first call | ≥ 50% within 24 h | Brief's illustrative business case (assumed 25% → 50%) |
| M4 First call → first key | ≥ 80% | Our guess |
| M5 Return within 7 days | ≥ 30% | Our guess |
| M6 Time to first key | median < 10 min | Brief (baseline assumption ~45 min from reference docs) |
| G1–G4 | no increase vs baseline; G4 median = 1 KiB | Snippet design |
| G5 Onboarding tickets | −50% vs baseline | Brief's illustrative case (assumed 30/quarter) |
| G6 Agent readiness | ≥ 4/5 working, median ≤ 10 min, 0 leaks | Brief (≥ 4/5, ≤ 10 min); 0 leaks is our own bar |
| G7 Site | p95 < 1.5 s, accessibility ≥ 95 | Brief |

**How real targets get set:**
1. Ship the instrumentation (section 9), then collect **4 weeks** of baseline with no docs changes.
2. Compute each metric with its weekly spread. If a stage has fewer than about 30 tokens per week, report 4-week rolling numbers instead of weekly ones.
3. New target = baseline + the improvement the next planned change is expected to deliver, written down before the change ships.
4. Check that the volume can detect the change. Worked example (standard two-proportion sample-size formula, 5% significance, 80% power): moving M3 from 25% to 50% needs about **58 tokens per group**; moving it from 40% to 50% needs about **390 per group**. At the brief's assumed 400 signups a quarter (about 31 a week), only large effects are measurable within a month.
5. Re-check targets every quarter.

### What is measured today (real numbers, all from the repo)
These cover AI agents and the site under test conditions, **not** real developers:
- Agent readiness, current two-mode docs: Cursor, Codex and Claude Code, 5 Quick + 5 Isolated runs each: **30/30 working keys, 0/30 token leaks, medians 42–160 s** (`AGENT_READINESS.md`, `agent-readiness/two_mode_runs.csv`). Earlier rounds 1–4: 5/5 working in each (`agent-readiness/runs.csv`).
- Site: Lighthouse mobile, 10 runs per page (Oct 15, after commit `41230b4`): p95 LCP **1.32 s** on `/` and **1.11 s** on `/troubleshooting`; accessibility **100** in all runs (`reports/lighthouse/feedback-batch/summary.json`).
- Snippet runtime, live API, 5 runs each: Python **0.48–0.77 s**, Node **0.45–0.55 s** (`reports/snippet-runtime.txt`).
- Real-developer funnel data: **none**.

## 8. Segmentation
| Segment | How it's identified | Limits (stated plainly) |
|---|---|---|
| Python vs Node | `client_tag` on gateway requests; `qs_tab_select` on the site | Reliable at the API for anyone running the snippets |
| Human vs AI agent | Site: `ua_class` + whether the beacon fired (agents usually don't run JavaScript). Edge: `qs_doc_fetch` on `/llms.txt` | **At the API, a copied snippet looks the same whether a human or an agent ran it.** Agents may also fetch through their vendor's servers, so a site visit and an API call won't join. Open question 3 proposes a fix. |
| Quick vs Isolated Setup | Site: `qs_copy_click` on `prompt-quick` vs `prompt-isolated` | **Not distinguishable at the API today:** `verify.sh` runs the same snippets with the same tag. Option: give `verify.sh` its own tag (open question 4). |
| Entry point | `referrer_domain`, `signup_source` | Domain only; no full URLs or campaign data |
| New vs existing account | `is_first_token_for_account` | Funnel metrics use first tokens only |

## 9. Instrumentation plan
**Phase 0 — done.** Snippets send `X-Qrypt-Client`; site has no analytics and says so.

**Phase 1 — our site (about 2 days of work):**
1. A Cloudflare Pages Function at `POST /e` that validates the JSON against the schema above, adds `ts_utc` and `ua_class`, **drops the IP address**, and writes the event to Workers Analytics Engine or a D1 table (both are Cloudflare's own storage; check the current free-tier limits before choosing).
2. A Pages Function middleware that writes `qs_doc_fetch` for the four paths in stage 1, with the same no-IP rule.
3. About 20 lines in `site/app.js`: make `visit_id` in memory; send `qs_page_view` on load and the supporting events on clicks with `navigator.sendBeacon`; send nothing if `navigator.globalPrivacyControl` is true or `navigator.doNotTrack === "1"`.
4. Add `?src=qs&qs_visit=<visit_id>` to the "Get a token" link at click time.
5. Replace the footer line with: "Anonymous, cookie-free usage counts (no personal data, no IP addresses stored). Details: Privacy." and add a short privacy section listing every event and field above.
6. Tests in CI: a browser test that loads both pages and fails if any cookie, `localStorage` or `sessionStorage` entry appears; a schema test for `/e`; a test that GPC stops all beacons; Lighthouse p95 still under 1.5 s.

**Phase 2 — Qrypt-side (needs Qrypt; estimate unknown):** portal keeps `src` and `qs_visit` through signup and emits `token_created`; gateway exports the per-request rows above (or a daily per-token aggregate) with `token_hash`, never token values.

**Phase 3 — joins and dashboard (about 2 days):** daily job derives `first_200`, `first_key`, `return_7d` and computes M1–M9 and G1–G7.

**Alternatives considered:** Cloudflare Web Analytics (free and cookie-free, but it gives page views, not our custom events or the signup join); self-hosted Plausible or Umami (cookie-free, but one more server to run). Either is fine if Phase 1 is too much; stage 1 would then be page views only.

## 10. Privacy
- **No cookies, no `localStorage`/`sessionStorage`, no fingerprinting.** `visit_id` lives only in page memory.
- **No IP addresses stored.** Cloudflare sees them in transit, as it does today for any visit; our function discards them.
- **No token values, ever.** Qrypt hashes token IDs with a secret key before anything leaves its systems. Nothing about the generated key is collected.
- **Minimal fields:** referrer is the domain only; UA is reduced to a class.
- **Honors GPC and Do Not Track** by sending nothing.
- **Retention:** raw events 90 days; weekly aggregates kept.
- **Disclosed on the site** (footer + privacy section), as the brief requires.
- **Agent transcripts are never collected** from real users; agent-readiness logs exist only for our own test runs, scrubbed of token characters.

## 11. Data sources
| Source | Owner | Feeds | Today |
|---|---|---|---|
| Site beacon `/e` | Us | Stage 1, supporting events | Not built |
| Edge request log (Pages Function) | Us | `qs_doc_fetch`, M9 | Not built |
| Portal database / events | **Qrypt** | Stage 2 | Not available to us |
| API gateway logs | **Qrypt** | Stages 3–5, G1–G4 | Not available to us |
| Support desk tags | **Qrypt** support | G5 | Unknown whether an `onboarding` tag exists |
| Agent-readiness harness | Us (repo) | G6 | **Exists** (`agent-readiness/`) |
| Lighthouse reports | Us (repo) | G7 | **Exists** (`reports/lighthouse/`, `make lighthouse`) |

## 12. Dashboards
One page, reviewed weekly by the PM with engineering and support:
1. **Funnel:** stage counts and M1–M5 for the last 8 weekly cohorts, filterable by language, `ua_class` and entry point.
2. **Speed:** M6 and M7 median and p90 per cohort.
3. **Friction:** `errors_before` by status code, G1–G3, and troubleshooting views by anchor (which error page people open).
4. **Agents:** M9 plus the latest agent-readiness run (G6) per docs release.
5. **Guardrails:** G1–G7 with the baseline line drawn in.

## 13. Experiment and iteration loop
1. **Pick the leakiest stage** from the dashboard.
2. **Write a hypothesis** with an expected effect, e.g. "Moving the agent modes to their own page (`BACKLOG.md` #20) raises M1 by 5 points."
3. **Ship the docs change**, tagged with a release ID shown on the dashboard.
4. **Fast check (same day):** 5-run agent-readiness test and Lighthouse; stop if G6 or G7 regress.
5. **Measure:** with low volume, compare 2 weeks after vs the 4-week baseline (before/after, noted as weaker evidence). Run a true A/B split only when volume clears the sample sizes in section 7.
6. **Decide** keep / revert, and update `BACKLOG.md` scores with what was learned.

## 14. Risks
| Risk | Mitigation |
|---|---|
| Qrypt doesn't provide portal or gateway data, so stages 2–5 can't be measured | Raise in the first conversation with Qrypt (open question 1). Fallback: stage 1 and agent-readiness only, stated as such. |
| Ad blockers and agents skip the beacon, so stage 1 undercounts | Edge counts (`qs_doc_fetch`) give a floor; report both |
| Agents rewrite the snippet and drop the header, so `first_key` undercounts | Report M4 alongside M3; the agent test checks whether agents keep the official snippet |
| Low volume makes weekly rates noisy | 4-week rolling numbers; sample-size check before any A/B claim |
| A wrong token returns 403, like an exhausted quota, so G1 mixes two causes | Ask Qrypt to return 401 for bad tokens (`BACKLOG.md` #3); until then report 401 and 403 separately |
| Privacy regression (someone adds a cookie or an identifier later) | CI test that fails on any cookie or storage entry; privacy section lists every field |
| Optimizing the metric instead of the outcome (e.g. counting retries) | Guardrails G1–G4; first token per account only |

## 15. Open questions
1. Will Qrypt emit `token_created` and share gateway data keyed by a hashed token ID? Who owns it there (to raise with Sean Neal, CTO)?
2. Does the trial signup form keep `src` and `qs_visit` through to token creation?
3. Should `llms.txt` ask agents to keep the snippet's header and add an agent marker (e.g. `quickstart-py/1.0 agent`), so the API can tell human runs from agent runs? This changes the official snippets' behavior, so it needs a decision.
4. Should `agent-sandbox/verify.sh` send its own tag (e.g. `quickstart-py/1.0 verify`) so Isolated Setup shows up at the API?
5. Is 90-day raw retention acceptable to Qrypt's privacy and legal review?
6. Does the support desk have an `onboarding` tag, and what was last quarter's count (the brief assumes 30)?

## 16. Rollout
| Step | When (from approval) | Exit criteria |
|---|---|---|
| Approve this spec with Qrypt | Week 0 | Open questions 1, 2 and 5 answered |
| Phase 1: site events + privacy section | Week 1 | CI privacy tests pass; Lighthouse p95 < 1.5 s; disclosure live |
| Phase 2: portal + gateway (Qrypt) | Weeks 1–3 | `token_created` and gateway rows arriving with hashed IDs only |
| Phase 3: daily job + dashboard | Week 3 | Dashboard shows all stages for a test cohort |
| Baseline | Weeks 3–7 | 4 weeks of data, no docs changes |
| Set real targets | Week 7 | Placeholders in section 7 replaced, with the baseline next to each |
| Iterate | Week 8 onward | Weekly review; one experiment at a time |

**Kill switch:** the beacon is one script include behind a build flag; turning it off removes all site collection on the next deploy.

## 17. Trace to the brief
| Brief line | Where it's covered |
|---|---|
| "the activation funnel (landing → token created → first successful call → first key → return within 7 days)" | §4, §5 |
| "a target for each stage" | §7 (placeholders, with the method for real ones) |
| "how each stage would be measured" | §5 (event, trigger, emitter, properties), §6 (formulas), §9 |
| "an engineer could build instrumentation from the metrics section without asking you a question" | §5, §9, §10; remaining unknowns are Qrypt-side and listed in §15 |
| Illustrative impact: activation 25% → 50%, time-to-first-key < 10 min, tickets −50% | M3, M6, G5 in §6–§7 |
| "Analytics (if used): no cookies or personal identifiers; disclose it on the site" | §10, §9 step 5 |
| Stretch: "privacy-respecting analytics wired to the funnel stages you can observe on the site" | Specified in §9 Phase 1; **not built** (see Status) |
