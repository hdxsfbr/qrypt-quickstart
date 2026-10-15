# Demo video script: Qrypt Developer Quickstart (v1)

Output: `/workspace/qrypt-demo/qrypt-demo-v1.mp4` (box), 1080p30, 3:18 (limit 5:00). Narration: Andre's cloned voice, Chatterbox standard, exaggeration 0.35, cfg 0.55.

Rules: the token never appears on screen (terminal and agent scenes are replays of captured real output; every frame of them OCR-scanned). The site is an unofficial prototype, not affiliated with or made by Qrypt. Numbers come only from PRD.md and AGENT_READINESS.md.

| Scene | Start | Length | On screen |
|---|---|---|---|
| s1 | 0:00 | 17.4 s | Hook title slide (unofficial-prototype tag) |
| s2 | 0:17 | 31.0 s | Live site tour: steps 1-3, Python/Node tabs, copy button, pitfalls, troubleshooting page (Playwright, 125% zoom) |
| s3 | 0:48 | 26.0 s | Fresh run: starter zip, venv, `test -f .env`, quickstart.py -> Success (real output, replayed terminal) |
| s4 | 1:14 | 22.5 s | Error paths: missing-token message; mock server 401 (real output, replayed terminal) |
| s5 | 1:37 | 43.5 s | Claude Code fresh Quick Setup run with the short prompt, two-phase, sped up (steps from its own log) |
| s6 | 2:20 | 17.6 s | Agent-readiness results slide (AGENT_READINESS.md), Codex sandbox-off caveat |
| s7 | 2:38 | 24.0 s | Activation funnel slide (PRD.md section 4) |
| s8 | 3:02 | 16.0 s | Close slide |

## Narration

### s1 (0:00)
> Imagine you've never heard of Crypt. Five minutes from now, you have a working A E S two fifty six encryption key, made from quantum randomness. That's the goal of this quick start. Quick note: it's an unofficial prototype I built. It isn't made by Crypt or affiliated with them.

### s2 (0:17)
> Here's the quick start page. Three steps: get a test token, save it in a file called dot E N V, and run a short snippet in Python or Node. Each snippet is about twenty-five lines of code and has a copy button.
> It also warns about the things that trip people up, like the size setting counting kibi-bytes, not bytes. And there's a troubleshooting page that maps every error code to a likely fix.

### s3 (0:48)
> Now a fresh run in a new, empty folder. I download the starter zip from the site, create a virtual environment, and install the three dependencies. The token goes into dot E N V, and we never print it. Then one command. It fetches one kibi-byte of quantum random bytes, keeps thirty-two of them as the key, and encrypts and decrypts a test message. Success. The key itself is never shown.

### s4 (1:14)
> What happens when something's wrong? Running it with no token gives a plain message: what's missing, and where to get one. And against the local mock server, which is a fake copy of the A P I that spends no real token, a bad token returns a four-oh-one error with a clear explanation. No retry loop, no stack trace.

### s5 (1:37)
> Lots of developers now hand this job to an A I coding agent. Here's Claude Code with the short prompt from the site: set up the quick start and run the Python snippet, using the page and the L L M S dot text file, a plain-text copy of the docs for agents.
> It reads the docs, downloads the starter, installs the dependencies, and runs the mock tests. All eighteen pass. Then it checks for a dot E N V file, finds none, and asks me to create it, instead of hunting for the token. I create it and say go ahead. It checks the file exists without reading it, and runs the snippet. Success. The whole run took under two minutes, sped up here.

### s6 (2:20)
> We tested this properly. Cursor... Codex, and Claude Code each did five runs in two setup modes. Thirty out of thirty produced a working key, and none leaked the token. One honest caveat: the Codex runs had the Codex sandbox turned off.

### s7 (2:38)
> To know if it's working for real developers, the plan defines an activation funnel. Landing on the page. Creating a token. The first successful call. The first key. And coming back within seven days. Activation means a working key, and the targets are placeholders until we have four weeks of real data.

### s8 (3:02)
> So that's the Crypt Developer Quick Start. A newcomer, or their A I agent, gets from zero to a working A E S key in minutes, with clear errors and the token kept off screen. Thanks for watching.

## Live API use
Two real 1 KiB calls on Oct 15, 2026: the fresh terminal run (s3) and the Claude Code run (s5). Error paths used no token (missing) and the local mock (401).
