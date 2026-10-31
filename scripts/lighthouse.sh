#!/usr/bin/env bash
# Lighthouse audit of the rendered site (optional quality gate). Requires Node (npx) and Chrome.
# Serves _site with gzip (scripts/serve_site.py) so transfer sizes match a real static host.
#   bash scripts/lighthouse.sh            # audits home, chapter, episode and lab pages -> _review/lighthouse/
set -euo pipefail
cd "$(dirname "$0")/.."
[ -d _site ] || { echo "render the site first (quarto render)"; exit 1; }
mkdir -p _review/lighthouse
PORT=${PORT:-8771}
python scripts/serve_site.py --port "$PORT" >/dev/null 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null || true' EXIT
sleep 1
PAGES=(
  "home|index.html"
  "chapter|part-1-foundations/ch02-ml-fundamentals/index.html"
  "episode|part-1-foundations/ch02-ml-fundamentals/03-evaluating-models.html"
  "lab|part-1-foundations/ch02-ml-fundamentals/labs/lab-02-first-ml-project.html"
)
for entry in "${PAGES[@]}"; do
  name=${entry%%|*}; path=${entry#*|}
  npx --yes lighthouse "http://127.0.0.1:$PORT/$path" --quiet --chrome-flags="--headless=new --no-sandbox" \
    --only-categories=performance,accessibility,best-practices --output=json --output=html \
    --output-path="_review/lighthouse/$name" >/dev/null
  python - "$name" <<'EOF'
import json, sys
name = sys.argv[1]
r = json.load(open(f"_review/lighthouse/{name}.report.json", encoding="utf8"))
cats = r["categories"]
print(f"{name:8s} performance {cats['performance']['score']*100:.0f}  accessibility {cats['accessibility']['score']*100:.0f}  best-practices {cats['best-practices']['score']*100:.0f}")
EOF
done
echo "reports in _review/lighthouse/"
