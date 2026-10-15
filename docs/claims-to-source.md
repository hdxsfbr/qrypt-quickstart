# Claims-to-Source Table

Every factual claim about Qrypt in this repo and on the site, with its source. **Live** means we checked it against the real API on Oct 14, 2026 (PT), using 1 KiB of entropy in total.

A = https://docs.qrypt.com/eaas/ · F = https://docs.qrypt.com/faqs/ · B = project brief (`docs/brief/`)

| # | Claim | Source | Quote | Verified live |
|---|---|---|---|---|
| 1 | Endpoint is `GET https://api-eus.qrypt.com/api/v1/quantum-entropy?size={n}` | A | "Use the following URL: https://api-eus.qrypt.com/api/v1/quantum-entropy?size={kib_entropy}" … "HTTP Verb: GET" | Yes (200) |
| 2 | `size` is in KiB (1,024 bytes) | A | "the number of kibibytes (1,024 bytes) of entropy being requested" | Yes (size=1 returned 1,024 bytes) |
| 3 | `size` ranges from 1 to 512 | A | "The minimum value is 1 and the maximum value is 512." | Yes: 0 and 513 returned 400 "'size' must be an integer between 1 and 512" |
| 4 | Default size is 1 | A | "If unspecified, the default value is one (1)." | No |
| 5 | Send `Accept: application/json` | A | "Include an HTTP “Accept” header field with a value of “application/json”." | Yes (sent; not tested without it) |
| 6 | Auth header is `Authorization: Bearer <token>` | A | "“Bearer {access_token}”" | Yes |
| 7 | Response is `{"random":[…], "size": n}` | A | "two fields named “random” and “size”" | Yes |
| 8 | Each `random` string decodes to 1,024 bytes | A | "each of which—when decoded—contains 1,024 bytes of entropy" | Yes |
| 9 | Standard base64 (RFC 4648 §4) | A | "base64-encoded strings (as defined in RFC 4648 §4, Base 64 Encoding)" | Yes (decoded with standard base64) |
| 10 | Calls use HTTPS | A | "all calls are made using an encrypted HTTPS connection" | Yes |
| 11 | Documented region: `api-eus`, Eastern US | A | "api-eus — Eastern United States" | Yes (api-eus works) |
| 12 | 400 means a malformed request | A | "The request was invalid (i.e., malformed or otherwise unacceptable)." | Yes |
| 13 | 401 means an invalid or expired token | A, F | "The access token is either invalid or has expired." | **Contradicted:** a bad token gave 403. 401 only appears when the header is missing or malformed: `{"error":"Missing or malformed Authorization header (expected 'Bearer <token>')"}` |
| 14 | 403 means the allotment is used up for the period | A | "has already retrieved the maximum allotment of entropy allowed for the current period" | Partly: a bad token *also* returns 403 `{"error":"Forbidden or entropy quota reached"}` |
| 15 | The allotment period is monthly | F | "Once the monthly entropy quota has been reached, quantum entropy service requests will return an error code of 403." | No |
| 16 | 429 means more than 30 requests per 10 seconds | A | "exceeded the maximum number of requests (30) allowed for the designated time interval (10 seconds)" | **Stricter live:** Oct 14 ~6:58 PM PT, a 429 came back about 1 s after a single prior call (2nd request total). Retry after 15 s gave 200. Guidance: wait 10 s or more, never loop. |
| 17 | 500 means an internal error; contact support | A | "The Qrypt service has encountered an internal error. Please contact Qrypt support" | No |
| 18 | 503 means not enough entropy supply; retry later | A | "Qrypt’s supply of entropy is temporarily insufficient … Please wait and try the request again." | No |
| 19 | Tokens are shown only once | F | "Qrypt only displays access tokens when they are first generated." | No |
| 20 | Treat tokens like passwords; your account is billed by token | F | "the mechanism by which your account will be charged for entropy data … treated as secure and secret information" | No |
| 21 | Expired tokens return 401 | F | "After an access token expires, any quantum entropy service requests using that token will return an error code of 401." | No |
| 22 | Get a token at portal.qrypt.com/register | B | "create an account at https://portal.qrypt.com/register and generate an access token for the Entropy service" (the official docs say "contact us to obtain one") | No |
| 23 | No SDK is needed for the entropy API | B | "No SDK required. Call the REST endpoint directly from any language." | Yes (plain HTTP works) |

## Observed behavior not covered by the docs (live, Oct 14, 2026)
| Observation | Evidence |
|---|---|
| Cloudflare blocks the `Python-urllib/*` User-Agent | 403 "Error 1010: Access denied … browser_signature_banned". `python-requests`, `node`, curl and custom User-Agents all passed. |
| No rate-limit headers on a 200 | No `Retry-After` or `X-RateLimit-*` headers in the response |
| Error bodies are JSON `{"error":"…"}` | Seen on the 400, 401 and 403 responses |
| The docs' curl example leaves out the `Accept` header | Compare with Request table in A |
| Live 429 after one prior call | `make live-js` got 429 ~1 s after `make live-py` (Oct 14, 2026 ~6:58 PM PT); 200 after waiting 15 s. See `reports/live-usage.log`. |
| Quota size isn't documented | Not stated in A or F |
