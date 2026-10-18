# PRD: Developer Quickstart & Onboarding Funnel for Qrypt Quantum Entropy

Owner: Andre Batista (PM) · Status: v1.2 · Date: Oct 14, 2026 (updated Oct 18) · Reading time: about 10 minutes

This is an unofficial prototype built on Qrypt's public API docs. It is not made by, affiliated with or endorsed by Qrypt.

## Glossary
- **Entropy:** truly random bytes. Qrypt's comes from quantum measurements.
- **KiB (kibibyte):** 1,024 bytes. The API's `size` parameter counts KiB, *not* bytes.
- **Base64:** a way of writing binary data as text. Every API block has to be decoded before you use it.
- **AES-256-GCM:** a standard encryption method. It uses a 32-byte key and also detects tampering.
- **Activation:** the point where a new developer gets real value. For us, that's a working key.
- **Funnel:** the ordered steps from first visit to activation, with how many people drop off at each one.
- **AI coding agent:** a tool such as Claude Code, Cursor or Codex that writes and runs code from a prompt.
- **llms.txt:** a plain-text copy of the docs that AI agents can read easily.
- **PRD:** product requirements document (this file).
- **CI:** continuous integration, tests that run automatically on every push.
- **HTTP status code:** the number a server returns, e.g. 200 = OK, 401/403 = not allowed, 429 = too many requests, 500/503 = server problem.
- **Mock server:** a fake local copy of the API used in tests, so no real token or entropy is spent.
- **RICE:** a backlog score: Reach × Impact × Confidence ÷ Effort.

## 1. Problem
Getting first value from Qrypt's entropy API currently means reading reference docs, figuring out authentication, decoding base64 blocks, and working out how to turn those bytes into a usable key. Most languages have no SDK for this. Developers who fail in their first session rarely come back. Support tickets caused by avoidable mistakes (a wrong header, mixing up units, rate limits) are pure cost.

When we tested the live API on Oct 14, 2026, we found more friction that the current docs don't mention:

| Finding | Why it hurts |
|---|---|
| A **wrong token returns 403** ("Forbidden or entropy quota reached"), not the 401 the docs promise. 401 only comes back when the header is missing or malformed. | Developers who mistype a token get told they're "out of quota" and go looking for the wrong fix. |
| Cloudflare **blocks Python's built-in `urllib`** with a 403 "Error 1010" page because of its default User-Agent (the name a client sends to identify itself). | The obvious "no dependencies" Python script fails with a misleading error, and AI agents often write exactly that script. |
| **No rate-limit headers** come back (no `Retry-After` or `X-RateLimit-*`). | Clients can't tell how long to wait after a 429. |
| The docs' **curl example leaves out `Accept: application/json`**, even though the docs list it as required. | Copy-paste drift: what the examples do doesn't match what the docs say. |
| **The quota size isn't documented.** We only know it's monthly, and you find out you've hit it from a 403. | Nobody can plan usage, and 403 is already ambiguous. |

## 2. Goal
Get a new developer, or the AI agent acting for them, from "never heard of Qrypt" to **an AES-256 key made from Qrypt entropy in under 10 minutes**, and measure whether that's happening.

### Business case (illustrative: assumptions, not real data)
- Signup → first successful call: from an **assumed 25%** to **50%**. At an **assumed 400 signups per quarter**, that's about **+100 activated developers per quarter**.
- Median time to first key: **under 10 minutes**, against an **assumed ~45 minutes** working from the reference docs alone.
- Onboarding tickets: **down 50%**. Assuming 30 per quarter, that's 15 deflected × 4 quarters × 0.5 hours × $60/hour ≈ **$1,800/year**.
These numbers need checking against real analytics once the instrumentation below is in place.

