# Linux & Bash practice workspace

Original synthetic teaching fixtures for Molecules & Models, Chapters 16–18.
Created for this course; data and accompanying code are licensed under the
repository's MIT licence. No external data, accounts, or downloads are needed
after obtaining the bundle. These fixtures are not experimental observations,
reference sequences, or a scientific benchmark.

## Files and schema

All text files use UTF-8 and LF line endings. TSV files have one header row,
literal tab separators, no quoted fields, no embedded tabs/newlines, and no
missing values. This deliberately simple contract makes basic awk/cut exercises
appropriate. Use a CSV/TSV-aware parser for more complicated real exports.

- `samples.tsv`: six fictional samples. `sample_id` is unique; `condition` is
  control or treated; `reads_million` is an illustrative non-negative number of
  sequencing reads in millions; `qc_status` is pass or fail.
- `compounds.tsv`: six illustrative molecular records. `compound_id` is unique;
  `smiles` is a molecular text representation; `mol_weight` is an illustrative
  molecular weight in g/mol; `logS` is an illustrative log10(mol/L) solubility
  target; `split` is an already assigned train/test label. The numbers are not
  validated measurements. The scripts do not calculate chemistry or fit models.
- `sequences.fasta`: three artificial DNA records. Sequence lines are wrapped
  to demonstrate that line counts and record counts differ. There are no
  accessions or real organisms associated with these records.
- `pipeline.log`: six fabricated log messages, including two WARN lines and one
  ERROR line. A final INFO message does not establish that a scientific job
  succeeded; use exit codes and validated outputs.
- `scripts/`: the Chapter 18 Bash and Python examples. Run them only on the
  practice data until you understand their input and output contracts.

## Layout after extracting linux-bash-practice.zip

The ZIP contains `data/raw/`, `scripts/`, and this README directly. Extract it
into a new folder, such as `mm-linux-lab`. Open Bash in that folder and run
`mkdir -p results logs`. All tutorial paths are relative to this workspace root.
Raw files stay in `data/raw/`; derived outputs go under `results/`.

For an existing checkout, `python scripts/build_linux_bash_bundle.py` rebuilds
the ZIP deterministically. Quarto runs this before every site render. The file
`SHA256SUMS` inside the ZIP uses paths relative to the extracted workspace;
`sha256sum -c SHA256SUMS` verifies its source files on Linux.

## Results you can check by hand

- Samples: 6 data rows; pass IDs S01, S02, S04, S05; fail IDs S03, S06.
- Passing reads: 68.3 million in total, mean 17.075 million.
- Conditions: 3 control and 3 treated rows. Passing reads by condition:
  control 28.1 million; treated 40.2 million.
- Compounds: 4 train and 2 test rows. Keep those assignments unchanged.
- FASTA: 3 headers; sequence lengths 12, 10, and 8 nucleotides.
- Log: 2 WARN lines and 1 ERROR line.

Small rounding differences in formatted numbers are expected; changed IDs or
record counts need investigation. Successful execution is a software check,
not evidence of scientific validity.
