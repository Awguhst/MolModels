#!/usr/bin/env python
"""Visual + accessibility review of the rendered site with Playwright.

* Serves _site/ on a local port.
* Screenshots the home, a chapter, an episode and a lab page at 1440, 1024 and 390 px wide,
  in dark and light themes -> _review/screenshots/<page>-<width>-<theme>.png
* Runs axe-core on each page in both themes -> _review/axe/<page>-<theme>.json and a summary.
* Exit code 1 if any serious/critical axe violation is found.

    python scripts/review_site.py                 # everything
    python scripts/review_site.py --no-axe        # screenshots only
    python scripts/review_site.py --pages home,episode

Requires: pip install playwright && playwright install chromium, and an axe-core copy at
scripts/vendor/axe.min.js (see scripts/get_axe.sh) or the AXE_PATH environment variable.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import json
import os
import socketserver
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
SHOTS = ROOT / "_review" / "screenshots"
AXE_OUT = ROOT / "_review" / "axe"
AXE_PATH = Path(os.environ.get("AXE_PATH") or ROOT / "scripts" / "vendor" / "axe.min.js")

PAGES = {
    "home": "index.html",
    "chapter": "part-1-foundations/ch02-ml-fundamentals/index.html",
    "episode": "part-1-foundations/ch02-ml-fundamentals/03-evaluating-models.html",
    "lab": "part-1-foundations/ch02-ml-fundamentals/labs/lab-02-first-ml-project.html",
    "glossary": "appendices/glossary.html",
}
WIDTHS = [1440, 1024, 390]
THEMES = ["dark", "light"]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # noqa: D401
        pass


def serve(port: int) -> socketserver.TCPServer:
    handler = functools.partial(Quiet, directory=str(SITE))
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default=",".join(PAGES))
    ap.add_argument("--no-axe", action="store_true")
    ap.add_argument("--no-shots", action="store_true")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    pages = [p for p in args.pages.split(",") if p in PAGES]
    if not SITE.exists():
        sys.exit("render the site first (quarto render)")
    SHOTS.mkdir(parents=True, exist_ok=True)
    AXE_OUT.mkdir(parents=True, exist_ok=True)
    axe_src = AXE_PATH.read_text(encoding="utf8") if (not args.no_axe and AXE_PATH.exists()) else None
    if not args.no_axe and axe_src is None:
        print(f"axe-core not found at {AXE_PATH}; skipping accessibility checks")
    httpd = serve(args.port)
    base = f"http://127.0.0.1:{args.port}/"
    worst = 0
    summary = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for theme in THEMES:
            ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
            ctx.add_init_script(f"try {{ localStorage.setItem('mm-theme', '{theme}'); }} catch (e) {{}}")
            page = ctx.new_page()
            for name in pages:
                url = base + PAGES[name]
                if not (SITE / PAGES[name]).exists():
                    print(f"skip {name}: {PAGES[name]} not rendered")
                    continue
                page.goto(url, wait_until="networkidle")
                # the theme script enables stylesheet links after load, which starts their download:
                # wait until every enabled stylesheet has actually been parsed before capturing
                page.wait_for_timeout(300)
                page.wait_for_function(
                    "Array.from(document.querySelectorAll('link[rel=\"stylesheet\"]')).every(l => l.sheet !== null)",
                    timeout=20000,
                )
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(300)
                if not args.no_shots:
                    for w in WIDTHS:
                        page.set_viewport_size({"width": w, "height": 900})
                        page.wait_for_timeout(250)
                        out = SHOTS / f"{name}-{w}-{theme}.png"
                        page.screenshot(path=str(out), full_page=True)
                    page.set_viewport_size({"width": 1440, "height": 900})
                if axe_src:
                    page.add_script_tag(content=axe_src)
                    res = page.evaluate("async () => await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa','best-practice']}})")
                    (AXE_OUT / f"{name}-{theme}.json").write_text(json.dumps(res, indent=1), encoding="utf8")
                    bad = [v for v in res["violations"] if v["impact"] in ("serious", "critical")]
                    worst += len(bad)
                    summary.append((name, theme, len(res["violations"]), len(bad)))
                    for v in res["violations"]:
                        targets = "; ".join(n["target"][0] if n["target"] else "?" for n in v["nodes"][:3])
                        print(f"  [{v['impact']:>8}] {name}/{theme}: {v['id']} ({len(v['nodes'])} nodes) e.g. {targets}")
            ctx.close()
        browser.close()
    httpd.shutdown()
    if summary:
        print("\naxe summary (page, theme, violations, serious+critical):")
        for row in summary:
            print("  ", row)
    print(f"screenshots in {SHOTS}")
    return 1 if worst else 0


if __name__ == "__main__":
    sys.exit(main())
