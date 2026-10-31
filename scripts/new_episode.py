#!/usr/bin/env python
"""Scaffold a new episode with the standard front matter and skeleton.

    python scripts/new_episode.py --chapter 3 --episode 2 --title "Decision trees" \
        [--teaching 35] [--exercises 20] [--level beginner]

Creates part-N-.../chNN-slug/EE-title-slug.qmd and tells you what to fill in.
The chapter directory must already exist (see new_chapter.py).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

TEMPLATE = '''---
title: "{title}"
chapter: {chapter}
episode: {episode}
teaching: {teaching}        # minutes
exercises: {exercises}
level: {level}     # beginner | intermediate | advanced
questions:
  - "What question does this episode answer?"
objectives:
  - "Do something concrete with the tool introduced here."
keypoints:
  - "One sentence a learner should remember a month later."
prerequisites: [{prereq}]
---

{{{{< include /_includes/mm-setup.qmd >}}}}

Opening paragraph: the scientific problem that motivates this episode, in two or three sentences.
Link the first use of every technical term to the glossary with `{{{{< term id >}}}}`.

## First idea

Intuition in plain words (or a figure) before any maths or code.

```{{python}}
import numpy as np

rng = np.random.default_rng(42)
x = rng.normal(size=5)
x
```

Interpret the output in one or two sentences.

::: {{.predict}}
Before you run the next cell: what do you expect, and why?
:::

```{{python}}
#| renderings: [light, dark]
#| fig-alt: "Describe what the figure shows for readers who cannot see it."
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(x)
ax.set(xlabel="index", ylabel="value")
plt.show()
```

::: {{.pitfall title="A common mistake"}}
What goes wrong, and how to recognise it.
:::

::: {{.bridge audience="chem"}}
A bridge box aimed at one background (chem | bio | math | cs).
:::

::: {{.deep-dive title="Optional maths"}}
The derivation, for those who want it.
:::

## Exercises

::: {{.challenge level=1 title="Check understanding"}}
Question.

:::: {{.solution}}
Answer, with the *why*.
::::
:::

::: {{.challenge level=2 title="Apply"}}
Task.

:::: {{.solution}}
Code and explanation.
::::
:::

::: {{.challenge level=3 title="Stretch"}}
Harder, open-ended task.

:::: {{.solution}}
Sketch of a solution.
::::
:::

## Where this is going

One paragraph linking this idea to a later cheminformatics or bioinformatics chapter.
'''


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:48]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--chapter", type=int, required=True)
    ap.add_argument("--episode", type=int, required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--teaching", type=int, default=30)
    ap.add_argument("--exercises", type=int, default=20)
    ap.add_argument("--level", default="beginner", choices=["beginner", "intermediate", "advanced"])
    args = ap.parse_args()

    matches = list(ROOT.glob(f"part-*/ch{args.chapter:02d}-*"))
    if not matches:
        sys.exit(f"no chapter directory ch{args.chapter:02d}-* found; create it with scripts/new_chapter.py first")
    cdir = matches[0]
    meta = yaml.safe_load((cdir / "_metadata.yml").read_text(encoding="utf8"))
    if meta.get("stub"):
        print(f"note: {cdir.name} is marked stub: true in _metadata.yml; set it to false once the chapter has real episodes")
    path = cdir / f"{args.episode:02d}-{slugify(args.title)}.qmd"
    if path.exists():
        sys.exit(f"{path} already exists")
    prereq = f"ch{args.chapter:02d}-ep{args.episode - 1:02d}" if args.episode > 1 else f"ch{args.chapter - 1:02d}-ep01"
    path.write_text(
        TEMPLATE.format(title=args.title.replace('"', "'"), chapter=args.chapter, episode=args.episode,
                        teaching=args.teaching, exercises=args.exercises, level=args.level, prereq=prereq),
        encoding="utf8",
    )
    print(f"created {path.relative_to(ROOT)}")
    print("next: write the episode, then `quarto preview` and run `pytest tests/test_front_matter.py`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
