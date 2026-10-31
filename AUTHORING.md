# Authoring guide

This is the contract every chapter of *Molecules & Models* follows. It was written after building
the golden episode ([2.3 Evaluating models honestly](part-1-foundations/ch02-ml-fundamentals/03-evaluating-models.qmd));
copy that file's structure when in doubt. The tests in `tests/` enforce most of what is below.

Contents: [Workflow](#workflow) · [Anatomy of an episode](#anatomy-of-an-episode) · [Front matter](#front-matter) ·
[Callouts](#callout-vocabulary) · [Glossary](#glossary-terms) · [Code cells](#code-cells) · [Figures](#figures-light-and-dark) ·
[Labs](#labs) · [Chapter pages](#chapter-landing-pages) · [Style](#writing-style) · [Checklist](#checklist-adding-a-chapter) · [How it works](#how-the-machinery-works)

## Workflow

```bash
# one-time
mamba env create -f environment.yml && mamba activate molecules-models   # or: pip install -r requirements.txt
python scripts/fetch_data.py                   # downloads data/esol.csv with checksum verification

# author
python scripts/new_chapter.py --part 1 --chapter 3 --title "Beyond linear models" --short "Beyond linear models"
python scripts/new_episode.py --chapter 3 --episode 1 --title "Decision trees" --teaching 30 --exercises 20
quarto preview                                 # live preview; pre-render regenerates navigation automatically

# before committing
python scripts/make_student_notebooks.py       # if you touched a *-solutions.ipynb
pytest                                         # front matter, content rules, data, notebooks, rendered site
python scripts/review_site.py                  # screenshots + axe-core (needs: playwright install chromium)
```

Quarto needs to find the Python environment: activate it, or set `QUARTO_PYTHON` to its interpreter.

## Anatomy of an episode

One episode is one `.qmd` file, `NN-slug.qmd`, inside its chapter directory. Reading order of the page:

1. **Title block** (generated from front matter): breadcrumb, number + title, time/level line, Overview card (Questions | Objectives).
2. `{{< include /_includes/mm-setup.qmd >}}` as the very first line after the front matter. It is a hidden cell that styles figures and enables light/dark renderings.
3. **Opening paragraph**: the scientific question that motivates the episode. No "In this episode we will".
4. **Sections** (`##`), each following the same arc: motivating example → intuition in words or a figure → minimal maths (details in a `.deep-dive`) → code → interpretation of the output → pitfall.
5. **`## Exercises`**: 2–4 `.challenge` boxes graded `level=1` (★ check understanding), `2` (★★ apply), `3` (★★★ stretch), each with a nested `.solution`. One episode per chapter contains an exercise titled **"Debug this"** with a realistic broken snippet.
6. **`## Where this is going`**: one paragraph linking the idea to a later cheminformatics or bioinformatics chapter.
7. **Key points card** (generated from `keypoints`), then the footer (previous/next, edit/report, last updated). Both are generated, never hand-written.

Also required somewhere in the body: at least one `.predict` box and at least one `.bridge`. `tests/test_content_rules.py` checks all of this.

Length: 1,500–3,000 words plus code. Split anything longer into two episodes.

## Front matter

```yaml
---
title: "Evaluating models honestly"
chapter: 2
episode: 3
teaching: 35        # minutes
exercises: 20
level: beginner     # beginner | intermediate | advanced
questions:          # 1–5, phrased as a learner would ask
  - "Why can't I judge a model on the data it was trained on?"
objectives:         # 1–6, each starts with a verb and names a concrete skill
  - "Split data into training and test sets reproducibly."
keypoints:          # 1–8 sentences a learner should remember a month later
  - "Always compare against a simple baseline."
prerequisites: [ch02-ep02]   # episode ids: chCC-epNN or chCC-labNN
---
```

Validated against `tests/episode-schema.json`. Keep titles free of `$` maths and avoid leading numbers like `1.` (they parse as lists). Ids are derived: chapter 2 episode 3 is `ch02-ep03`; Lab 1 of chapter 1 is `ch01-lab01`.
The chapter directory's `_metadata.yml` supplies `chapter`, `chapter-id`, `chapter-title`, `chapter-short`, `chapter-href`; episodes never repeat those.

## Callout vocabulary

All callouts are fenced divs handled by `_extensions/mm/callouts.lua`. Titles accept inline markdown.

| Syntax | Renders as | Notes |
|---|---|---|
| `::: {.prereq}` | Prerequisite | use on chapter pages and the first episode |
| `::: {.note title="..."}` | Note | asides, definitions |
| `::: {.tip title="..."}` | Tip | |
| `::: {.pitfall title="..."}` | Common mistake | at least one per section is a good rhythm |
| `::: {.predict}` | Predict before you run | put it immediately before the cell it refers to |
| `::: {.challenge level=2 title="..."}` | Exercise ★★☆ | nest the solution inside it |
| `:::: {.solution}` | collapsed "Show solution" | code in solutions is executed; keep it short |
| `::: {.discussion}` | Discussion prompt | |
| `::: {.bridge audience="chem"}` | Chemist's corner | `chem`, `bio` (Biologist's corner), `math` (Maths corner), `cs` (For programmers) |
| `::: {.deep-dive title="..."}` | collapsed "Show the maths" | optional theory; never required to follow the episode |
| `::: {.checkpoint title="..."}` | multiple-choice question | see below |
| `::: {.definition title="..."}` | Definition 1, 2, ... | formal mathematics (Appendix A); numbered per page in order of appearance |
| `::: {.theorem title="..."}`, `::: {.proposition title="..."}` | Theorem 1 / Proposition 1 | state the result; put the argument in a `.proof` after it |
| `::: {.proof}` | collapsed "Show proof" | keep proofs short; a sketch is fine |

Nested divs use more colons (`::::`). Example:

```markdown
::: {.challenge level=2 title="Beat the baseline"}
Train a `Ridge` model and compare its test RMSE with the `DummyRegressor`.

:::: {.solution}
```{python}
ridge = Ridge(alpha=1.0).fit(X_train, y_train)
```
The RMSE falls because ... (always explain *why*).
::::
:::
```

### Checkpoint questions

```markdown
::: {.checkpoint title="Which metric?"}
A few molecules are predicted terribly and the rest well. Which metric moves most?

- [x] RMSE

  Correct: squaring the errors makes the few large ones dominate.
- [ ] MAE

  MAE treats every error proportionally, so a few large errors move it less.
- [ ] R²

  R² changes too, but it is a rescaled version of the squared error, not a separate signal.
:::
```

Exactly one option is `[x]`. Each option's feedback is the indented paragraph below it. The result is a `<details>` per
option: it works without JavaScript and is keyboard accessible; JavaScript only adds the running score. A chapter
checkpoint is a page `checkpoint.qmd` with `checkpoint-quiz: true` and ten of these.

## Glossary terms

Every term is defined once, in `glossary.yml`, and linked at first use in each episode:

```markdown
... the only way to measure {{< term generalisation >}} is to keep a {{< term test-set >}} ...
{{< term descriptor plural >}}        -> uses the `plural:` form
{{< term mae "MAE" >}}                -> custom display text
```

The shortcode produces a link to the glossary page plus a hover/focus tooltip (CSS only). The glossary page
(`appendices/glossary.qmd`) is `{{< glossary >}}`. Unknown ids print a warning at render time and fail
`tests/test_content_rules.py`. When you introduce a term, add it to `glossary.yml` with `id`, `term`, `short`
(tooltip, one sentence, plain text), `definition` (markdown, maths allowed), `chapter` and `see`.

## Code cells

- Learner-visible code is exactly what a learner would type. Anything else (seeding helpers, path juggling) goes in a cell with `#| echo: false`.
- One new idea per cell; cells ≤ 20 lines; every cell shows its output; truncate with `.head()`.
- Cells run top to bottom from the repository root (`execute-dir: project`), so data paths are `data/penguins.csv`. For ESOL, which is not bundled, use the local-then-URL idiom from episode 1.5 / 2.3.
- Seeds: `rng = np.random.default_rng(42)`, `random_state=42` (or `seed` inside an explicit loop over seeds).
- **No warnings.** `execute: warning: true` is deliberate: a warning in the rendered output is a bug. Fix the cause (use the current API) rather than filtering. `tests/test_rendered_site.py` fails on any stderr block.
- Modern APIs only: the matplotlib object-oriented interface (`fig, ax = plt.subplots()`), pandas 3 idioms (no chained assignment, `df.loc[...] = ...`, `observed=True` in `groupby` when grouping categoricals), current scikit-learn (`root_mean_squared_error`, `*Display.from_estimator`).
- Pinned versions live in `environment.yml` / `requirements.txt`. `scripts/check_env.py` prints them. matplotlib is held at 3.10.x because seaborn 0.13.2 emits deprecation warnings on 3.11.
- Non-executed snippets (for example a deliberately broken "Debug this" listing) use a plain ```` ```python ```` block.

## Figures: light and dark

Every cell that creates a figure:

```python
#| renderings: [light, dark]
#| fig-alt: "What the figure shows, for readers who cannot see it."
fig, ax = plt.subplots()
ax.scatter(x, y)
ax.set(xlabel="...", ylabel="... (units)")
plt.show()
```

How it works: the hidden setup cell applies `assets/mpl/mm-light.mplstyle` and registers an IPython hook. At the end of
every cell the hook displays each open figure twice, once as is and once with its *chrome* (backgrounds, text, spines,
grid, legend frame) recoloured for the dark theme; `plt.show()` is a no-op during rendering so figures survive until the hook
runs. Quarto's `renderings` option tags the two outputs `light-content` / `dark-content` and the theme switch shows the
right one. Learners who copy the visible code get the ordinary light figure. Consequences:

- the cell must emit *nothing else* (no `print`, no trailing expression), hence `plt.show()` as the last line;
- one figure per cell;
- do not use `fig-cap` or `label: fig-...` on these cells (Quarto limitation with `renderings`); write captions as text;
- data colours come from the palette in the mplstyle (colour-blind-safe, readable on both backgrounds); do not hard-code colours unless they are semantic;
- always give units in axis labels.

Why not two matplotlib styles? Any approach that re-runs the cell would double execution time and break cells with side effects; recolouring the finished figure is cheaper and keeps learner code untouched. The fallback of a single light figure on a framed panel is what you get automatically if you forget `renderings`; the tests will tell you.

## Labs

- Files: `labs/lab-NN-slug.qmd` (the lab page) and `labs/lab-NN-slug-solutions.ipynb` (**the single source of truth**). `python scripts/make_student_notebooks.py` writes `labs/lab-NN-slug.ipynb`; `pytest` fails if it is stale.
- Lab page front matter (schema `tests/lab-schema.json`): `title, chapter, lab, duration ("60–90 min"), minutes (integer, for the schedule), level, objectives, prerequisites-text, summary, dataset, notebook` (base name). The chapter page's lab card and its three buttons (Open in Colab, Download .ipynb, View solutions) are generated from it.
- Notebook structure: title + goals → setup cell (Colab-aware: `try: import google.colab` and `pip install` only what is missing) → data loading with local path then raw-GitHub fallback → numbered tasks → reflection questions.
- Cell tags (JupyterLab: View → Cell toolbar → Tags, or the cell metadata editor):
  - `solution`: replaced by a `# TODO` stub in the student version (leading comment lines are kept as the task statement);
  - `check`: friendly `assert`s that confirm the learner's result ("✅ check" cells); kept verbatim;
  - `solutions-only`: removed from the student notebook.
- Budget: CPU, under 3 minutes, no GPU, no accounts, no paid APIs. `tests/test_notebooks_execute.py` enforces time and warnings.
- Quarto executes and renders the solutions notebook as `labs/lab-NN-slug-solutions.html` (the "View solutions" page).

## Chapter landing pages

`index.qmd` has `chapter-index: true` and a `summary`, then includes the generated hero, schedule table and lab cards:

```markdown
{{< generated ch02-hero >}}
## What you will be able to do
- ...
## Schedule
{{< generated ch02-schedule >}}
## Lab
{{< generated ch02-labs >}}
```

A thin `key-points.qmd` includes `_generated/chNN-keypoints.md`. Stub chapters have `stub: true` in `_metadata.yml`,
an `index.qmd` with the "soon" banner, 4–6 topic bullets and 3 planned outcomes; they appear dimmed in the sidebar and as dashed stations on the roadmap.

## Writing style

- Second person, warm, precise, no filler. Short paragraphs (≤ 4 sentences). British spelling.
- Define every term at first use and link it with `{{< term >}}`.
- Lead with the scientific example, then intuition, then maths, then code. Interpret every output. Follow with the pitfall.
- Maths: `$...$` inline, `$$...$$` display. KaTeX is self-hosted and attached only to pages that contain maths (the `math.lua` filter sets a flag that `episode.lua` reads); readers without JavaScript see the TeX source. Keep maths in the body minimal; put derivations in `.deep-dive`. Avoid `$` in callout titles.
- Units everywhere: logS in log₁₀(mol/L), masses in g, lengths in mm.
- Never invent citations, dataset facts or API behaviour. If you cannot verify it, leave it out.
- Bridge boxes are written *for* that reader: chemists get bench analogies, biologists get experiments, mathematicians get the formal view, programmers get the engineering view.
- Each persona in README's audience table should be able to follow the episode without a difficulty jump. If a step assumes something a chemist or biologist would not know, add a bridge box or a link to the maths refresher.

## Checklist: adding a chapter

1. `python scripts/new_chapter.py --part P --chapter N --title "..." --short "..."` (or edit the existing stub: set `stub: false`, replace `index.qmd`).
2. For each episode: `python scripts/new_episode.py ...`, write it, add glossary terms, render it (`quarto render path/to/episode.qmd`), check for warnings in the output.
3. Write the lab: solutions notebook first, then `make_student_notebooks.py`, then the lab page. Run the notebook test.
4. Add the chapter checkpoint (`checkpoint.qmd`, 10 questions).
5. Update `ROADMAP.md` (move the chapter from planned to built) and the Chapter 0 "suggested paths" if needed.
6. `pytest`, `quarto render`, `python scripts/review_site.py`; look at the screenshots.
7. Re-read the chapter as each of the four personas; fix difficulty jumps.

## How the machinery works

| Piece | Where | Role |
|---|---|---|
| Pre-render | `scripts/build_course_data.py` | reads front matter → `_generated/course.json`, `_sidebar.yml` (via `metadata-files`), hero/schedule/lab/key-point includes, metro map SVG |
| Lua filters | `_extensions/mm/callouts.lua`, `math.lua`, `episode.lua` | callouts; TeX → KaTeX spans; key points card, footer, KaTeX + JS dependencies. Quarto parses `.solution` into its own "Proof" node before any filter runs, so `callouts.lua` reclaims those nodes with a `Proof` handler; `_quarto.yml` lists `filters: [mm, quarto]` so the extension runs first |
| Shortcodes | `_extensions/mm/term.lua`, `glossary.lua` | glossary tooltips and page (`glossary.yml` parsed by pandoc) |
| Title block | `_extensions/mm/partials/title-block.html` | episode / lab / plain title blocks from metadata |
| Post-render | `scripts/post_render.py` | sidebar decoration (numbers, times, check circles, "soon"), part accent on `<html>`, skip link, a11y fixes, CDN removal, guards Quarto's nav script against SVG links |
| Theme | `brand/*.yml`, `assets/scss/*.scss`, `assets/highlight/*.theme` | tokens as CSS custom properties in `_tokens.scss`; dark is the default layer, light overrides tokens. Design rules: colour is semantic only (one accent per Part, one per callout kind), callouts are a thin coloured rule rather than a box, headings are serif, links are ink-coloured with an accent underline, no all-caps labels. Any SCSS change needs a clean full render (`rm -rf _site && quarto render`) because the compiled CSS file name is hashed |
| JS | `assets/js/mm.js` | theme switch (Dark/Light/Auto), expand-all-solutions, quiz score, long-output collapse, print expansion, `/` search |
| Fonts | `assets/fonts/` | IBM Plex Sans, Source Serif 4, JetBrains Mono, subset with fontTools (`scripts/subset_fonts.sh`), served via `brand` typography |

Fonts: the spec's three families are used unchanged; they are subset to Latin + Greek + symbols (38–68 KB per face) and self-hosted. No CDN is contacted at runtime: `tests/test_rendered_site.py::test_no_runtime_cdn` guards this.
