#!/usr/bin/env bash
# Isolated Setup: start an AI agent in Docker with NO host secrets.
# Usage:
#   agent-sandbox/run.sh /path/to/project [agent-command...]
# Defaults to an interactive bash if no command is given.
#
# What is mounted: ONLY the project directory, at /work.
# What is NOT mounted or passed: .env files, home dirs, SSH keys, cloud
# credentials, Docker socket, or any QRYPT_API_KEY value.
# Live verification is a separate host-side step: agent-sandbox/verify.sh
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
proj=$(realpath "${1:?usage: run.sh /path/to/project [command...]}"); shift || true
# Refuse to start if a .env is sitting in the project: that would leak into
# the bind mount. Move it aside (or use verify.sh's --env path outside /work).
if [ -f "$proj/.env" ] || [ -f "$proj/.env.local" ]; then
  echo "run.sh: refuse to mount $proj because it contains a .env file." >&2
  echo "Move secrets outside the project (e.g. ~/.config/qrypt/.env) and" >&2
  echo "pass that path to agent-sandbox/verify.sh --env <path>." >&2
  exit 2
fi
docker image inspect qrypt-agent-sandbox >/dev/null 2>&1 \
  || docker build -q -t qrypt-agent-sandbox "$here" >/dev/null
# SANDBOX_DOCKER_ARGS may mount an agent CLI binary (read-only) and its login
# state, but MUST NOT add -v for home secrets, docker.sock, or -e QRYPT_*.
# shellcheck disable=SC2086
tty=(); [ -t 0 ] && tty=(-it)
# shellcheck disable=SC2086
exec docker run --rm "${tty[@]}" \
  --network bridge \
  --security-opt no-new-privileges \
  -v "$proj":/work \
  ${SANDBOX_DOCKER_ARGS:-} \
  qrypt-agent-sandbox "${@:-bash}"
