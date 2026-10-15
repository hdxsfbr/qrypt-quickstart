#!/usr/bin/env bash
# Re-run the agent's program once (1 KiB) and judge success. Usage: verify.sh DIR
cd "$1" || exit 2
c=""
if [ -f package.json ] && grep -q '"start"' package.json; then c="npm start --silent"; fi
if [ -z "$c" ]; then
  f=$(find . -maxdepth 3 \( -path ./node_modules -o -path ./.venv -o -path ./venv \) -prune -o -type f \( -name '*.py' -o -name '*.mjs' -o -name '*.js' \) -print | grep -viE 'test|config' | head -1)
  py=python3; [ -x .venv/bin/python ] && py=.venv/bin/python; [ -x venv/bin/python ] && py=venv/bin/python
  case "$f" in *.py) c="$py $f";; *.js|*.mjs) c="node $f";; esac
fi
[ -z "$c" ] && { echo "VERIFY none"; exit 1; }
out=$(timeout 60 bash -c "$c" 2>&1); rc=$?
echo "$out" > /tmp/qverify.out
echo "VERIFY cmd=[$c] rc=$rc"
