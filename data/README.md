# Datasets

Small datasets live here. Anything whose redistribution terms are unclear is **not** bundled;
it is downloaded at build time by `scripts/fetch_data.py` with SHA-256 verification and cached
locally (git-ignored).

## Palmer penguins: `penguins.csv` (bundled)

| | |
|---|---|
| Source | https://github.com/allisonhorst/palmerpenguins (`inst/extdata/penguins.csv`) |
| Licence | CC0 1.0 (public domain dedication) |
| Citation | Horst AM, Hill AP, Gorman KB (2020). *palmerpenguins: Palmer Archipelago (Antarctica) penguin data.* R package version 0.1.0. https://allisonhorst.github.io/palmerpenguins/ doi:10.5281/zenodo.3960218 |
| Data origin | Gorman KB, Williams TD, Fraser WR (2014). Ecological sexual dimorphism and environmental variability within a community of Antarctic penguins (genus *Pygoscelis*). PLoS ONE 9(3):e90081. |
| Rows | 344 penguins |
| SHA-256 | `f204db2c753b0937caac3cb35258562c14f073e4bbc76be24b4c51ce22767a93` |

Columns:

| column | type | meaning |
|---|---|---|
| `species` | category | Adelie, Chinstrap or Gentoo |
| `island` | category | Biscoe, Dream or Torgersen (Palmer Archipelago) |
| `bill_length_mm` | float | culmen length in millimetres |
| `bill_depth_mm` | float | culmen depth in millimetres |
| `flipper_length_mm` | float | flipper length in millimetres |
| `body_mass_g` | float | body mass in grams |
| `sex` | category | female, male or missing |
| `year` | int | study year (2007–2009) |

Missing values are written as `NA`.

## ESOL / Delaney aqueous solubility: `esol.csv` (downloaded at build time, git-ignored)

| | |
|---|---|
| Canonical source used | https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/delaney-processed.csv (MoleculeNet / DeepChem copy) |
| Original publication | Delaney JS (2004). ESOL: Estimating aqueous solubility directly from molecular structure. *J. Chem. Inf. Comput. Sci.* 44(3):1000–1005. doi:10.1021/ci034243x |
| MoleculeNet | Wu Z et al. (2018). MoleculeNet: a benchmark for molecular machine learning. *Chem. Sci.* 9:513–530. |
| Redistribution | The MoleculeNet file carries no explicit licence statement, so it is not bundled here. Fetch it with `python scripts/fetch_data.py`. |
| Rows | 1128 compounds |
| SHA-256 | `8c06a76f0c6487d29ab0f903e6a7a7139f189ab3c1178f159c8be8964602f189` |

Columns (names exactly as in the file):

| column | type | meaning |
|---|---|---|
| `Compound ID` | str | compound name |
| `ESOL predicted log solubility in mols per litre` | float | Delaney's own model prediction (log₁₀ mol/L) |
| `Minimum Degree` | int | smallest number of heavy-atom neighbours of any atom |
| `Molecular Weight` | float | g/mol |
| `Number of H-Bond Donors` | int | hydrogen-bond donor count |
| `Number of Rings` | int | ring count |
| `Number of Rotatable Bonds` | int | rotatable bond count |
| `Polar Surface Area` | float | topological polar surface area, Å² |
| `measured log solubility in mols per litre` | float | **the target**: measured log₁₀ solubility (mol/L) |
| `smiles` | str | SMILES string of the molecule |

## Breast cancer Wisconsin (diagnostic)

Loaded directly with `sklearn.datasets.load_breast_cancer()`; nothing is stored here.
Source: Wolberg WH, Street WN, Mangasarian OL (1995), UCI Machine Learning Repository, doi:10.24432/C5DW2B.
569 samples, 30 features computed from digitised images of fine-needle aspirates, target 0 = malignant, 1 = benign (scikit-learn encoding).
