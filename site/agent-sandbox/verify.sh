#!/usr/bin/env bash
# Trusted live verification. Runs OUTSIDE the agent container.
# Loads QRYPT_API_KEY from a .env the agent cannot see, then runs FIXED
# snippets from this repo (never agent-modifiable code) against the live API.
# Prints only a sanitized success/failure line. Never prints the token, the
# entropy, or the key.
#
# Usage:
#   agent-sandbox/verify.sh --env ~/.config/qrypt/.env [--lang py|js|both]
#
# The --env path MUST NOT be inside a directory the agent container mounts.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/.." && pwd)
envf=""; lang=both; base=""
while [ $# -gt 0 ]; do
  case "$1" in
    --env) envf=$(realpath "${2:?}"); shift 2;;
    --lang) lang=${2:?}; shift 2;;
    --base-url) base=${2:?}; shift 2;;
    *) echo "usage: verify.sh --env <path> [--lang py|js|both]" >&2; exit 2;;
  esac
done
[ -n "$envf" ] && [ -f "$envf" ] || { echo "verify.sh: --env <existing-file> is required" >&2; exit 2; }
# Optional: point at the mock server (CI / dry-run). Live is the default.
[ -n "$base" ] && export QRYPT_BASE_URL="$base"

# Refuse if the env file is world-readable or owned oddly (mode must be 600/400).
mode=$(stat -c '%a' "$envf" 2>/dev/null || stat -f '%Lp' "$envf")
case "$mode" in 600|400|0400|0600) ;; *)
  echo "verify.sh: refusing $envf (mode $mode). chmod 600 it first." >&2; exit 2;;
esac

# Work in a private temp dir the agent never sees. Copy FIXED snippets only.
work=$(mktemp -d); trap 'rm -rf "$work"' EXIT
mkdir -p "$work/py" "$work/js"
cp "$repo/quickstart/python/quickstart.py" \
   "$repo/quickstart/python/requirements.txt" "$work/py/"
cp "$repo/quickstart/node/quickstart.mjs" "$work/js/"
# Place .env next to each snippet WITHOUT printing it.
cp "$envf" "$work/py/.env" && chmod 600 "$work/py/.env"
cp "$envf" "$work/js/.env" && chmod 600 "$work/js/.env"

run_one() {
  local name=$1; shift
  local out rc
  set +e
  out=$("$@" 2>&1)
  rc=$?
  set -e
  # Scrub anything that looks like a token or long base64 blob from the output
  # we show the user. Only the success/error line should remain.
  if [ $rc -eq 0 ] && grep -q '^Success:' <<<"$out"; then
    echo "verify $name: PASS (AES-GCM round trip; key not shown)"
    return 0
  fi
  # Map known friendly errors; never echo raw output (may contain headers).
  if grep -q 'QRYPT_API_KEY is missing' <<<"$out"; then
    echo "verify $name: FAIL (missing token in --env file)"; return 1
  fi
  if grep -qE '^40[013]|429|50[03]|Network error' <<<"$out"; then
    echo "verify $name: FAIL ($(grep -oE '^[0-9]{3}|Network error[^.]+' <<<"$out" | head -1))"
    return 1
  fi
  echo "verify $name: FAIL (non-zero exit; details suppressed)"
  return 1
}

fail=0
if [ "$lang" = py ] || [ "$lang" = both ]; then
  python3 -m venv "$work/py/.venv" >/dev/null
  "$work/py/.venv/bin/pip" -q install -r "$work/py/requirements.txt" >/dev/null
  run_one python "$work/py/.venv/bin/python" "$work/py/quickstart.py" || fail=1
fi
if [ "$lang" = js ] || [ "$lang" = both ]; then
  run_one node node "$work/js/quickstart.mjs" || fail=1
fi
# Log bytes used without recording the token (1 KiB per successful call).
if [ $fail -eq 0 ] && [ -z "$base" ]; then
  n=0; [ "$lang" = both ] && n=2 || n=1
  mkdir -p "$repo/reports"
  echo "live bytes: $((n * 1024)) (verify.sh $(date -u +%Y-%m-%dT%H:%MZ))" \
    >> "$repo/reports/live-usage.log"
fi
exit $fail
