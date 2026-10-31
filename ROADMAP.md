# Roadmap

Each Part has an accent colour (violet, amber, green, coral) used in the navigation and the metro map on the home page.
"Built" chapters have episodes, exercises, a lab and a checkpoint; "planned" chapters have a stub page with an outline.

## Part I · Foundations: ML & data science (violet)

| # | Chapter | Status |
|---|---|---|
| 0 | Start here: how the course works, setup, self-check | built |
| 1 | Scientific Python for data work: NumPy, pandas, plotting, EDA (Lab 1: guided EDA, breast cancer Wisconsin) | built |
| 2 | Machine learning fundamentals with scikit-learn (Lab 2: predict ESOL solubility end to end; checkpoint quiz) | built |
| 3 | Beyond linear models: trees, ensembles, SVMs, PCA, clustering, model interpretation | planned |
| 4 | Deep learning essentials with PyTorch: tensors, autograd, MLPs, training loops | planned |

### Proposed outline for Chapter 3 (next iteration)

Working title: **Beyond linear models**. Reuses ESOL (regression) and breast cancer Wisconsin (classification) so that every
new model is compared against the Chapter 2 baselines on identical splits. Suggested episodes (teaching + exercise minutes):

1. **Decision trees** (30 + 15). How a tree splits; `DecisionTreeRegressor`/`Classifier`; depth as the overfitting knob with a
   validation curve; reading a tree with `plot_tree`; why single trees are unstable. Bridge: chemists read trees as decision rules.
2. **Random forests and gradient boosting** (40 + 20). Bagging and feature subsampling; out-of-bag estimates; `RandomForestRegressor`
   vs `HistGradientBoostingRegressor`; learning rate and number of trees; honest comparison with ridge from Lab 2 using the same
   `KFold(random_state=42)`; the chapter's "Debug this" (fitting with `n_estimators=1` and reporting OOB score).
3. **Support vector machines and kernels** (35 + 20). Margin intuition; `SVC`/`SVR`; the RBF kernel as similarity; `C` and `gamma`
   with a 2-D validation heatmap; why scaling is mandatory; a bridge to Tanimoto kernels on fingerprints (Part II).
4. **Unsupervised learning: PCA** (35 + 20). Variance, components and loadings on the 30 breast-cancer features; scree plot;
   PCA for visualisation vs for preprocessing; the leakage trap of fitting PCA on all data. Maths deep-dive: eigen-decomposition.
5. **Unsupervised learning: clustering** (30 + 20). k-means and the elbow/silhouette; hierarchical clustering with a dendrogram;
   clustering penguins and ESOL descriptors; what clusters do and do not mean. Bridge to single-cell clustering (Chapter 11).
6. **Interpreting models** (35 + 20). Permutation importance (on test data, with `GroupKFold` caveats); partial dependence and ICE
   plots; SHAP-style additive explanations explained without the library; interpretability vs causality. Bridge: what a chemist
   can and cannot conclude from "PSA is the most important descriptor".
- **Lab 3: tabular bake-off** (90 min). Ridge vs random forest vs gradient boosting vs SVR on ESOL with nested CV; PCA + logistic
  regression vs random forest on breast cancer; a permutation-importance figure; a one-paragraph recommendation.
- **Checkpoint quiz** (10 questions).

New glossary terms: decision tree, ensemble, bagging, boosting, out-of-bag, kernel, margin, principal component, loading,
explained variance, k-means, silhouette, dendrogram, permutation importance, partial dependence.
New library needs: none beyond scikit-learn (SHAP is explained, not installed).

## Part II · Cheminformatics (amber)

| # | Chapter | Planned content |
|---|---|---|
| 5 | Molecules as data | SMILES, RDKit, descriptors, Morgan fingerprints, Tanimoto similarity search; Lab: recompute ESOL descriptors from SMILES |
| 6 | QSAR and property prediction | scaffold/time splits, applicability domain, uncertainty (ensembles, conformal), activity cliffs; Lab: scaffold-split benchmark |
| 7 | Graph neural networks for molecules | graph featurisation, message passing, a minimal GNN in PyTorch Geometric, fair comparison with fingerprints |
| 8 | Structure-based design | PDB files, binding sites, AutoDock Vina docking, pose interpretation, ML rescoring; Lab: dock a small library |

Adds to `environment.yml`: rdkit, openbabel, vina, pytorch (CPU), torch-geometric.

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
| A | Maths refresher (vectors/matrices, dot products, gradients, mean/variance/distributions, logarithms) | built for Ch 1–2; extend with eigenvalues (Ch 3), probability (Ch 5+), information theory (Ch 10) |
| B | Glossary | built; grows with every chapter |
| C | Reproducibility toolkit | planned |
| D | Further reading | planned |

## Cross-cutting work for later iterations

- "Download this page as a notebook" on every episode (the custom callouts need to degrade to Markdown).
- Lighthouse performance run in CI once the site is deployed.
- Translations: the glossary and callout labels are the first things to internationalise.
