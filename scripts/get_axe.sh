#!/usr/bin/env bash
# Fetch axe-core (MPL-2.0) for scripts/review_site.py. Requires npm.
set -euo pipefail
cd "$(dirname "$0")"
tmp=$(mktemp -d)
(cd "$tmp" && npm init -y >/dev/null && npm i axe-core --silent)
mkdir -p vendor
cp "$tmp/node_modules/axe-core/axe.min.js" vendor/axe.min.js
cp "$tmp/node_modules/axe-core/LICENSE" vendor/LICENSE-axe-core
rm -rf "$tmp"
echo "axe-core vendored into scripts/vendor/"
