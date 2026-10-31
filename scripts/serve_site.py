#!/usr/bin/env python
"""Serve _site/ locally with gzip compression and long cache headers, the way GitHub Pages does.

    python scripts/serve_site.py [--port 8771]

Used by scripts/lighthouse.sh so that performance numbers reflect compressed transfer sizes;
Python's plain http.server sends uncompressed CSS/JS, which makes Lighthouse scores meaningless.
"""
from __future__ import annotations

import argparse
import functools
import gzip
import http.server
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPRESSIBLE = {".html", ".css", ".js", ".json", ".svg", ".txt", ".xml", ".ipynb", ".csv", ".md"}


class GzipHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # noqa: D401
        pass

    def send_head(self):
        path = Path(self.translate_path(self.path))
        if path.is_dir():
            path = path / "index.html"
        if path.suffix.lower() in COMPRESSIBLE and path.is_file() and "gzip" in self.headers.get("Accept-Encoding", ""):
            data = gzip.compress(path.read_bytes(), compresslevel=6)
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(str(path)))
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "public, max-age=600")
            self.end_headers()
            return io.BytesIO(data)
        return super().send_head()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8771)
    args = ap.parse_args()
    handler = functools.partial(GzipHandler, directory=str(ROOT / "_site"))
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler) as httpd:
        print(f"serving _site on http://127.0.0.1:{args.port}/ (gzip)", flush=True)
        httpd.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
