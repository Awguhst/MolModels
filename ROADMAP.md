# Roadmap

Each Part has an accent colour (violet, amber, green, coral) used in the navigation and the metro map on the home page.
"Built" chapters have episodes, exercises, a lab and a checkpoint; "planned" chapters have a stub page with an outline.

## Part I · Foundations: ML & data science (violet)

Part I is complete: 27 episodes across Chapters 0–4, four CPU-friendly labs, checkpoints for Chapters 1–4, key-point summaries and supporting appendices.

| # | Chapter | Built content |
|---|---|---|
| 0 | Start here | Course paths, environment setup, scientific-data habits and readiness self-check |
| 1 | Scientific Python | Python, NumPy, pandas, visualisation, solubility EDA; Lab 1: guided breast-cancer data exploration |
| 2 | ML fundamentals | Regression, metrics, regularisation, classification, pipelines and leakage; dedicated cross-validation and hyperparameter-tuning lessons; Lab 2: solubility prediction |
| 3 | Beyond linear models | Trees, forests and boosting, SVMs, PCA, clustering and interpretation; Lab 3: nested model-family comparison |
| 4 | Deep learning essentials | Tensors, autograd, MLPs and losses, minibatch training, validation and regularisation; Lab 4: a CPU neural-network experiment |

The shared workflow defines the prediction question, independent sample unit, baseline and metric before selection. Preprocessing is fitted inside training folds. Searches use development data; grouped and temporal designs match intended use; nested CV evaluates an entire selection procedure. Fold variability is distinguished from confidence intervals and individual prediction uncertainty. Error analysis motivates hypotheses without claiming causation.

Chapter 3 reuses existing datasets and scikit-learn; Chapter 4 adds pinned CPU PyTorch 2.9.1. No GPU, paid API or new dataset is required. All labs ship student and solution notebooks, with student versions generated from tagged solution cells.

## Part II · Cheminformatics (amber)

| # | Chapter | Planned content |
|---|---|---|
| 5 | Molecules as data | SMILES, RDKit, descriptors, Morgan fingerprints, Tanimoto similarity search; Lab: recompute ESOL descriptors from SMILES |
| 6 | QSAR and property prediction | scaffold/time splits, applicability domain, uncertainty (ensembles, conformal), activity cliffs; Lab: scaffold-split benchmark |
| 7 | Graph neural networks for molecules | graph featurisation, message passing, a minimal GNN in PyTorch Geometric, fair comparison with fingerprints |
| 8 | Structure-based design | PDB files, binding sites, AutoDock Vina docking, pose interpretation, ML rescoring; Lab: dock a small library |

Adds to `environment.yml`: rdkit, openbabel, vina, torch-geometric (PyTorch is already installed for Part I).

## Part III · Bioinformatics (green)

| # | Chapter | Planned content |
|---|---|---|
| 9 | Biological sequences and databases | Biopython, FASTA/GenBank, pairwise alignment, BLAST concepts, identity clustering |
| 10 | ML on sequences | k-mers, one-hot, sequence-identity splits, 1-D CNNs, protein language model embeddings |
| 11 | Omics data | count matrices, normalisation, QC, PCA/UMAP, clustering, differential expression, cell typing with scanpy |
| 12 | Protein structure | predicted structures and confidence, structure-derived features, RMSD/TM-score, structure-aware splits |

Adds: biopython, scanpy, anndata, (small) pre-computed ESM embeddings shipped as data.

## Part IV · Generative models & frontiers (coral)

| # | Chapter | Planned content |
|---|---|---|
| 13 | Generative models for molecules | VAEs, SMILES/SELFIES language models, diffusion and flow models in outline, evaluation of generated sets |
| 14 | Generative design loops | multi-objective optimisation, docking-guided generation, active learning, protein design concepts |
| 15 | Capstone projects | four project briefs, reporting template, peer review and reproducibility checklist |

Adds: selfies, pytorch.

## Appendices

| | Appendix | Status |
|---|---|---|
| A | Maths refresher (vectors/matrices, dot products, gradients, mean/variance/distributions, logarithms) | built for Foundations, including eigenvectors/SVD for PCA and classification losses; extend for later specialist topics |
| B | Glossary | built; grows with every chapter |
| C | Reproducibility toolkit | built: provenance, environments, splits, saved procedures and report template |
| D | Further reading | built for Foundations with annotated primary documentation |

## Cross-cutting work for later iterations

- "Download this page as a notebook" on every episode (the custom callouts need to degrade to Markdown).
- Lighthouse performance run in CI once the site is deployed.
- Translations: the glossary and callout labels are the first things to internationalise.
