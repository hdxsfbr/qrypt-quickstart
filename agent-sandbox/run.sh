#!/usr/bin/env bash
# Start the sandbox for a project folder. Usage:
#   agent-sandbox/run.sh /path/to/project /path/to/.env [command...]   (default: bash). If .env is inside the project it is moved into the container.
# Extra docker flags (e.g. to mount your agent CLI and its login) go in SANDBOX_DOCKER_ARGS.
set -euo pipefail
proj=$(realpath "$1"); envf=$(realpath "$2"); shift 2
docker image inspect qrypt-agent-sandbox >/dev/null 2>&1 || docker build -q -t qrypt-agent-sandbox "$(dirname "$0")" >/dev/null
QRYPT_DOTENV=$(cat "$envf"); export QRYPT_DOTENV   # passed by name, never on the command line
# Remove the readable host copy from the project folder; the container re-creates it as qrypt-only.
[ "$(dirname "$envf")" = "$proj" ] && rm -f "$envf"
exec docker run --rm -i ${SANDBOX_DOCKER_ARGS:-} -e QRYPT_DOTENV -v "$proj":/work qrypt-agent-sandbox "${@:-bash}"
