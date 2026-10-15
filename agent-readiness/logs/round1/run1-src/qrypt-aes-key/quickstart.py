# Qrypt quickstart (Python): turn 1 KiB of quantum entropy into an AES-256-GCM key.
# Needs: pip install -r requirements.txt  and a .env file with QRYPT_API_KEY=...
import base64, os, sys
import requests
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

load_dotenv()
token = os.getenv("QRYPT_API_KEY")
if not token:
    sys.exit("QRYPT_API_KEY is missing. Copy .env.example to .env and paste your token from portal.qrypt.com.")
base = os.getenv("QRYPT_BASE_URL", "https://api-eus.qrypt.com")  # override only for the mock server
# size is in KiB, not bytes: size=1 returns 1,024 bytes. A custom User-Agent avoids Cloudflare's urllib block.
r = requests.get(f"{base}/api/v1/quantum-entropy", params={"size": 1}, timeout=15, headers={
    "Authorization": f"Bearer {token}", "Accept": "application/json",
    "User-Agent": "qrypt-quickstart/1.0", "X-Qrypt-Client": "quickstart-py/1.0"})
errors = {
    400: "400 Bad request: size must be an integer from 1 to 512 (it counts KiB, not bytes).",
    401: "401 Missing or malformed Authorization header: it must be 'Bearer <token>'.",
    403: "403 Token invalid OR monthly quota reached. Check the token first (Qrypt returns 403 for a wrong token, not 401).",
    429: "429 Rate limited (30 requests per 10 s). Wait 10 seconds before trying again; do not retry in a loop.",
    500: "500 Qrypt internal error. Try again shortly; contact support@qrypt.com if it persists.",
    503: "503 Qrypt entropy supply is temporarily low. Try again shortly."}
if r.status_code != 200:
    sys.exit(errors.get(r.status_code, f"Unexpected HTTP {r.status_code}. See the troubleshooting page."))
key = base64.b64decode(r.json()["random"][0])[:32]  # decode first, then take 32 bytes = AES-256 key
nonce, message = os.urandom(12), b"hello, quantum entropy"
aes = AESGCM(key)
assert aes.decrypt(nonce, aes.encrypt(nonce, message, None), None) == message
print("Success: AES-256-GCM round trip with a Qrypt entropy key (key not shown).")
