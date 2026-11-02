#!/usr/bin/env python
"""Post-render step: decorate the rendered HTML so the site works fully without JavaScript.

* <html data-mm-part="N">            the Part accent colour for the page
* skip link                           "Skip to content" as the first focusable element
* sidebar decoration                  episode numbers, time estimates, completion circles, "soon" chips,
* lab cards                           substitute the GitHub repo/branch into Colab links
* a11y fixes                          role="button" on collapse toggles, labelled navbar, non-empty table headers
* navbar current section              match the page's Part directory instead of Quarto's shared sidebar
* no CDN                              remove the RequireJS/jQuery CDN tags Quarto adds for HTML outputs
* quarto-nav.js                       guard the <a>.href rewrite against SVG anchors (roadmap stations)
* lazy figures                        loading="lazy" on figure images; idempotent via a marker comment
"""
from __future__ import annotations

import hashlib
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


MARKER = "<!-- mm-post-render -->"
MM_SCRIPT_VERSION = hashlib.sha256((ROOT / "assets" / "js" / "mm.js").read_bytes()).hexdigest()[:12]
MM_SCRIPT_RE = re.compile(
    r'''(<script\b[^>]*\bsrc=["'])(/?(?:\.\.?/)*site_libs/quarto-contrib/mm-[^/"'?]+/mm\.js)(?:\?[^"']*)?(["'])'''
)
ASSET_VERSIONS = []
for asset, tag, attribute in (
    ("assets/css/chemistry.css", "link", "href"),
    ("brand/favicon.svg", "link", "href"),
):
    source = ROOT / asset
    if source.is_file():
        pattern = re.compile(
            rf'''(<{tag}\b[^>]*\s{attribute}=["'])(/?(?:\.\.?/)*{re.escape(asset)})(?:\?[^"']*)?(["'])'''
        )
        version = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
        ASSET_VERSIONS.append((pattern, version))


def normalize_navbar_active(html: str, page_rel: PurePosixPath) -> str:
    """Quarto associates the shared sidebar with Part I; select the actual page's Part instead."""
    current_part = page_rel.parts[0] if page_rel.parts and re.match(r"part-\d+-", page_rel.parts[0]) else None

    def navbar(match: re.Match) -> str:
        def link(anchor_match: re.Match) -> str:
            anchor = anchor_match[0]
            classes = re.search(r'\bclass="([^"]*)"', anchor)
            href = re.search(r'\bhref="([^"]*)"', anchor)
            if not classes or "nav-link" not in classes[1].split() or not href:
                return anchor
            target = PurePosixPath(resolve(page_rel, href[1]).lstrip("/"))
            if not target.parts or not re.match(r"part-\d+-", target.parts[0]):
                return anchor
            active = target.parts[0] == current_part
            names = [name for name in classes[1].split() if name != "active"]
            if active:
                names.append("active")
            anchor = anchor[:classes.start(1)] + " ".join(names) + anchor[classes.end(1):]
            anchor = re.sub(r'\s+aria-current="[^"]*"', "", anchor)
            return anchor[:-1] + ' aria-current="page">' if active else anchor

        return match[1] + re.sub(r"<a\b[^>]*>", link, match[2]) + match[3]

    return re.sub(r'(<nav\b[^>]*\bclass="[^\"]*\bnavbar\b[^\"]*"[^>]*>)(.*?)(</nav>)', navbar, html, flags=re.S)


