# PRD: Developer Quickstart & Onboarding Funnel for Qrypt Quantum Entropy

Owner: Andre Batista (PM) · Status: Draft v1 · Date: Oct 14, 2026 · Reading time: about 10 minutes

## Glossary
- **Entropy:** truly random bytes. Qrypt's comes from quantum measurements.
- **KiB (kibibyte):** 1,024 bytes. The API's `size` parameter counts KiB, *not* bytes.
- **Base64:** a way of writing binary data as text. Every API block has to be decoded before you use it.
- **AES-256-GCM:** a standard encryption method. It uses a 32-byte key and also detects tampering.
- **Activation:** the point where a new developer gets real value. For us, that's a working key.
- **Funnel:** the ordered steps from first visit to activation, with how many people drop off at each one.
- **AI coding agent:** a tool such as Claude Code, Cursor or Codex that writes and runs code from a prompt.
- **llms.txt:** a plain-text copy of the docs that AI agents can read easily.
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
**Principles:**
- No cookies and no personal data.
- The visitor ID is a random ID per browser, kept in `localStorage`, and resettable.
- Server-side stages use a **hashed token ID** (SHA-256 of the token's ID, never the token itself).
- All events go to one table: `funnel_events(event, anon_id, token_hash, ts_utc, props_json)`.
- Targets are illustrative and should be set again after 4 weeks of baseline data.

| # | Stage | Event and exact definition | How it's measured | Target |
|---|---|---|---|---|
| 1 | **Landing** | `qs_page_view`: a page load of `/quickstart` or `/llms.txt`, with props `{path, referrer_domain, ua_class: human\|agent}` | A static-site beacon (a small no-cookie request) to `/e`. `/llms.txt` hits come from CDN logs. `ua_class=agent` when the User-Agent matches a maintained list of agent/bot patterns. | Baseline only: count weekly unique `anon_id`s |
| 2 | **Token created** | `token_created`: the portal issues an Entropy token. Props are `{token_hash, signup_source}`, with `signup_source` taken from a `?src=qs` link parameter on the quickstart's "Get a token" button. | Portal backend emits it when the token is created. Joined to stage 1 through `src=qs` plus `anon_id`, passed along in the signup URL. | ≥ 40% of stage-1 visitors arriving with `src=qs` |
| 3 | **First successful call** | `first_200`: the first HTTP 200 from `/quantum-entropy` for a `token_hash`. | API gateway logs: `min(ts)` where `status=200`, grouped by `token_hash`. Also record the non-200s per token before the first 200 (by status code), which show where friction is. | ≥ 50% of tokens created, within 24 hours of creation (versus the assumed 25%) |
| 4 | **First key** | `first_key`: the quickstart snippet completes the AES-GCM round trip. | Snippets send a request header `X-Qrypt-Client: quickstart-py/1.0` or `quickstart-js/1.0`. A 200 that carries this header counts as a first key, since the snippet only succeeds when the round trip works. There's no extra network call and nothing about the key is ever sent. The proxy measure is the share of first-200s that have the header. | ≥ 80% of stage 3. Median from `qs_page_view` to `first_key` under 10 minutes, measured where `anon_id` and `token_hash` are joined. |
| 5 | **Return within 7 days** | `return_7d`: any 200 for the same `token_hash` between 24 hours and 7 days after `first_200`, **without** the quickstart header (meaning real integration use). | Gateway logs, as a daily batch job | ≥ 30% of stage 4 |

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
- A 10-item RICE backlog, and a claims-to-source table (`docs/claims-to-source.md`).

## 6. Out of scope
- A full SDK in any language.
- Changes to the Qrypt API or portal. We document current behavior and file the 403/401 mismatch as a backlog item.
- Building the analytics pipeline itself. This PRD specifies it, and the site ships at most a cookie-free beacon (stretch goal).
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
**Why Isolated Setup exists:** in our agent-readiness tests, unrestricted agents read part of `.env` in 14 of 15 runs despite two doc revisions. Isolated Setup keeps the token off the agent container and runs live verification as fixed snippets on the host (`agent-sandbox/verify.sh`).
**What we are not claiming:** Docker does not guarantee zero leakage. Isolation boundaries (no token in agent env/FS, no docker.sock, `run.sh` refuses a project that contains `.env`) are tested by `agent-sandbox/test-isolation.sh`. Container escapes, compromised agent binaries and reckless `SANDBOX_DOCKER_ARGS` are out of scope.

## 8. Risks and mitigations
| Risk | Mitigation |
|---|---|
| A bad token returns 403, so users mistake it for quota exhaustion | The snippet message says "token invalid **or** quota reached: check the token first". The troubleshooting page explains this, and there's a backlog item asking Qrypt to return 401. |
| Cloudflare bot rules change and block `requests` or Node too | Snippets send an explicit User-Agent (`qrypt-quickstart/1.0`), and CI includes a monthly live smoke test (one cheap automated check against the real API). |
| No rate-limit headers, so agents retry tightly and hit 429 | Snippets never retry automatically, and the docs say "wait 10 seconds; the limit is 30 requests per 10 seconds". |
| The quota is undocumented, and the test budget is ≤ 10 MB | Each run uses 1 KiB, CI uses the mock server only, and we log total live usage. |
| Keys leak through logs or recordings | Snippets never print keys, `.env` is gitignored, and recordings mask the token. |
| Docs drift away from the API | The claims-to-source table records whether each claim was verified live, and we re-check it each release. |
| Unrestricted agents read `.env` by reflex | Quick Setup warns + disposable-token guidance. Isolated Setup keeps the token off the agent mount; `verify.sh` runs fixed snippets. Documented in PRD §7a. |
| Funnel joins break without cookies | We accept some loss of attribution. Stages 3–5 are server-side and exact. |

## 9. Open questions
- How big is the monthly quota per plan? It isn't documented.
- Is the bad-token 403 intended? To raise with Qrypt (Sean Neal).
- Will the portal accept a `src=qs` parameter and a `token_hash` event for stage 2?
