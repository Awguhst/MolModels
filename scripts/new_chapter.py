#!/usr/bin/env python
"""Scaffold a chapter directory (or turn a stub into a real chapter).

    python scripts/new_chapter.py --part 2 --chapter 5 --title "Molecules as data" --short "Molecules as data"

Creates (or completes) part-N-.../chNN-slug/ with:
    _metadata.yml      chapter number, titles, part accent inheritance
    index.qmd          landing page: hero include, outcomes, schedule include, lab cards include
    key-points.qmd     thin page that includes the generated key points list
    labs/_metadata.yml execution settings for solution notebooks
    checkpoint.qmd     a chapter quiz skeleton (optional, --with-quiz)
Existing files are never overwritten.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def write_if_missing(path: Path, text: str) -> None:
    if path.exists():
        print(f"keep    {path.relative_to(ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf8")
    print(f"created {path.relative_to(ROOT)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--part", type=int, required=True, choices=[1, 2, 3, 4])
    ap.add_argument("--chapter", type=int, required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--short", help="short title for the sidebar/metro map (default: title)")
    ap.add_argument("--stub", action="store_true", help="create as a 'coming soon' stub")
    ap.add_argument("--with-quiz", action="store_true")
    args = ap.parse_args()

    course = yaml.safe_load((ROOT / "course.yml").read_text(encoding="utf8"))
    part = next(p for p in course["parts"] if p["number"] == args.part)
    existing = list(ROOT.glob(f"part-*/ch{args.chapter:02d}-*"))
    cdir = existing[0] if existing else ROOT / part["dir"] / f"ch{args.chapter:02d}-{slugify(args.title)}"
    cid = f"ch{args.chapter:02d}"
    short = args.short or args.title

    write_if_missing(cdir / "_metadata.yml", (
        f"chapter: {args.chapter}\nchapter-id: {cid}\nchapter-title: \"{args.title}\"\nchapter-short: \"{short}\"\n"
        f"chapter-href: index.html\nstub: {'true' if args.stub else 'false'}\n"
    ))
    if args.stub:
        write_if_missing(cdir / "index.qmd", f'''---
title: "{args.title}"
chapter-index: true
summary: "One-paragraph summary of what this chapter will cover."
---

::: {{.mm-soon-banner}}<span class="mm-chip">soon</span> This chapter is planned but not yet written.:::

## What it will cover

::: {{.mm-stub-outline}}
- Topic one
- Topic two
- Topic three
- Topic four
:::

## Planned learning outcomes

1. Outcome one.
2. Outcome two.
3. Outcome three.
''')
        return 0

    write_if_missing(cdir / "index.qmd", f'''---
title: "{args.title}"
chapter-index: true
summary: "One-paragraph summary shown in the hero strip and on the roadmap."
---

{{{{< generated {cid}-hero >}}}}

## What you will be able to do

- Outcome one.
- Outcome two.
- Outcome three.

## Schedule

{{{{< generated {cid}-schedule >}}}}

## Lab

{{{{< generated {cid}-labs >}}}}

## Before you start

::: {{.prereq}}
What learners should already know, with links to the relevant episodes.
:::
''')
    write_if_missing(cdir / "key-points.qmd", f'''---
title: "Chapter {args.chapter} key points"
chapter: {args.chapter}
chapter-index: false
subtitle: "Every key point of the chapter, generated from the episode front matter."
---

{{{{< generated {cid}-keypoints >}}}}
''')
    write_if_missing(cdir / "labs" / "_metadata.yml", "chapter-href: ../index.html\nexecute:\n  enabled: true\n")
    if args.with_quiz:
        write_if_missing(cdir / "checkpoint.qmd", f'''---
title: "Chapter {args.chapter} checkpoint"
chapter: {args.chapter}
checkpoint-quiz: true
subtitle: "Ten questions. Click an option to see why it is right or wrong."
---

::: {{.checkpoint title="Question 1"}}
Question text?

- [x] Correct option

  Why it is correct.
- [ ] Wrong option

  Why it is wrong.
:::
''')
    print(f"\nnext: python scripts/new_episode.py --chapter {args.chapter} --episode 1 --title \"...\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
