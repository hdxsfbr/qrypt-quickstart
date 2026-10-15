# Qrypt Quickstart: Research Notes (Oct 14, 2026, 6:22 PM PT)

Files saved here: `brief_page.txt` (the full portal page text) and `pm_developer_quickstart_onboarding.md` (the portal attachment, 12.7 KB).

## 1. API facts from the official docs (with quotes)
Source A = https://docs.qrypt.com/eaas/ · Source B = https://docs.qrypt.com/faqs/

| Fact | Exact quote | Source |
|---|---|---|
| The endpoint | "https://api-eus.qrypt.com/api/v1/quantum-entropy?size={kib_entropy}" with HTTP verb GET | A |
| Size is in KiB (kibibytes, 1 KiB = 1,024 bytes), from 1 to 512, default 1 | "integer that specifies the number of kibibytes (1,024 bytes) … The minimum value is 1 and the maximum value is 512. If unspecified, the default value is one (1)." | A |
| Headers | "Include an HTTP “Accept” header field with a value of “application/json”." / "“Bearer {access_token}”" | A |
| Response shape | "two fields named “random” and “size” … array of base64-encoded strings (each of which—when decoded—contains 1,024 bytes of entropy)" | A |
| Base64 variant | "as defined in RFC 4648 §4" (standard base64, not the URL-safe kind) | A |
| Region | Only one is listed: "api-eus — Eastern United States", even though the docs say the service is "hosted in several locations worldwide" | A |
| 400 | "The request was invalid (i.e., malformed or otherwise unacceptable)." | A |
| 401 | "The access token is either invalid or has expired." | A |
| 403 | "Limit reached … has already retrieved the maximum allotment of entropy allowed for the current period." | A |
| 429 | "exceeded the maximum number of requests (30) allowed for the designated time interval (10 seconds). Please wait and try again." | A |
| 500 | "The Qrypt service has encountered an internal error. Please contact Qrypt support" | A |
| 503 | "Qrypt’s supply of entropy is temporarily insufficient … Please wait and try the request again." | A |
| Allotment is monthly | "Once the monthly entropy quota has been reached, quantum entropy service requests will return an error code of 403." | B |
| Expired token gives 401 | "After an access token expires, any quantum entropy service requests using that token will return an error code of 401." | B |
| Token is shown only once | "Qrypt only displays access tokens when they are first generated." Lost tokens: support@qrypt.com | B |
| The token is what you're billed by | "the mechanism by which your account will be charged for entropy data … treat as … a password" | B |
| Getting a token | The docs say "contact us to obtain one". The brief says portal.qrypt.com/register. Search also turned up portal.qrypt.com/trial ("Start your Qrypt trial") | A, brief |
| SDK | There is a separate Key Generation SDK (https://docs.qrypt.com/sdk/), but it is for a different product. The brief says "No SDK required". | brief |

The docs do not say what the token's lifetime is, what token types exist, how big the monthly quota is, or which rate-limit headers are returned.

## 2. Live tests (hdx-lab, Oct 14 ~6:22 PM PT)
The key and random bytes were never printed. **Usage: 1 KiB of entropy used in total.** The other calls either failed before reaching Qrypt or were rejected without returning any data.

| # | Call | Status | Body / notes | Latency |
|---|---|---|---|---|
| 0 | Six calls from Python's built-in `urllib` | **403** | Cloudflare "Error 1010: Access denied … blocked access based on your browser's signature" (error_name `browser_signature_banned`) | ~70–170 ms |
| 1 | Valid key, size=1 (curl) | 200 | `{"random":[1 string],"size":1}`, which decodes to 1024 bytes. Content-Type is application/json. **No rate-limit headers** (no X-RateLimit or Retry-After), and the server is Cloudflare. | 0.46 s |
| 2 | No Authorization header | 401 | `{"error":"Missing or malformed Authorization header (expected 'Bearer <token>')"}` | 0.21 s |
| 3 | Bad token | **403** | `{"error":"Forbidden or entropy quota reached"}` | 0.37 s |
| 4 | size=0 | 400 | `{"error":"'size' must be an integer between 1 and 512"}` | 0.12 s |
| 5 | size=513 | 400 | Same message as size=0 | 0.09 s |
| 6 | User-Agent check, no auth (no entropy used) | | `python-requests`, `node`, Node's built-in `fetch` and a custom User-Agent all get 401 (the request goes through). **`Python-urllib/*` gets 403 from Cloudflare.** | |

I skipped the wrong-Accept test because the only one I ran happened through urllib and was blocked by Cloudflare first. I did not try to trigger a 429, 500 or 503.

## 3. Where the live API disagrees with the docs or brief
1. **A bad token returns 403, not 401.** The docs and brief say 401 means an invalid or expired token. Live, 401 only means the header is missing or malformed. A wrong token gets 403 "Forbidden or entropy quota reached", the same code as running out of quota. The snippets and the troubleshooting page have to treat 403 as "bad token OR quota used up". This is a strong item for the claims table and the backlog.
2. **Python's standard library (`urllib`) is blocked** by Cloudflare's bot check, which returns an HTML or JSON 403 error 1010. Our Python snippet must use `requests` or set a custom User-Agent (the label a client sends to identify itself). An agent writing "no dependencies" Python will hit a confusing 403. This is the biggest gotcha for the agent test.
3. The official docs' curl example leaves out the `Accept` header. The brief requires it.
4. The docs say "contact us" for a token; the brief says self-register.
5. The submission section says GitHub. We're going with GitLab as decided.

## 4. Gotchas for developers and AI agents
- They may treat `size` as bytes, e.g. size=32 thinking it's 32 bytes. size is always KiB, so ask for 1 and slice off 32 bytes.
- They may use the base64 string itself as the key instead of decoding it first.
- They may pick urllib for Python, which gets blocked (see above).
- A 403 can mean either a bad token or a used-up quota, and there are no rate-limit headers, so the client has to back off on its own after a 429 rather than reading a Retry-After header.
- Error bodies are JSON of the form `{"error": "..."}`, but the Cloudflare block page is HTML or a different JSON shape. Parse defensively.
- The docs' JavaScript example uses `atob`; Node should use `Buffer.from(s,'base64')` and `crypto` with `aes-256-gcm`, including a 12-byte nonce (a one-time random value) and the auth tag.
- Node 24 is installed on the lab and has built-in fetch.
- They may reuse the same entropy bytes for two keys.

## 5. Cloudflare status
- `/user/tokens/verify` fails ("Invalid API Token") because this is an **account-owned token**. `/accounts/{id}/tokens/verify` works: **success, status active, no expiry**.
- Listing Pages projects works (success) and returns **0 projects**, so it can at least read Pages. Whether it can deploy is untested; that only shows up on the first `wrangler pages deploy` (wrangler is Cloudflare's command-line tool).

## 6. Open questions
- How big is the account's monthly quota? We can't see it; only a 403 would tell us.
- Is the 401→403 mismatch intended? It might be worth asking Sean Neal (sean@qrypt.com).
- Are there other regions? Only api-eus is documented.
- Does the real API ever return a 503 or 429 body? Their shape is unknown, so the mock server should guess `{"error":...}`.
