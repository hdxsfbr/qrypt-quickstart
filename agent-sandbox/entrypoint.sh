#!/bin/sh
# Runs as root once: write .env as qrypt-only (mode 600), then drop to the "agent" user.
# The secret arrives in QRYPT_DOTENV and is removed from the environment before the agent starts.
set -e
chmod 755 /work
if [ -n "${QRYPT_DOTENV:-}" ]; then
  rm -f /work/.env
  (umask 077; printf '%s\n' "$QRYPT_DOTENV" > /work/.env); chown qrypt:qrypt /work/.env
fi
exec env -u QRYPT_DOTENV sudo -u agent -H --preserve-env=TERM,PATH "$@"
