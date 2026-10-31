"""Checks on the rendered site in _site/ (skipped if it has not been rendered):
internal links resolve, no runtime CDN calls, every figure has alt text and a light/dark pair,
no Python warnings leaked into outputs, pages stay under the size budget."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

from conftest import ROOT

SITE = ROOT / "_site"
pytestmark = pytest.mark.skipif(not SITE.exists(), reason="site not rendered (quarto render)")


def pages() -> list[Path]:
    return sorted(p for p in SITE.rglob("*.html") if "site_libs" not in p.parts)


def test_internal_links_resolve():
    broken = []
    ids_cache: dict[Path, set[str]] = {}
    for page in pages():
        html = page.read_text(encoding="utf8")
        for href in re.findall(r'(?:href|src)="([^"]+)"', html):
            if href.startswith(("http://", "https://", "mailto:", "data:", "javascript:", "#", "tel:")):
                continue
            parts = urlsplit(href)
            target = (page.parent / unquote(parts.path)).resolve() if parts.path else page
            if parts.path and not target.exists():
                broken.append(f"{page.relative_to(SITE)} -> {href}")
                continue
            if parts.fragment and target.suffix == ".html" and target.exists():
                if target not in ids_cache:
                    t = target.read_text(encoding="utf8")
                    ids_cache[target] = set(re.findall(r'\bid="([^"]+)"', t)) | set(re.findall(r'\bname="([^"]+)"', t))
                if parts.fragment not in ids_cache[target] and not parts.fragment.startswith("cb"):
                    broken.append(f"{page.relative_to(SITE)} -> {href} (missing anchor)")
    assert not broken, "broken internal links:\n" + "\n".join(broken[:50])


def test_no_runtime_cdn():
    offenders = []
    for page in pages():
        html = page.read_text(encoding="utf8")
        for m in re.findall(r'<(?:script|link)[^>]+(?:src|href)="(https?://[^"]+)"', html):
            offenders.append(f"{page.relative_to(SITE)}: {m}")
        if "fonts.googleapis.com" in html or "fonts.gstatic.com" in html:
            offenders.append(f"{page.relative_to(SITE)}: Google Fonts reference")
    assert not offenders, "\n".join(offenders[:30])


def test_figures_have_alt_and_theme_pairs():
    problems = []
    for page in pages():
        html = page.read_text(encoding="utf8")
        for img in re.findall(r"<img[^>]*figure-img[^>]*>", html):
            if 'alt=""' in img or " alt=" not in img:
                problems.append(f"{page.relative_to(SITE)}: figure without alt text")
        n_light = html.count("cell-output-display light-content")
        n_dark = html.count("cell-output-display dark-content")
        if n_light != n_dark:
            problems.append(f"{page.relative_to(SITE)}: {n_light} light vs {n_dark} dark renderings")
        # a figure outside a light/dark container means a cell forgot `renderings`
        bare = re.findall(r'<div class="cell-output cell-output-display">\s*<div>\s*<figure', html)
        if bare and "labs" not in page.parts:
            problems.append(f"{page.relative_to(SITE)}: {len(bare)} figure(s) without renderings")
    assert not problems, "\n".join(problems)


def test_no_warnings_or_errors_in_outputs():
    bad = []
    for page in pages():
        html = page.read_text(encoding="utf8")
        if "cell-output-stderr" in html:
            bad.append(f"{page.relative_to(SITE)}: stderr (warning) output")
        if "cell-output-error" in html:
            # an error cell is allowed only when the author asked for it (#| error: true), e.g. to teach tracebacks
            src = ROOT / page.relative_to(SITE).with_suffix(".qmd")
            if not (src.exists() and "#| error: true" in src.read_text(encoding="utf8")):
                bad.append(f"{page.relative_to(SITE)}: unexpected error output")
        if re.search(r"(Deprecation|Future|User|Runtime)Warning", html):
            bad.append(f"{page.relative_to(SITE)} mentions a Warning in output")
    assert not bad, "\n".join(bad)


def test_page_size_budget():
    over = [(p.relative_to(SITE).as_posix(), p.stat().st_size // 1024) for p in pages() if p.stat().st_size > 1_500_000]
    assert not over, f"pages over 1.5 MB: {over}"


def test_every_episode_page_has_structure():
    for page in pages():
        html = page.read_text(encoding="utf8")
        if 'class="mm-ep-label"' in html and "mm-keypoints" not in html and "Lab " not in html[:20000]:
            if '<span class="mm-ep-label">Lab' in html:
                continue
            pytest.fail(f"{page.relative_to(SITE)}: episode without key points card")


def test_solutions_are_collapsible():
    """Every exercise solution renders as a collapsed <details> (Quarto's own 'Solution.' environment must not win)."""
    bad = []
    for page in pages():
        html = page.read_text(encoding="utf8")
        if 'class="proof solution"' in html:
            bad.append(f"{page.relative_to(SITE)}: solution rendered by Quarto's proof environment")
        n_ex = html.count("mm-callout--challenge")
        n_sol = html.count('details class="mm-callout mm-callout--solution"')
        if n_ex and n_sol < n_ex:
            bad.append(f"{page.relative_to(SITE)}: {n_ex} exercises but {n_sol} collapsible solutions")
    assert not bad, chr(10).join(bad)


def test_collapsible_bodies_are_intact():
    """A filter bug once replaced the first paragraph of every untitled collapsible box with 'nil'."""
    bad = []
    for page in pages():
        html = page.read_text(encoding="utf8")
        for m in re.finditer(r'<details class="mm-callout mm-callout--(solution|proof|deep-dive)[^"]*"[^>]*>.*?<div class="mm-callout-body">\s*(.{0,12})', html, re.S):
            if m.group(2).strip().startswith("nil"):
                bad.append(f"{page.relative_to(SITE)}: {m.group(1)} body starts with 'nil'")
    assert not bad, chr(10).join(bad)
