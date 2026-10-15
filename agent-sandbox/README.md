# Agent sandbox: keep AI agents from reading .env

**Why:** in our agent-readiness tests, agents ran `head -c 20 .env` in 14 of 15 runs, despite the docs telling them not to. File permissions stop that. Docs don't.

**How it works:**
- The agent runs in Docker as user `agent`.
- `run.sh` passes `.env` into the container by an environment-variable *name*, never on the command line, and removes the readable copy from the project folder. The entrypoint writes it to `/work/.env`, owned by a separate user `qrypt` with mode 600, then starts the agent with that variable removed from its environment.
- The entrypoint also writes a read-only `QRYPT-SANDBOX-README.txt` hint into the folder (added after a Claude Code run gave up without finding `qrypt-run`).
- `qrypt-run file.py|file.mjs|file.js` is the only way in. It's a fixed sudo rule that runs one program file from `/work` as `qrypt`, so the snippet still reads `QRYPT_API_KEY` from `.env`.

```bash
agent-sandbox/run.sh ~/my-project ~/my-project/.env your-agent-command   # or no command, for a shell
# inside: cat .env -> Permission denied;  qrypt-run quickstart.py -> Success
```
`.env` now lives in the project folder as uid 1500, mode 600. To remove it: `docker run --rm -v ~/my-project:/w alpine rm /w/.env`.

**Checked by hand (Oct 14, 2026):**
- As `agent`: `cat .env`, `head .env`, `sudo -u qrypt cat .env` and `sudo cat .env` are all denied.
- `qrypt-run .env` and `qrypt-run /etc/shadow` are refused.
- The agent's environment doesn't contain the token.
- `qrypt-run quickstart.py` prints the success line.

**Limits:** this blocks accidental reads, not a deliberately malicious agent. An agent could still write a program that prints the token and run it with `qrypt-run`. Use a test token, and review what the agent runs.
