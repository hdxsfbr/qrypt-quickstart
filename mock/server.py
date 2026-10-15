"""Mock Qrypt entropy API for CI. Stdlib only.
MOCK_MODE: success | 401 | 403 | 429 | 500 | 503 (default success). Also honors real-API rules
(missing/malformed Bearer -> 401, size outside 1..512 -> 400)."""
import base64, json, os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

MODE = os.getenv("MOCK_MODE", "success")
BODIES = {"401": "Missing or malformed Authorization header (expected 'Bearer <token>')",
          "403": "Forbidden or entropy quota reached", "429": "Too many requests",
          "500": "Internal server error", "503": "Entropy supply temporarily insufficient"}

class H(BaseHTTPRequestHandler):
    def send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/healthz": return self.send(200, {"status": "ok"})
        if u.path != "/api/v1/quantum-entropy": return self.send(404, {"error": "not found"})
        if MODE in BODIES: return self.send(int(MODE), {"error": BODIES[MODE]})
        if not self.headers.get("Authorization", "").startswith("Bearer "): return self.send(401, {"error": BODIES["401"]})
        size = parse_qs(u.query).get("size", ["1"])[0]
        if not size.isdigit() or not 1 <= int(size) <= 512:
            return self.send(400, {"error": "'size' must be an integer between 1 and 512"})
        self.send(200, {"random": [base64.b64encode(os.urandom(1024)).decode() for _ in range(int(size))], "size": int(size)})
    def log_message(self, fmt, *a):  # log method/path/status only, never headers (tokens)
        sys.stderr.write("mock: %s\n" % (fmt % a))

if __name__ == "__main__":
    HTTPServer(("127.0.0.1", int(os.getenv("MOCK_PORT", "18787"))), H).serve_forever()
