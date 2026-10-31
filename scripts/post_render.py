#!/usr/bin/env python
"""Post-render step: decorate the rendered HTML so the site works fully without JavaScript.

* <html data-mm-part="N">            the Part accent colour for the page
* skip link                           "Skip to content" as the first focusable element
* sidebar decoration                  episode numbers, time estimates, completion circles, "soon" chips,
                                      per-chapter progress bars (filled by assets/js/mm.js)
* lab cards                           substitute the GitHub repo/branch into Colab links
* a11y fixes                          role="button" on collapse toggles, labelled navbar, non-empty table headers
* no CDN                              remove the RequireJS/jQuery CDN tags Quarto adds for HTML outputs
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path, PurePosixPath

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR") or (ROOT / "_site"))
course = json.loads((ROOT / "_generated" / "course.json").read_text(encoding="utf8"))
cfg = yaml.safe_load((ROOT / "_quarto.yml").read_text(encoding="utf8"))
REPO = cfg.get("github-repo", "YOUR-USER/molecules-and-models")
BRANCH = cfg.get("github-branch", "main")

by_href: dict[str, dict] = {p["href"]: p for p in course["pages"].values()}
chapter_by_href: dict[str, dict] = {c["href"]: c for c in course["chapters"].values()}

SKIP = '<a class="mm-skip" href="#quarto-document-content">Skip to content</a>'
LINK_RE = re.compile(r'<a href="([^"]+)" class="sidebar-item-text sidebar-link( active)?">(.*?)</a>', re.S)
CDN_SCRIPT_RE = re.compile(r'<script src="https://cdn\.jsdelivr\.net/npm/(?:requirejs|jquery)@[^"]*"[^>]*></script>\s*')


def resolve(page_rel: PurePosixPath, href: str) -> str:
    href = href.split("#", 1)[0]
    target = (page_rel.parent / href)
    parts: list[str] = []
    for seg in target.parts:
        if seg == "..":
            if parts:
                parts.pop()
        elif seg != ".":
            parts.append(seg)
    return "/".join(parts)


def decorate(html: str, page_rel: PurePosixPath) -> str:
    # 1. part accent
    m = re.match(r"part-(\d)-", page_rel.parts[0]) if page_rel.parts else None
    if m:
        html = html.replace("<html ", f'<html data-mm-part="{m.group(1)}" ', 1)
    # 2. skip link
    html = re.sub(r"(<body[^>]*>)", r"\1" + SKIP, html, count=1)

    # 3. sidebar links
    def repl(mo: re.Match) -> str:
        href, active, text = mo.group(1), mo.group(2) or "", mo.group(3)
        target = resolve(page_rel, href)
        pg = by_href.get(target)
        ch = chapter_by_href.get(target)
        if pg and pg["kind"] == "episode":
            minutes = pg["teaching"] + pg["exercises"]
            inner = (f'<span class="mm-ep-num">{pg["label"]}</span> <span class="mm-ep-title">{pg["title"]}</span> '
                     f'<span class="mm-time">{minutes} min</span><span class="mm-check" data-mm-check="{pg["id"]}" aria-hidden="true"></span>')
            return f'<a href="{href}" class="sidebar-item-text sidebar-link{active}">{inner}</a>'
        if pg and pg["kind"] == "lab":
            inner = (f'<span class="mm-ep-num">Lab</span> <span class="mm-ep-title">{pg["title"]}</span> '
                     f'<span class="mm-time">{pg.get("duration", "")}</span><span class="mm-check" data-mm-check="{pg["id"]}" aria-hidden="true"></span>')
            return f'<a href="{href}" class="sidebar-item-text sidebar-link{active}">{inner}</a>'
        if pg and pg["kind"] == "quiz":
            inner = f'<span class="mm-ep-num">Quiz</span> <span class="mm-ep-title">{text}</span>'
            return f'<a href="{href}" class="sidebar-item-text sidebar-link{active}">{inner}</a>'
        if ch is not None:
            if ch["stub"]:
                label = re.sub(r"\s*\(soon\)\s*$", "", text)
                return (f'<a href="{href}" class="sidebar-item-text sidebar-link mm-soon{active}">'
                        f'<span class="mm-ep-title">{label}</span><span class="mm-chip">soon</span></a>')
            return (f'<a href="{href}" class="sidebar-item-text sidebar-link{active}"><span class="mm-ep-title">{text}</span>'
                    f'<span class="mm-pct" data-mm-pct="{ch["id"]}"></span></a>'
                    f'<span class="mm-progress" data-mm-bar="{ch["id"]}" data-part="{ch["part"]}" aria-hidden="true" hidden><span></span></span>')
        if "(soon)" in text:
            label = text.replace("(soon)", "").strip()
            return f'<a href="{href}" class="sidebar-item-text sidebar-link mm-soon{active}"><span class="mm-ep-title">{label}</span><span class="mm-chip">soon</span></a>'
        return mo.group(0)

    html = LINK_RE.sub(repl, html)
    # 4. Colab links
    html = html.replace("{GITHUB_REPO}", REPO).replace("{GITHUB_BRANCH}", BRANCH)
    # 5. Accessibility fixes to Quarto's own markup
    html = html.replace('class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarCollapse" aria-controls="navbarCollapse" role="menu"',
                        'class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarCollapse" aria-controls="navbarCollapse"')
    html = re.sub(r'(<a class="(?:sidebar-item-toggle|flex-grow-1 no-decor|sidebar-item-text sidebar-link)[^"]*"[^>]*?) role="navigation"', r'\1 role="button"', html)
    html = html.replace('<th data-quarto-table-cell-role="th"></th>', '<th data-quarto-table-cell-role="th"><span class="mm-visually-hidden">index</span></th>')
    html = html.replace('<nav class="navbar navbar-expand-lg "', '<nav class="navbar navbar-expand-lg " aria-label="Main"')
    html = html.replace('<nav id="quarto-sidebar" class="sidebar', '<nav id="quarto-sidebar" aria-label="Course contents" class="sidebar')
    html = html.replace('<nav id="TOC" role="doc-toc"', '<nav id="TOC" role="doc-toc" aria-label="On this page"')
    # 6. No runtime CDN calls: Quarto adds RequireJS + jQuery from jsdelivr whenever a cell displays
    #    HTML (pandas tables). We have no Jupyter widgets, so drop them.
    html = CDN_SCRIPT_RE.sub("", html)
    html = html.replace("""<script type="application/javascript">define('jquery', [],function() {return window.jQuery;})</script>""", "")
    return html


def main() -> int:
    n = 0
    for f in OUT.rglob("*.html"):
        rel = PurePosixPath(f.relative_to(OUT).as_posix())
        html = f.read_text(encoding="utf8")
        new = decorate(html, rel)
        if new != html:
            f.write_text(new, encoding="utf8")
            n += 1
    if os.environ.get("QUARTO_PROJECT_SCRIPT_QUIET") != "1":
        print(f"[post_render] decorated {n} pages in {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
