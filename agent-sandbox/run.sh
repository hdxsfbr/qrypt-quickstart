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
# Visible hint so agents that `ls` first know they have no token.
printf '%s\n' \
  'Qrypt Isolated Setup. You have NO QRYPT_API_KEY in this container — that is intentional.' \
  'Implement the example from https://qrypt-quickstart.pages.dev/llms.txt and run mock tests.' \
  'Tell the human to run on the host: agent-sandbox/verify.sh --env <their-secret-path>' \
  > "$proj/QRYPT-ISOLATED.txt"
chmod 444 "$proj/QRYPT-ISOLATED.txt" 2>/dev/null || true

# Tag the image by a hash of the Dockerfile so a stale image from an older
# design (e.g. one with a secret-handling entrypoint) is never reused.
tag=$( (sha256sum "$here/Dockerfile" 2>/dev/null || shasum -a 256 "$here/Dockerfile") | cut -c1-12)
img="qrypt-agent-sandbox:$tag"
docker image inspect "$img" >/dev/null 2>&1 \
  || docker build -q -t "$img" "$here" >/dev/null
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
  "$img" "${@:-bash}"
