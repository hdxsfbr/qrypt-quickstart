// Qrypt quickstart (Node 20.12+): turn 1 KiB of quantum entropy into an AES-256-GCM key.
// No dependencies. Needs a .env file with QRYPT_API_KEY=...
import { existsSync } from "node:fs";
import { createCipheriv, createDecipheriv, randomBytes } from "node:crypto";

if (existsSync(".env")) process.loadEnvFile(".env");
const token = process.env.QRYPT_API_KEY;
const fail = (msg) => { console.error(msg); process.exit(1); };
if (!token) fail("QRYPT_API_KEY is missing. Copy .env.example to .env and paste your token from portal.qrypt.com.");
const base = process.env.QRYPT_BASE_URL ?? "https://api-eus.qrypt.com"; // override only for the mock server
// size is in KiB, not bytes: size=1 returns 1,024 bytes.
const res = await fetch(`${base}/api/v1/quantum-entropy?size=1`, { headers: {
  Authorization: `Bearer ${token}`, Accept: "application/json",
  "User-Agent": "qrypt-quickstart/1.0", "X-Qrypt-Client": "quickstart-js/1.0" } });
const errors = {
  400: "400 Bad request: size must be an integer from 1 to 512 (it counts KiB, not bytes).",
  401: "401 Missing or malformed Authorization header: it must be 'Bearer <token>'.",
  403: "403 Token invalid OR monthly quota reached. Check the token first (Qrypt returns 403 for a wrong token, not 401).",
  429: "429 Rate limited (30 requests per 10 s). Wait 10 seconds before trying again; do not retry in a loop.",
  500: "500 Qrypt internal error. Try again shortly; contact support@qrypt.com if it persists.",
  503: "503 Qrypt entropy supply is temporarily low. Try again shortly." };
if (res.status !== 200) fail(errors[res.status] ?? `Unexpected HTTP ${res.status}. See the troubleshooting page.`);
const key = Buffer.from((await res.json()).random[0], "base64").subarray(0, 32); // decode, then 32 bytes
const iv = randomBytes(12), msg = "hello, quantum entropy";
const c = createCipheriv("aes-256-gcm", key, iv), ct = Buffer.concat([c.update(msg), c.final()]);
const d = createDecipheriv("aes-256-gcm", key, iv); d.setAuthTag(c.getAuthTag());
if (Buffer.concat([d.update(ct), d.final()]).toString() !== msg) fail("Round trip failed.");
console.log("Success: AES-256-GCM round trip with a Qrypt entropy key (key not shown).");
