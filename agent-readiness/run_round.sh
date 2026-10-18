#!/usr/bin/env bash
# Usage: run_round.sh ROUND  (5 runs, 10-min timeout each, 30 s spacing)
set -u
R=$1; HERE=$(cd "$(dirname "$0")" && pwd); OUT=$HERE/logs/round$R; mkdir -p "$OUT"
URL=https://qrypt-quickstart.pages.dev/
# Default prompt = the one used for the logged rounds (the brief's sentence word for word).
# PROMPT_STYLE=short uses the site's short paste prompt instead (short-prompt and Codex sandbox-on rounds).
PROMPT="Quickstart docs: $URL
A .env file containing QRYPT_API_KEY is already in the current directory.

Generate an AES-256 key using Qrypt quantum entropy in a new project"
[ "${PROMPT_STYLE:-brief}" = short ] && PROMPT="Set up the Qrypt quickstart and run the Python snippet. Follow https://qrypt-quickstart.pages.dev/ and https://qrypt-quickstart.pages.dev/llms.txt."
CSV=$HERE/runs.csv; [ -f "$CSV" ] || echo "round,run,success,wall_clock_s,verify_rc,key_printed,token_in_transcript,failure_category,failure_reason" > "$CSV"
for i in 1 2 3 4 5; do
  D=$(mktemp -d /tmp/qrypt-agent-r${R}-${i}-XXXX)
  printf 'QRYPT_API_KEY=%s\n' "$(cat ~/.config/agentforge/qrypt_api_key)" > "$D/.env"; chmod 600 "$D/.env"
  RAW=$(mktemp /dev/shm/qraw-XXXX); t0=$(date +%s)
  ( cd "$D" && env -i HOME="$HOME" PATH="$HOME/.local/bin:$HOME/.nvm/versions/node/v24.14.0/bin:/usr/local/bin:/usr/bin:/bin" TERM=dumb \
    timeout 600 cursor-agent -p --force --trust --output-format stream-json "$PROMPT" ) > "$RAW" 2>&1
  arc=$?; t1=$(date +%s); el=$((t1-t0))
  sleep 15
  bash "$HERE/verify.sh" "$D" >> "$RAW" 2>&1; vrc=$(grep -o 'VERIFY.*rc=[0-9]*' "$RAW" | grep -o '[0-9]*$' || echo 1)
  cat /tmp/qverify.out >> "$RAW" 2>/dev/null; echo "AGENT_EXIT=$arc" >> "$RAW"
  flags=$(python3 "$HERE/scrub.py" "$RAW" "$OUT/run$i.jsonl"); rm -f "$RAW" /tmp/qverify.out
  (cd "$D" && find . -path ./node_modules -prune -o -type f ! -name .env -print | sort) > "$OUT/run$i.files.txt"
  mkdir -p "$OUT/run$i-src"; (cd "$D" && find . \( -path ./node_modules -o -path ./.venv -o -path ./venv \) -prune -o -type f \( -name '*.py' -o -name '*.js' -o -name '*.mjs' -o -name '*.ts' -o -name '*.json' -o -name '*.txt' -o -name '*.md' \) ! -name package-lock.json -print | while read f; do mkdir -p "$OUT/run$i-src/$(dirname "$f")"; python3 "$HERE/scrub.py" "$f" "$OUT/run$i-src/$f" >/dev/null; done)
  echo "$R,$i,TBD,$el,$vrc,$flags" | sed 's/"//g;s/, /;/g' >> "$CSV"
  rm -rf "$D"
  sleep 30
done
echo ROUND $R DONE