def decorate(html: str, page_rel: PurePosixPath) -> str:
    # Refresh even already-decorated pages: partial renders can update the shared script.
    html = MM_SCRIPT_RE.sub(lambda m: f"{m[1]}{m[2]}?v={MM_SCRIPT_VERSION}{m[3]}", html)
    for pattern, version in ASSET_VERSIONS:
        html = pattern.sub(lambda m, v=version: f"{m[1]}{m[2]}?v={v}{m[3]}", html)
    html = normalize_navbar_active(html, page_rel)
    if MARKER in html:
        return html  # already processed (quarto preview re-runs post-render after every partial render)
    html = html.replace("</head>", MARKER + "</head>", 1)
    # 0. figures below the fold load lazily
    html = re.sub(r'<img src="([^"]+)" alt="([^"]*)" width="(\d+)" height="(\d+)" class="figure-img">',
                  r'<img src="\1" alt="\2" width="\3" height="\4" class="figure-img" loading="lazy" decoding="async">', html)
    # 1. part accent
    m = re.match(r"part-(\d)-", page_rel.parts[0]) if page_rel.parts else None
    if m:
        html = html.replace("<html ", f'<html data-mm-part="{m.group(1)}" ', 1)
    # 2. skip link
    # insert right after the real body tag (search past </head>, so text in head comments can never match)
    head_end = html.find("</head>")
    html = html[:head_end] + re.sub(r"(<body\b[^>]*>)", r"\1" + SKIP, html[head_end:], count=1)

    # 3. sidebar links
    def repl(mo: re.Match) -> str:
        href, active, text = mo.group(1), mo.group(2) or "", mo.group(3)
        text = re.sub(r"<[^>]+>", "", text).strip()  # Quarto wraps the label in <span class="menu-text">
        target = resolve(page_rel, href)
        pg = by_href.get(target)
        ch = chapter_by_href.get(target)
        if pg and pg["kind"] == "episode":
            minutes = pg["teaching"] + pg["exercises"]
            inner = (f'<span class="mm-ep-num">{pg["label"]}</span> <span class="mm-ep-title">{pg["title"]}</span> '
                     f'<span class="mm-time">{minutes} min</span>')
            return f'<a href="{href}" class="sidebar-item-text sidebar-link{active}">{inner}</a>'
        if pg and pg["kind"] == "lab":
            inner = (f'<span class="mm-ep-num">Lab</span> <span class="mm-ep-title">{pg["title"]}</span> '
                     f'<span class="mm-time">{pg.get("duration", "")}</span>')
            return f'<a href="{href}" class="sidebar-item-text sidebar-link{active}">{inner}</a>'
        if pg and pg["kind"] == "quiz":
            inner = f'<span class="mm-ep-num">Quiz</span> <span class="mm-ep-title">{text}</span>'
            return f'<a href="{href}" class="sidebar-item-text sidebar-link{active}">{inner}</a>'
        if ch is not None:
            if ch["stub"]:
                label = re.sub(r"\s*\(soon\)\s*$", "", text)
                m2 = re.match(r"(\d+) (.*)", label)
                inner = f'<span class="mm-ep-num">{m2.group(1)}</span> <span class="mm-ep-title">{m2.group(2)}</span>' if m2 else f'<span class="mm-ep-title">{label}</span>'
                return (f'<a href="{href}" class="sidebar-item-text sidebar-link mm-soon{active}">'
                        f'{inner}<span class="mm-chip">soon</span></a>')
            m2 = re.match(r"(\d+) (.*)", text)
            label = f'<span class="mm-ep-num">{m2.group(1)}</span> <span class="mm-ep-title">{m2.group(2)}</span>' if m2 else f'<span class="mm-ep-title">{text}</span>'
            return f'<a href="{href}" class="sidebar-item-text sidebar-link{active}">{label}</a>'
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
    # Quarto drops logo-alt when the logo has light/dark variants; the brand link then has no name
    html = html.replace('alt="" class="navbar-logo', 'alt="Molecules &amp; Models home" class="navbar-logo')
    # the mobile sidebar toggle carries an aria-label that does not contain its visible text
    html = html.replace('aria-expanded="false" aria-label="Toggle sidebar navigation" onclick', 'aria-expanded="false" onclick')
    # 6. No runtime CDN calls: Quarto adds RequireJS + jQuery from jsdelivr whenever a cell displays
    #    HTML (pandas tables). We have no Jupyter widgets, so drop them.
    html = CDN_SCRIPT_RE.sub("", html)
    html = html.replace("""<script type="application/javascript">define('jquery', [],function() {return window.jQuery;})</script>""", "")
    return html


def patch_quarto_nav() -> None:
    """Quarto's quarto-nav.js rewrites every <a>.href but assumes it is a string; the roadmap's SVG
    station links expose an SVGAnimatedString and crash the handler. Skip non-string hrefs."""
    js = OUT / "site_libs" / "quarto-nav" / "quarto-nav.js"
    if js.exists():
        text = js.read_text(encoding="utf8")
        fixed = text.replace("      if (links[i].href) {", '      if (typeof links[i].href === "string") {')
        if fixed != text:
            js.write_text(fixed, encoding="utf8")


def main() -> int:
    n = 0
    patch_quarto_nav()
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
