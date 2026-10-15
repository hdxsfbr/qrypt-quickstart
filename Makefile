# Quickstart: `make check` (no token needed, ~1 min), then optionally `make live-py` or `make live-js` (1 KiB of real entropy each).
.PHONY: check deps test isolation site check-starter check-links live-py live-js lighthouse
deps:            ## install Python deps (Node needs none; Node 20.12+)
	python3 -m pip install -q -r quickstart/python/requirements.txt
test:            ## run both snippets against the mock: success, 401, 403, 429, 500, 503, missing token
	./mock/run_cases.sh
check: deps test
isolation:       ## Docker isolation probes (no real token)
	./agent-sandbox/test-isolation.sh
site:            ## regenerate site pages (Pygments highlighting) from sources
	python3 -m pip install -q -r tools/requirements-site.txt
	python3 tools/build_site.py
check-starter: site ## starter zip == repo files, no .env/token
	python3 tools/check_starter.py
check-links: site ## fail on outbound 4xx; SPA hosts use an allowlist (see tools/check_links.py)
	python3 tools/check_links.py
live-py:         ## real API, 1 KiB. Needs .env in quickstart/python
	cd quickstart/python && python3 quickstart.py && echo "live bytes: 1024" >> ../../reports/live-usage.log
live-js:         ## real API, 1 KiB. Needs .env in quickstart/node
	cd quickstart/node && node quickstart.mjs && echo "live bytes: 1024" >> ../../reports/live-usage.log
lighthouse:      ## make lighthouse URL=https://qrypt-quickstart.pages.dev/
	./tools/lighthouse.sh $(URL)
