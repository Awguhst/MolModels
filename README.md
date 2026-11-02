# Molecules & Models

*A practical path from data science to cheminformatics and bioinformatics.*

An open, step-by-step course for fresh graduates in informatics, chemistry, biology or mathematics:
scientific Python → machine learning → molecular property prediction, docking, sequence and protein
models, generative design. Built with [Quarto](https://quarto.org) and Python; every code cell is
executed when the site is built. Text CC BY 4.0, code MIT.

**Site:** hosted on [Railway](https://railway.com) from this repository (see [Deploying](#deploying-railway--docker)).

## Status (iteration 1)

| Part | Chapters | Status |
|---|---|---|
| I · Foundations | 0 Start here · 1 Scientific Python · 2 ML fundamentals | **complete**, with Labs 1–2, a checkpoint quiz, Appendix A (partial) and the glossary |
| I · Foundations | 3 Beyond linear models · 4 Deep learning essentials | planned (stub pages) |
| II · Cheminformatics | 5–8 | planned |
| III · Bioinformatics | 9–12 | planned |
| IV · Generative | 13–15 | planned |

See [ROADMAP.md](ROADMAP.md) for the outlines and [AUTHORING.md](AUTHORING.md) for how to add a chapter.

## Quick start (learners)

You do not need to install anything to follow the course: read the site and open the labs in Google Colab.
To run things locally:

```bash
git clone https://github.com/Awguhst/MolModels.git
cd MolModels
mamba env create -f environment.yml      # or: python -m venv .venv && .venv/bin/pip install -r requirements.txt
mamba activate molecules-models
python scripts/check_env.py              # ✅ / ❌ for every library
jupyter lab                              # open part-1-foundations/ch01-scientific-python/labs/lab-01-guided-eda.ipynb
```

## Quick start (authors / building the site)

Requirements: [Quarto ≥ 1.7](https://quarto.org/docs/get-started/) (1.10 is what this was built with), Python 3.12 with the
environment above (it includes JupyterLab, pytest, nbclient, nbformat, jsonschema, playwright).

```bash
python scripts/fetch_data.py             # downloads data/esol.csv (not redistributed) with SHA-256 check
quarto preview                           # live preview with the navigation regenerated on every render
quarto render                            # full build into _site/

pytest                                   # front-matter schema, content rules, data checksums,
                                         # student-notebook drift, notebook execution, rendered-site checks
playwright install chromium              # once
python scripts/review_site.py            # screenshots at 1440/1024/390 in both themes + axe-core -> _review/
python scripts/check_contrast.py         # WCAG contrast audit of the design tokens
bash scripts/lighthouse.sh               # optional: Lighthouse on four pages, served gzip-compressed -> _review/lighthouse/
python scripts/serve_site.py             # browse _site/ locally with gzip, as GitHub Pages serves it
```

Quarto must use the course environment: activate it before running Quarto, or set `QUARTO_PYTHON` to its interpreter.
On a first full render the labs and episodes execute (about 3–5 minutes); later renders reuse `_freeze/`.

## Deploying (Railway / Docker)

The `Dockerfile` renders the whole site in a Python 3.12 + Quarto 1.10.20 image (data download, full execution,
no `_freeze/`) and copies `_site/` into a small nginx image that listens on `$PORT`. `railway.json` tells Railway
to build it and to health-check `/healthz`.

1. In Railway: **New project → Deploy from GitHub repo →** `Awguhst/MolModels`. Railway picks up `railway.json`;
   no variables are required.
2. **Settings → Networking → Generate domain** (or add a custom domain), then redeploy once. The build reads
   `RAILWAY_PUBLIC_DOMAIN` and writes it into the sitemap, the Open Graph tags and the citation text. To use a
   different address, set the service variable `SITE_URL` (for example `https://molmodels.org/`).
3. Every push to `main` rebuilds and redeploys. A build takes about 5–10 minutes because every episode and
   lab executes; if it fails, the previous deployment stays live.

The image is built without the git history (`.git` is excluded from the build context), so the "last updated"
dates on episodes fall back to the file dates of the build checkout. Run the same image locally with:

```bash
docker build -t molmodels .
docker run --rm -p 8080:8080 molmodels            # http://localhost:8080/
```

## Repository layout

```
_quarto.yml                 site configuration (navigation is generated into _sidebar.yml)
course.yml                  parts, appendices and sidebar resources
brand/                      brand.yml (light/dark), logo
assets/                     scss/ (design tokens + rules), fonts/, js/, mpl/ (matplotlib style), highlight/, katex/
_extensions/mm/             Quarto extension: callouts, maths, episode footer/key points, glossary shortcodes, title block
_includes/mm-setup.qmd      hidden setup cell every episode includes (figure theming)
index.qmd about.qmd cite.qmd
part-1-foundations/         ch00-start-here/ ch01-scientific-python/ ch02-ml-fundamentals/ (+ stubs ch03, ch04)
part-2-cheminformatics/ part-3-bioinformatics/ part-4-generative/     stub chapters
appendices/                 maths-refresher.qmd, glossary.qmd, key-points.qmd, stubs C and D
data/                       penguins.csv + README.md (sources, licences, checksums); esol.csv is downloaded
glossary.yml                single source for the glossary page and tooltips
scripts/                    build_course_data.py, post_render.py, fetch_data.py, check_env.py,
                            make_student_notebooks.py, new_episode.py, new_chapter.py, review_site.py,
                            check_contrast.py, lighthouse.sh, serve_site.py, subset_fonts.sh
tests/                      pytest suite (see above)
.github/workflows/          publish.yml: render → test → link check (→ GitHub Pages, if enabled; see below)
Dockerfile, docker/         production image: Quarto render stage + nginx serve stage (nginx.conf.template)
railway.json                Railway build and health-check settings
_review/screenshots/        responsive screenshots from scripts/review_site.py
```

## After forking

Search and replace `Awguhst/MolModels` and `YOUR NAME` in `_quarto.yml`, `CITATION.cff`, `cite.qmd`,
`about.qmd`, `README.md`, the lab notebooks and `LICENSE`, then deploy on Railway as above. To publish on
GitHub Pages instead (or as well), enable Pages with "GitHub Actions" as the source and set the repository
variable `DEPLOY_TO_GITHUB_PAGES` to `true`; the workflow then deploys on every push to `main`.

## Licences

Course text and figures: [CC BY 4.0](LICENSE-CONTENT.md). Code: [MIT](LICENSE). Datasets, fonts and vendored
libraries keep their own licences, listed in `LICENSE-CONTENT.md` and `data/README.md`.

## Citing

See [cite.qmd](cite.qmd) / the *Cite this course* page, or `CITATION.cff`.
