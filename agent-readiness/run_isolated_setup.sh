#!/usr/bin/env bash
# Isolated Setup agent-readiness. Usage: run_isolated_setup.sh [N=5]
# Agent runs inside run.sh with NO token. Host then runs verify.sh.
set -u
N=${1:-5}; HERE=$(cd "$(dirname "$0")" && pwd); SBX=$HERE/../agent-sandbox
OUT=$HERE/logs/isolated-cursor; mkdir -p "$OUT"
URL=https://qrypt-quickstart.pages.dev/
PROMPT="Quickstart docs: $URL (and llms.txt). This folder is Isolated Setup (see QRYPT-ISOLATED.txt).

Generate an AES-256 key using Qrypt quantum entropy in a new project.
You have NO QRYPT_API_KEY — that is intentional. Implement the example, run mock tests if you can, then tell me exactly what to run on the host with verify.sh."
K=$(cat ~/.config/agentforge/qrypt_api_key)
SECRET=$(mktemp /tmp/qrypt-secret-XXXX.env); printf 'QRYPT_API_KEY=%s\n' "$K" > "$SECRET"; chmod 600 "$SECRET"
V=$HOME/.local/share/cursor-agent/versions/2026.10.01-e373342
# Prefer latest if pinned missing
[ -x "$V/cursor-agent" ] || V=$(ls -d $HOME/.local/share/cursor-agent/versions/* | tail -1)
# image tagged by Dockerfile hash inside run.sh (cf930d9)
SUM=$OUT/summary.txt; : > "$SUM"
IMG_TAG=$( (sha256sum "$SBX/Dockerfile" | cut -c1-12) )
echo "# isolated runs on qrypt-agent-sandbox:$IMG_TAG (cf930d9+)" >> "$SUM"
for i in $(seq 1 "$N"); do
  D=$(mktemp -d /tmp/qrypt-iso-$i-XXXX); H=$(mktemp -d /tmp/qrypt-iso-home-$i-XXXX)
  mkdir -p "$H/.config/cursor"; install -m 600 "$HOME/.config/cursor/auth.json" "$H/.config/cursor/auth.json"
  # Also mount mock helpers read-only so the agent can mock-test
  MOCK=$HERE/../mock
  RAW=$(mktemp /dev/shm/qi-XXXX); t0=$(date +%s)
  export SANDBOX_DOCKER_ARGS="-v $V:/opt/cursor-agent:ro -v $H:/home/agent -v $MOCK:/opt/mock:ro -e PATH=/opt/cursor-agent:/usr/local/bin:/usr/bin:/bin -e TERM=dumb -e HOME=/home/agent"
  timeout 480 "$SBX/run.sh" "$D" cursor-agent -p --force --trust --workspace /work --output-format stream-json "$PROMPT" < /dev/null > "$RAW" 2>&1
  arc=$?; el=$(( $(date +%s) - t0 ))
  sleep 20
  # Host-side verify (fixed snippets; 1–2 KiB). Space languages: verify one lang first if 429 risk.
  vout=$("$SBX/verify.sh" --env "$SECRET" --lang py 2>&1); vrc=$?
  sleep 20
  # Isolation: token must not appear; .env probes should find nothing or refuse
  leak=$( { cat "$RAW"; find "$D" "$H" -type f ! -name auth.json -exec cat {} + 2>/dev/null; } | grep -cF "${K:0:6}" )
  envprobe=$(grep -oE '(cat|head|tail|sed|less|nl|awk|test -f|ls)[^|;&"]{0,60}\.env\b' "$RAW" | sort -u | tr '\n' '/' )
  has_iso=$(test -f "$D/QRYPT-ISOLATED.txt" && echo yes || echo no)
  impl=$(cd "$D" && find . \( -path ./node_modules -o -path ./.venv \) -prune -o -type f \( -name '*.py' -o -name '*.mjs' -o -name '*.js' \) -print | grep -viE 'test|config' | head -3 | tr '\n' '/')
  told_verify=$(grep -ciE 'verify\.sh' "$RAW" || true)
  python3 "$HERE/scrub.py" "$RAW" "$OUT/run$i.jsonl" >/dev/null
  (cd "$D" && find . \( -path ./node_modules -o -path ./.venv \) -prune -o -type f -print | sort) > "$OUT/run$i.files.txt"
  echo "isolated,cursor,$i,wall_s=$el,agent_exit=$arc,verify_rc=$vrc,leak=$leak,has_iso_hint=$has_iso,told_verify=$told_verify,env_probes=$envprobe,impl=$impl,image=$IMG_TAG" | tee -a "$SUM"
  echo "VERIFY_OUT: $vout" >> "$OUT/run$i.files.txt"
  # Cleanup auth + project
  rm -f "$H/.config/cursor/auth.json" "$RAW"
  rm -rf "$D" "$H"
  sleep 30
done
shred -u "$SECRET" 2>/dev/null || rm -f "$SECRET"
echo ISO_DONE
