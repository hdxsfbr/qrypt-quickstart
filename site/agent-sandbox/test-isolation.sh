#!/usr/bin/env bash
# Prove the Isolated Setup boundaries without using any real token.
# Run from repo root or agent-sandbox/: exits 0 only if every probe passes.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/.." && pwd)
tag=$( (sha256sum "$here/Dockerfile" 2>/dev/null || shasum -a 256 "$here/Dockerfile") | cut -c1-12)
img="qrypt-agent-sandbox:$tag"
docker image inspect "$img" >/dev/null 2>&1 || docker build -q -t "$img" "$here" >/dev/null
# The image must run as agent with no secret-handling entrypoint or helper.
old=$(docker run --rm --entrypoint sh "$img" -c 'ls /usr/local/bin/entrypoint.sh /usr/local/bin/qrypt-run /usr/local/bin/qrypt-run-inner /etc/sudoers.d/qrypt 2>/dev/null | wc -l; id -un')
[ "$old" = "$(printf '0\nagent')" ] && echo "PASS image ($img) runs as agent with no secret entrypoint or helper" \
  || { echo "FAIL image ($img) has a secret entrypoint/helper or wrong user; rebuild it: $old"; exit 1; }

fail=0
pass() { echo "PASS $*"; }
bad()  { echo "FAIL $*"; fail=1; }

# 1) run.sh refuses a project that already contains .env
proj=$(mktemp -d); echo 'QRYPT_API_KEY=should-never-enter' > "$proj/.env"
chmod 600 "$proj/.env"
if "$here/run.sh" "$proj" true 2>/tmp/sbx-refuse.txt; then
  bad "run.sh should refuse a project with .env"
else
  grep -q 'refuse' /tmp/sbx-refuse.txt && pass "run.sh refuses project with .env" \
    || bad "run.sh refused but message unclear"
fi
rm -f "$proj/.env"

# 2) Inside the agent container: no QRYPT_* in env, no .env on disk,
#    no docker.sock, and a planted "secret" outside the mount is invisible.
echo 'planted-secret-value' > /tmp/qrypt-planted-secret-$$
chmod 600 /tmp/qrypt-planted-secret-$$
out=$(docker run --rm \
  -v "$proj":/work \
  -v "$repo/quickstart":/work/quickstart:ro \
  -v "$repo/mock":/work/mock:ro \
  "$img" bash -c '
    set +e
    echo "ENV_QRYPT=$(env | grep -c ^QRYPT_ || true)"
    echo "DOTENV=$(test -e /work/.env && echo yes || echo no)"
    echo "SOCK=$(test -e /var/run/docker.sock && echo yes || echo no)"
    echo "PLANTED=$(test -e /tmp/qrypt-planted-secret-'"$$"' && echo yes || echo no)"
    echo "HOME_SSH=$(test -e /home/agent/.ssh && echo yes || echo no)"
    export QRYPT_API_KEY=mock-token-not-secret QRYPT_BASE_URL=http://127.0.0.1:18787
    python3 -m venv /tmp/v && /tmp/v/bin/pip -q install -r /work/quickstart/python/requirements.txt >/dev/null
    MOCK_MODE=success MOCK_PORT=18787 python3 /work/mock/server.py >/dev/null 2>&1 &
    pid=$!; sleep 0.6
    (cd /work/quickstart/python && /tmp/v/bin/python quickstart.py); rc=$?
    kill $pid 2>/dev/null; wait $pid 2>/dev/null
    echo "MOCK_RC=$rc"
  ')
rm -f /tmp/qrypt-planted-secret-$$
grep -q 'ENV_QRYPT=0' <<<"$out" && pass "no QRYPT_* in agent env" || bad "QRYPT_* leaked into agent env: $out"
grep -q 'DOTENV=no'   <<<"$out" && pass "no .env inside agent FS" || bad ".env visible in agent FS"
grep -q 'SOCK=no'     <<<"$out" && pass "no docker.sock" || bad "docker.sock exposed"
grep -q 'PLANTED=no'  <<<"$out" && pass "host secret outside mount invisible" || bad "planted host secret visible"
grep -q 'HOME_SSH=no' <<<"$out" && pass "no host SSH dir" || bad "SSH dir present"
grep -q 'MOCK_RC=0'   <<<"$out" && pass "agent can run mock success" || bad "mock success failed: $out"

# 3) verify.sh refuses a world-readable env file and accepts a 600 file with a
#    fake token against the mock (no live bytes).
fake=$(mktemp); echo 'QRYPT_API_KEY=fake' > "$fake"; chmod 644 "$fake"
if "$here/verify.sh" --env "$fake" --lang py 2>/tmp/v-mode.txt; then
  bad "verify.sh should refuse mode 644"
else
  grep -qi 'mode\|chmod\|refusing' /tmp/v-mode.txt && pass "verify.sh refuses mode 644" \
    || bad "verify.sh mode check message unclear"
fi
chmod 600 "$fake"
rm -f "$fake"
# Mock-backed verify (no live bytes): fixed snippets + sanitized PASS line.
fake=$(mktemp); printf 'QRYPT_API_KEY=mock-token-not-secret\n' > "$fake"; chmod 600 "$fake"
MOCK_MODE=success MOCK_PORT=18787 python3 "$repo/mock/server.py" >/dev/null 2>&1 & mpid=$!
sleep 0.5
if out=$("$here/verify.sh" --env "$fake" --lang both --base-url http://127.0.0.1:18787 2>&1); then
  echo "$out" | grep -q 'PASS' && pass "verify.sh mock PASS (sanitized)" || bad "verify mock output: $out"
else
  bad "verify.sh mock failed: $out"
fi
kill $mpid 2>/dev/null || true; wait $mpid 2>/dev/null || true
# Output must never contain the mock token string either (habit check).
echo "$out" | grep -q 'mock-token' && bad "verify.sh echoed a token-shaped value" || pass "verify.sh output has no token"
rm -f "$fake"

# 4) Confirm no script passes the token into the container (no QRYPT_DOTENV).
if grep -RIn 'QRYPT_DOTENV' "$here" --include='*.sh' --include='Dockerfile' --include='entrypoint*' 2>/dev/null | grep -v test-isolation; then
  bad "QRYPT_DOTENV still present (agent must not receive the token)"
else
  pass "no QRYPT_DOTENV secret-passing path"
fi

rm -rf "$proj"
exit $fail
