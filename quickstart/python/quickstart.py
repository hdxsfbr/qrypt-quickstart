# Qrypt quickstart (Python): 1 KiB of quantum entropy -> AES-256-GCM key.
# Setup: pip install requests cryptography python-dotenv
# Then put QRYPT_API_KEY=<your token> in a .env file next to this script.
import base64
import os
import sys

import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

API = os.getenv("QRYPT_BASE_URL", "https://api-eus.qrypt.com")  # mock override

# One friendly message per failure. We never retry automatically.
HELP = {400: "400: size must be 1-512. It counts KiB, not bytes.",
        None: "QRYPT_API_KEY is missing: add to .env. Token: portal.qrypt.com",
        401: "401: Authorization header missing, malformed or expired.",
        403: "403: Token invalid OR monthly quota used. Check the token first.",
        429: "429: rate limited. Live can return 429 about 1 s after a single "
             "prior call; wait 10 s or more and never loop."}
# 500, 503 and anything else: Qrypt is busy or erroring, so try again later.

# Step 1: read the token from .env. Never print or log it.
load_dotenv()
token = os.getenv("QRYPT_API_KEY") or sys.exit(HELP[None])

# Step 2: fetch 1 KiB of entropy. A custom User-Agent avoids Cloudflare's
# block on Python's urllib; X-Qrypt-Client tags quickstart traffic.
headers = {
    "Authorization": f"Bearer {token}", "Accept": "application/json",
    "User-Agent": "qrypt-quickstart/1.0", "X-Qrypt-Client": "quickstart-py/1.0"}
try:
    resp = requests.get(f"{API}/api/v1/quantum-entropy", params={"size": 1},
                        headers=headers, timeout=15)
    if resp.status_code != 200:
        sys.exit(HELP.get(resp.status_code, f"{resp.status_code}: Qrypt is "
                          "busy or erroring. Try again shortly."))
    entropy_b64 = resp.json()["random"][0]
except (requests.RequestException, ValueError):
    sys.exit("Network error or non-JSON reply: check proxy/TLS, retry soon.")

# Step 3: decode first, then keep 32 bytes as the AES-256 key.
key = base64.b64decode(entropy_b64)[:32]

# Step 4: encrypt and decrypt a sample message with AES-256-GCM.
aes, nonce, message = AESGCM(key), os.urandom(12), b"hello, quantum entropy"
assert aes.decrypt(nonce, aes.encrypt(nonce, message, None), None) == message
print("Success: AES-256-GCM round trip with a Qrypt key (not shown).")
