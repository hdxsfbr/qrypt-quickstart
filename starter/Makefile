# Quickstart: `make check` (no token needed, ~1 min), then optionally `make live-py` or `make live-js` (1 KiB of real entropy each).
.PHONY: check deps test isolation live-py live-js
deps:            ## install Python deps (Node needs none; Node 20.12+)
	python3 -m pip install -q -r quickstart/python/requirements.txt
test:            ## run both snippets against the mock: success, 401, 403, 429, 500, 503, missing token
	./mock/run_cases.sh
check: deps test
isolation:       ## Docker isolation probes for Isolated Setup (no real token)
	./agent-sandbox/test-isolation.sh
live-py:         ## real API, 1 KiB. Needs .env in quickstart/python
	cd quickstart/python && python3 quickstart.py
live-js:         ## real API, 1 KiB. Needs .env in quickstart/node
	cd quickstart/node && node quickstart.mjs