## 3. Personas and jobs-to-be-done
| Persona | Who | Job to be done | What blocks them today |
|---|---|---|---|
| **App developer, new to Qrypt** | A backend or full-stack engineer checking whether Qrypt is a good source of randomness | "When I evaluate a randomness source, I want a working key in my language within one sitting, so I can decide whether to adopt it." | Reference-style docs, no copy-paste path, unclear errors |
| **AI coding agent** | An agent acting for that developer, given a URL and one prompt | "Given only the quickstart, produce a working key without inventing APIs." | It invents SDKs, uses `urllib` (blocked), treats `size` as bytes, skips `.env` |
| **Security-minded lead** | A reviewer who has to approve the dependency | "I want to know the key handling is safe and the claims are accurate." | Marketing superlatives, no safe-handling guidance |
| **Internal: support / sales / eng** | Qrypt staff | "I want fewer avoidable tickets and clear data on where developers drop off." | No funnel data at all |

## 4. Activation funnel, targets and measurement
This section is the summary. The full specification (every event's trigger, properties and emitter, formulas, segmentation, privacy, dashboards and rollout) is in [`docs/PRD-funnel-metrics.md`](docs/PRD-funnel-metrics.md).

**Activation = a working key** (stage 4). **North Star:** weekly activated tokens, meaning tokens created in the week that reach a first key within 24 hours.

**What exists today:** only the snippet header used in stage 4 (`X-Qrypt-Client`). The site has no analytics and no cookies, and stages 2–5 need data from Qrypt's portal and API gateway. No real funnel numbers exist yet.

**Principles:**
- No cookies and no personal data.
- The visit ID is a random ID made in page memory on each page load. It is not stored in a cookie or in browser storage, so it can't follow anyone between visits.
- Server-side stages use a **hashed token ID** (a keyed hash, HMAC-SHA-256, of the token's ID, computed by Qrypt; never the token itself).
- All events go to one table: `funnel_events(event, visit_id, token_hash, ts_utc, props_json)`.
- **Every target below is a placeholder.** Real targets are set after 4 weeks of baseline data, using the method in `docs/PRD-funnel-metrics.md` §7.

| # | Stage | Event and exact definition | How it's measured | Target |
|---|---|---|---|---|
| 1 | **Landing** | `qs_page_view`: a page load of `/` or `/troubleshooting`, with props `{visit_id, path, referrer_domain, ua_class}`. `qs_doc_fetch`: any request for `/llms.txt`, `/`, `/troubleshooting` or the starter zip, JavaScript or not | A static-site beacon (a small no-cookie request) to `/e`; edge counting for `qs_doc_fetch`, which is how AI agents show up. `ua_class` (`human`, `agent`, `tool`, `bot`) comes from a maintained list of User-Agent patterns. | Placeholder: ≥ 50% of human landing visits engage (copy, tab, signup or starter click) |
| 2 | **Token created** | `token_created`: the portal issues an Entropy token. Props are `{token_hash, signup_source, signup_visit_id}`, with `signup_source` taken from a `?src=qs` link parameter on the quickstart's "Get a token" link (not built yet). | Portal backend emits it when the token is created (Qrypt-side). Joined to stage 1 through the `qs_visit` value passed along in the signup URL. | Placeholder: ≥ 20% of human landing visits (≥ 40% of "Get a token" clicks) |
| 3 | **First successful call** | `first_200`: the first HTTP 200 from `/quantum-entropy` for a `token_hash`. | API gateway logs: `min(ts)` where `status=200`, grouped by `token_hash`. Also record the non-200s per token before the first 200 (by status code), which show where friction is. | Placeholder: ≥ 50% of tokens created, within 24 hours of creation (versus the brief's assumed 25%) |
| 4 | **First key** | `first_key`: the quickstart snippet completes the AES-GCM round trip. | Snippets send a request header `X-Qrypt-Client: quickstart-py/1.0` or `quickstart-js/1.0`. A 200 that carries this header counts as a first key, since the snippet only succeeds when the round trip works. There's no extra network call and nothing about the key is ever sent. The proxy measure is the share of first-200s that have the header. | Placeholder: ≥ 80% of stage 3. Median from `qs_page_view` to `first_key` under 10 minutes, measured where `visit_id` and `token_hash` are joined. |
| 5 | **Return within 7 days** | `return_7d`: any 200 for the same `token_hash` between 24 hours and 7 days after `first_200`, **without** the quickstart header (meaning real integration use). | Gateway logs, as a daily batch job | Placeholder: ≥ 30% of stage 4 |

**Guardrail metrics, which should stay flat or go down:**
- 401/403 rate per new token in its first hour.
- 429 count per new token.
- Onboarding support tickets tagged `onboarding` (target −50%).
- AI-agent success rate on the readiness test (≥ 4/5 runs, median ≤ 10 minutes).

**Dashboard:** one weekly funnel chart with stage-to-stage conversion, split by `ua_class` and by snippet language.

## 5. Scope (this deliverable)
- Python and Node quickstart snippets, ≤ 25 lines each. Python uses `requests`, because `urllib` is blocked. Each snippet:
  - reads `QRYPT_API_KEY` from `.env`
  - fetches 1 KiB of entropy
  - uses 32 bytes as the AES-256 key
  - runs an AES-GCM round trip and prints a success line, never the key
  - prints a clear message for a missing token and for 400/401/403/429/500/503, and exits non-zero without retrying in a loop
- CI runs both snippets on every push against a mock server: success, 401, 429 and 503.
- A static site with language tabs, copy buttons, a stated "about 5 minutes" target, a troubleshooting page (symptom → likely cause → fix for every code, plus the common mistakes), and `llms.txt`.
- Two agent onboarding modes: **Quick Setup** (default, no Docker, behavioral safeguards + security warnings) and **Isolated Setup** (`agent-sandbox/`, Docker, trusted host-side `verify.sh`).
- An agent-readiness test: 2 rounds × 5 runs, with a failure taxonomy (the categories of failure) mapped to doc fixes.
- **Optional key fingerprint, kept outside the core snippets.** The brief caps each snippet at 25 lines (excluding comments and imports), and a grader can count them, so the core files stay within that limit. The page shows a separate, clearly labeled optional block (2–3 lines per language) that prints the first 8 hex characters of SHA-256(key), so a user can see the key change between runs without exposing it. A "For production" note shows mixing Qrypt bytes with local randomness via HKDF (HMAC-based Key Derivation Function).
- A downloadable starter archive (`/qrypt-quickstart-starter.zip`) built by `make site` from the exact repo files (snippets, mock server and tests, `requirements.txt`, `.env.example`, `AGENTS.md`, `Makefile`, `agent-sandbox/`). CI checks it matches the repo byte for byte and holds no `.env` or token, because the GitLab repo is private and the page otherwise pointed to files readers could not get.
- A RICE-scored backlog (21 items: 16 open, 5 done), and a claims-to-source table (`docs/claims-to-source.md`).
- A funnel-metrics specification (`docs/PRD-funnel-metrics.md`). The instrumentation itself is not built (see Out of scope).

## 6. Out of scope
- A full SDK in any language.
- Changes to the Qrypt API or portal. We document current behavior and file the 403/401 mismatch as a backlog item.
- Building the analytics pipeline itself. `docs/PRD-funnel-metrics.md` specifies it. The site currently ships **no** analytics at all; the cookie-free beacon is a specified, unbuilt stretch goal.
- Regions other than `api-eus`, the only one documented.
- Qrypt's key-generation SDK product.

## 7. The tradeoff we are explicitly not making: no full SDK this quarter
**The choice:** we ship 25-line copy-paste snippets and agent-readable docs instead of official SDK packages.
**Why:**
1. The API is a single GET request. An SDK would wrap about 10 lines of code, but cost ongoing releases, security patches and version support in every language.
2. AI agents work best from plain HTTP examples. Packages that are new or rarely used are exactly what agents hallucinate (make up).
3. Snippets let us measure the funnel now. If the data shows SDK demand (for example, repeated tickets about the same wrapper logic), we revisit it next quarter.
**What we give up:** typed errors, built-in retries and a one-line install. We make up for part of that with clear error messages and troubleshooting docs.


## 7a. The tradeoff we are explicitly making: zero-install agent onboarding first
> We prioritize a zero-install agent onboarding path for developer accessibility, while offering an optional sandboxed workflow for users requiring stronger credential isolation. Quick Setup relies on behavioral safeguards and cannot guarantee that existing credentials will remain inaccessible to unrestricted agents.

**Why Quick Setup is the default:** most evaluators will not install Docker for a 10-minute trial. A copy-pasteable prompt unblocks Claude Code, Codex and Cursor immediately.
**Why Isolated Setup exists:** in our first agent-readiness rounds, Cursor (with no restrictions) printed part of `.env` in 14 of 15 runs despite two doc revisions. **Result after the redesign (Oct 15):** Cursor, Codex and Claude Code each ran 5 Quick and 5 Isolated runs: 30/30 produced a working key and 0/30 leaked the token. Quick Setup still depends on the agent following instructions; only Isolated Setup physically blocks access. Isolated Setup keeps the token off the agent container and runs live verification as fixed snippets on the host (`agent-sandbox/verify.sh`).
**What we are not claiming:** Docker does not guarantee zero leakage. Isolation boundaries (no token in agent env/FS, no docker.sock, `run.sh` refuses a project that contains `.env`) are tested by `agent-sandbox/test-isolation.sh`. Container escapes, compromised agent binaries and reckless `SANDBOX_DOCKER_ARGS` are out of scope.

## 8. Risks and mitigations
| Risk | Mitigation |
|---|---|
| A bad token returns 403, so users mistake it for quota exhaustion | The snippet message says "token invalid **or** quota reached: check the token first". The troubleshooting page explains this, and there's a backlog item asking Qrypt to return 401. |
| Cloudflare bot rules change and block `requests` or Node too | Snippets send an explicit User-Agent (`qrypt-quickstart/1.0`). A scheduled live smoke test (one cheap automated check against the real API) is proposed, not built: CI uses the mock only, to protect the 10 MB budget. |
| No rate-limit headers, so agents retry tightly and hit 429 | Snippets never retry automatically, and the docs say "wait 10 seconds; the limit is 30 requests per 10 seconds". |
| The quota is undocumented, and the test budget is ≤ 10 MB | Each run uses 1 KiB, CI uses the mock server only, and we log total live usage. |
| Keys leak through logs or recordings | Snippets never print keys, `.env` is gitignored, and recordings mask the token. |
| Docs drift away from the API | The claims-to-source table records whether each claim was verified live, and we re-check it each release. |
| Unrestricted agents read `.env` by reflex | Quick Setup warns + disposable-token guidance. Isolated Setup keeps the token off the agent mount; `verify.sh` runs fixed snippets. Documented in PRD §7a. |
| Funnel joins break without cookies | We accept some loss of attribution. Stages 3–5 are server-side and exact. |

## 9. Open questions
- How big is the monthly quota per plan? It isn't documented.
- Is the bad-token 403 intended? To raise with Qrypt (Sean Neal).
- Will the portal accept a `src=qs` parameter and a `token_hash` event for stage 2? (Full list: `docs/PRD-funnel-metrics.md` §15.)

## 10. Submission documents
| Document | What it holds |
|---|---|
| `README.md` | Grader quick-start (under 5 minutes), one-line description, how to build the site and rerun the agent test |
| `PRD.md` | This document |
| `AGENT_READINESS.md` | All agent-test rounds (5 runs each), failure taxonomy (the types of failure) and the doc fix for each |
| `BACKLOG.md` | 21 follow-ups (16 open, 5 done) scored with RICE |
| `docs/PRD-funnel-metrics.md` | Full funnel and metrics specification: events, formulas, placeholder targets, privacy, rollout |
| `docs/claims-to-source.md` | Every factual claim about Qrypt, with its official source and live check |
| `AI_USAGE.md` | AI tools used, exact agent-test prompt, and corrected AI-drafted claims |
| `docs/REQUIREMENTS_TRACE.md` | Each brief requirement mapped to evidence |
| Site | https://qrypt-quickstart.pages.dev/ (quickstart, `/troubleshooting.html`, `/llms.txt`) |
| Video (≤ 5 min) | 3:21. Fresh quickstart run, a 401 troubleshooting path, this funnel, one agent run (`docs/demo-script.md`) |
