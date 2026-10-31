#!/usr/bin/env python
"""Check WCAG contrast ratios for every design-token pair the site relies on.

Run:  python scripts/check_contrast.py
Exit code 1 if any pair falls below its target (4.5:1 for text, 3:1 for UI).
The token values are read from assets/scss/_tokens.scss so this cannot drift from the CSS.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "assets" / "scss" / "_tokens.scss"


def srgb_to_lin(c: float) -> float:
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * srgb_to_lin(r) + 0.7152 * srgb_to_lin(g) + 0.0722 * srgb_to_lin(b)


def contrast(fg: str, bg: str) -> float:
    l1, l2 = luminance(fg), luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def blend(fg: str, bg: str, alpha: float) -> str:
    """Colour of `fg` at opacity `alpha` over opaque `bg` (what a tinted callout background looks like)."""
    f = [int(fg.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)]
    b = [int(bg.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(alpha * x + (1 - alpha) * y):02X}" for x, y in zip(f, b))


def read_tokens() -> dict[str, dict[str, str]]:
    text = TOKENS.read_text(encoding="utf8")
    themes: dict[str, dict[str, str]] = {}
    for mode in ("dark", "light"):
        block = re.search(rf"@mixin mm-tokens-{mode}\s*\{{(.*?)\n\}}", text, re.S)
        if not block:
            sys.exit(f"could not find mixin mm-tokens-{mode} in {TOKENS}")
        themes[mode] = dict(re.findall(r"--mm-([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})", block.group(1)))
    return themes


def main() -> int:
    themes = read_tokens()
    failures = 0
    for mode, t in themes.items():
        print(f"\n=== {mode} ===")
        bgs = {"bg": t["bg"], "surface": t["surface"], "surface-2": t["surface-2"], "code-bg": t["code-bg"]}
        text_tokens = ["text", "text-muted", "accent-1", "accent-2", "accent-3", "accent-4", "link"]
        callouts = ["note", "tip", "pitfall", "challenge", "solution", "discussion", "bridge-chem",
                    "bridge-bio", "bridge-math", "bridge-cs", "checkpoint", "prereq", "deep-dive"]
        checks: list[tuple[str, str, str, float]] = []
        for name in text_tokens:
            for bgname, bg in bgs.items():
                checks.append((f"{name} on {bgname}", t[name], bg, 4.5))
        for name in callouts:
            # label text in the accent colour sits on a background tinted with ~8% of the accent
            for bgname in ("bg", "surface"):
                tinted = blend(t[name], bgs[bgname], 0.08)
                checks.append((f"{name} label on tinted {bgname}", t[name], tinted, 4.5))
                checks.append((f"text on tinted {name} ({bgname})", t["text"], tinted, 4.5))
                checks.append((f"{name} border on {bgname}", t[name], bgs[bgname], 3.0))
        for name in [k for k in t if k.startswith("syntax-")]:
            checks.append((f"{name} on code-bg", t[name], t["code-bg"], 4.5))
        checks.append(("primary button text (bg colour) on accent-1", t["bg"], t["accent-1"], 4.5))
        checks.append(("focus ring on bg", t["focus"], t["bg"], 3.0))
        checks.append(("focus ring on surface", t["focus"], t["surface"], 3.0))
        checks.append(("border on bg (non-text)", t["border"], t["bg"], 1.2))
        for label, fg, bg, target in checks:
            ratio = contrast(fg, bg)
            ok = ratio >= target
            failures += 0 if ok else 1
            flag = "ok " if ok else "LOW"
            print(f"  {flag} {ratio:5.2f}:1 (need {target}) {label}  {fg} / {bg}")
    print("\nAll contrast checks passed." if not failures else f"\n{failures} contrast check(s) FAILED.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
