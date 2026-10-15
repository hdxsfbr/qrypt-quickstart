#!/usr/bin/env bash
# Run both snippets against the mock for success, 401, 403, 429, 503 (+ missing token). Exit non-zero on any mismatch.
set -u
cd "$(dirname "$0")/.."
export QRYPT_BASE_URL="http://127.0.0.1:18787"
fail=0
check() { # lang mode expect_exit expect_text
  local lang=$1 mode=$2 code=$3 text=$4 out rc
  MOCK_MODE=$mode python3 mock/server.py 2>/dev/null & pid=$!; sleep 0.6
  if [ "$lang" = py ]; then out=$(cd quickstart/python && python3 quickstart.py 2>&1); rc=$?
  else out=$(cd quickstart/node && node quickstart.mjs 2>&1); rc=$?; fi
  kill $pid; wait $pid 2>/dev/null
  if [ $rc -eq $code ] && grep -q "$text" <<<"$out"; then echo "PASS $lang $mode -> exit $rc: $out"
  else echo "FAIL $lang $mode (exit $rc, wanted $code /$text/): $out"; fail=1; fi
}
for lang in py js; do
  export QRYPT_API_KEY=mock-token-not-secret
  check $lang success 0 "Success"
  check $lang 401 1 "401"
  check $lang 403 1 "Token invalid OR"
  check $lang 429 1 "wait 10 s or more"
  check $lang 503 1 "Try again shortly"
  check $lang 500 1 "Try again shortly"
  check $lang html 1 "non-JSON reply"
  QRYPT_BASE_URL=http://127.0.0.1:9 check $lang neterr 1 "Network error"
  QRYPT_API_KEY= check $lang success 1 "QRYPT_API_KEY is missing"
done
exit $fail
