# Contributing

Thank you for helping improve *Molecules & Models*. Contributions of every size are welcome: typo fixes,
clearer explanations, better exercises, new bridge boxes for a background we serve poorly, and whole chapters.

## Small fixes

Use the **Edit this page** link at the bottom of any page: it opens the source file on GitHub where you
can propose a change directly. Or use **Report a problem** to open an issue with the page pre-filled.

## Larger changes

1. Fork and clone the repository; set up the environment as in [README.md](README.md).
2. Read [AUTHORING.md](AUTHORING.md). It is short and the tests enforce most of it.
3. Make your change on a branch. For a new episode or chapter use `scripts/new_episode.py` / `scripts/new_chapter.py`.
4. Run `quarto render` and `pytest`. For visual changes also run `python scripts/review_site.py` and look at the screenshots in both themes.
5. Open a pull request. Describe what changed and, for content, which of the four audiences you had in mind.

## What we look for

- **Scientific correctness first.** Every factual claim must be verifiable; do not add citations, numbers or API behaviour you have not checked.
- **No difficulty jumps.** A chemist, a biologist, a mathematician and a programmer should each be able to follow. If a step assumes something one of them would not know, add a bridge box or a link to the maths refresher.
- **Runnable, warning-free code** with fixed seeds and pinned versions. The site build fails on warnings by design.
- **Accessibility.** Alt text on every figure, colour-blind-safe palettes, contrast ≥ 4.5:1, keyboard-operable interactions.
- **Licensing.** Only add datasets that are small (< 5 MB) and openly licensed, documented in `data/README.md` with source, licence, citation, column dictionary and SHA-256. If terms are unclear, download at runtime with a checksum rather than bundling.

## Code of conduct

Be kind, be specific, assume good faith. Reviews focus on the work, not the person. Harassment of any kind is not tolerated.
