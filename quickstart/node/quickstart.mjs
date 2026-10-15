// Qrypt quickstart (Node 20.12+): 1 KiB of quantum entropy -> AES-256-GCM key.
// No dependencies. Put QRYPT_API_KEY=<your token> in a .env file here.
import assert from "node:assert";
import { existsSync } from "node:fs";
import { createCipheriv, createDecipheriv, randomBytes } from "node:crypto";

const API = process.env.QRYPT_BASE_URL ?? "https://api-eus.qrypt.com"; // mock

// One friendly message per failure. We never retry automatically.
const HELP = { 400: "400: size must be 1-512. It counts KiB, not bytes.",
  missing: "QRYPT_API_KEY is missing: add to .env. Token: portal.qrypt.com",
  network: "Network error or non-JSON reply: check proxy/TLS, retry soon.",
  401: "401: Authorization header missing, malformed or expired.",
  403: "403: Token invalid OR monthly quota used. Check the token first.",
  429: "429: rate limited. Live can return 429 about 1 s after a single " +
    "prior call; wait 10 s or more and never loop." };
// 500, 503 and anything else: Qrypt is busy or erroring, so try again later.
const fail = (msg) => { console.error(msg); process.exit(1); };

// Step 1: read the token from .env. Never print or log it.
if (existsSync(".env")) process.loadEnvFile(".env");
const token = process.env.QRYPT_API_KEY || fail(HELP.missing);

// Step 2: fetch 1 KiB of entropy (size counts KiB, not bytes).
const headers = { Authorization: `Bearer ${token}`, Accept: "application/json",
  "User-Agent": "qrypt-quickstart/1.0", "X-Qrypt-Client": "quickstart-js/1.0" };
const url = `${API}/api/v1/quantum-entropy?size=1`;
const res = await fetch(url, { headers }).catch(() => fail(HELP.network));
if (res.status !== 200) fail(HELP[res.status] ??
  `${res.status}: Qrypt is busy or erroring. Try again shortly.`);
const body = await res.json().catch(() => fail(HELP.network));

// Step 3: decode first, then keep 32 bytes as the AES-256 key.
const key = Buffer.from(body.random[0], "base64").subarray(0, 32);

// Step 4: encrypt and decrypt a sample message with AES-256-GCM.
const GCM = "aes-256-gcm", iv = randomBytes(12), message = "hello, quantum";
const enc = createCipheriv(GCM, key, iv);
const sealed = Buffer.concat([enc.update(message, "utf8"), enc.final()]);
const dec = createDecipheriv(GCM, key, iv).setAuthTag(enc.getAuthTag());
assert.equal(dec.update(sealed, null, "utf8") + dec.final("utf8"), message);
console.log("Success: AES-256-GCM round trip with a Qrypt key (not shown).");
