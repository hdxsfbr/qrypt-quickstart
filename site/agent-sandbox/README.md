# Isolated Setup (Docker)

Run an AI coding agent **without giving it your Qrypt token**. The agent can
read the docs, write the example, install dependencies and run the **mock**
tests. Live verification is a separate, trusted step you run yourself.

## What this isolates (and what it does not)

| Property | Status |
|---|---|
| Agent process has no `QRYPT_API_KEY` in its environment | Yes (enforced, tested) |
| Agent filesystem has no `.env` | Yes (`run.sh` refuses to start if the project contains one) |
| Host home, SSH keys, cloud creds, Docker socket not mounted | Yes (default `run.sh`) |
| Agent cannot modify the code that runs with the real token | Yes (`verify.sh` copies fixed snippets from this repo into a private temp dir) |
| Docker guarantees zero leakage | **No.** A compromised agent CLI binary, a malicious `SANDBOX_DOCKER_ARGS`, or a kernel/container escape is out of scope. Review what you mount. |

## Quick start
```bash
# 1. Put your token somewhere the agent will never see:
mkdir -p ~/.config/qrypt
cp .env.example ~/.config/qrypt/.env   # then edit; chmod 600
chmod 600 ~/.config/qrypt/.env

# 2. Work in a clean project folder (no .env inside it):
mkdir -p ~/qrypt-demo && cd ~/qrypt-demo
# (agent will create the example files here)

# 3. Start the agent inside the sandbox (no secrets enter the container):
path/to/qrypt-quickstart/agent-sandbox/run.sh ~/qrypt-demo your-agent-command

# 4. Inside: implement from https://qrypt-quickstart.pages.dev/ , then run
#    the mock tests (no real token needed). With the starter archive unzipped
#    in the project, the image has no make, so:
#      python3 -m venv .venv && . .venv/bin/activate
#      pip install -r quickstart/python/requirements.txt && ./mock/run_cases.sh

# 5. On the HOST, after the agent finishes, verify against the live API:
path/to/qrypt-quickstart/agent-sandbox/verify.sh --env ~/.config/qrypt/.env
# -> "verify python: PASS ..." / "verify node: PASS ..."
```

## Existing repos
Do **not** mount a repo that already contains `.env`, `*.pem`, SSH keys or
cloud credentials. Either:
- work in a fresh directory and copy only the source you want the agent to see, or
- move secrets out of the tree first (`mv .env ~/.config/qrypt/.env`).

`run.sh` refuses to start if `$project/.env` exists, so a forgotten secret
file cannot ride in through the bind mount. `.dockerignore` excludes common
secret names from the **image build** context; that does **not** protect you
from bind mounts — `run.sh`'s refusal does.

## Isolation tests
```bash
agent-sandbox/test-isolation.sh    # no real token; exits 0 on PASS
```

## Limits (read this)
- This is stronger than "please don't read .env" in a prompt. It is **not** a
  formal guarantee against a determined attacker with a container escape.
- `SANDBOX_DOCKER_ARGS` lets you mount an agent CLI. If you mount your home
  directory or docker.sock there, you undo the isolation. Don't.
- `verify.sh` spends 1 KiB of real entropy per language. Use a disposable
  token when you can.
