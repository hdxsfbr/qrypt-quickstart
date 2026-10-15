#!/bin/sh
# Runs as root once: write .env as qrypt-only (mode 600), then drop to the "agent" user.
# The secret arrives in QRYPT_DOTENV and is removed from the environment before the agent starts.
set -e
chmod 755 /work
if [ -n "${QRYPT_DOTENV:-}" ]; then
  rm -f /work/.env
  (umask 077; printf '%s\n' "$QRYPT_DOTENV" > /work/.env); chown qrypt:qrypt /work/.env
fi
# A visible hint for agents: every first "ls -la" shows it.
printf '%s\n' 'This folder runs in the Qrypt agent sandbox.' '.env is readable ONLY through qrypt-run (Permission denied otherwise, on purpose).' 'Run your program with:  qrypt-run quickstart.py   (or quickstart.mjs / any .py .mjs .js file in /work)' > /work/QRYPT-SANDBOX-README.txt
chmod 444 /work/QRYPT-SANDBOX-README.txt
exec env -u QRYPT_DOTENV sudo -u agent -H --preserve-env=TERM env PATH="$PATH" "$@"
