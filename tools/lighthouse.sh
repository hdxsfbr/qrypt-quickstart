#!/usr/bin/env bash
# 10 Lighthouse mobile runs against $1 (deployed URL). Saves reports to reports/lighthouse/ and prints p95 load + min a11y.
set -eu
URL=${1:?usage: tools/lighthouse.sh https://site.pages.dev/}
OUT=reports/lighthouse; mkdir -p "$OUT"
for i in $(seq 1 10); do
  npx -y lighthouse@12 "$URL" --quiet --form-factor=mobile --only-categories=performance,accessibility \
    --chrome-flags="--headless=new --no-sandbox" --output=json --output=html --output-path="$OUT/run-$i" >/dev/null
done
python3 - "$OUT" <<'PY'
import json, glob, math, sys
runs = [json.load(open(f)) for f in sorted(glob.glob(sys.argv[1] + "/run-*.report.json"))]
lcp = sorted(r["audits"]["largest-contentful-paint"]["numericValue"] / 1000 for r in runs)
a11y = [round(r["categories"]["accessibility"]["score"] * 100) for r in runs]
p95 = lcp[max(0, math.ceil(0.95 * len(lcp)) - 1)]
summary = {"url": runs[0]["finalDisplayedUrl"], "runs": len(runs), "lcp_seconds": lcp, "p95_load_lcp_s": p95,
           "accessibility_min": min(a11y), "pass": p95 < 1.5 and min(a11y) >= 95}
json.dump(summary, open(sys.argv[1] + "/summary.json", "w"), indent=2); print(json.dumps(summary, indent=2))
PY
