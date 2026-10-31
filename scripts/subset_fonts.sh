#!/usr/bin/env bash
# Re-subset the fonts in assets/fonts/src into assets/fonts (run after replacing a source font).
set -euo pipefail
cd "$(dirname "$0")/../assets/fonts"
U="U+0000-00FF,U+0100-017F,U+0180-024F,U+0370-03FF,U+1E00-1EFF,U+2000-206F,U+2070-209F,U+20A0-20CF,U+2100-214F,U+2150-218F,U+2190-21FF,U+2200-22FF,U+2300-23FF,U+2500-257F,U+2580-259F,U+25A0-25FF,U+2600-26FF,U+2700-27BF,U+2B00-2BFF,U+FB00-FB06"
for f in src/*.woff2; do
  python -m fontTools.subset "$f" --output-file="$(basename "$f")" --flavor=woff2 --unicodes="$U" --layout-features='*' --name-IDs='*' --notdef-outline
done
ls -la ./*.woff2
