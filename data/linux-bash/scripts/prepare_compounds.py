#!/usr/bin/env python3
"""Validate a synthetic descriptor table and preserve its declared train/test split."""
from __future__ import annotations

import argparse
import csv
import math
import os
from pathlib import Path
import tempfile


def prepare(source: Path, destination: Path) -> None:
    if source.resolve() == destination.resolve():
        raise ValueError("input and output must differ")
    fields = ["compound_id", "smiles", "mol_weight", "logS", "split"]
    rows = []
    seen = set()
    with source.open(newline="", encoding="utf8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != fields:
            raise ValueError("invalid compound header")
        for line, row in enumerate(reader, 2):
            if set(row) != set(fields) or any(not row[k] for k in fields):
                raise ValueError(f"missing or extra fields on row {line}")
            if row["compound_id"] in seen:
                raise ValueError(f"duplicate compound_id on row {line}")
            seen.add(row["compound_id"])
            weight, logs = float(row["mol_weight"]), float(row["logS"])
            if not math.isfinite(weight) or weight <= 0 or not math.isfinite(logs):
                raise ValueError(f"invalid numeric value on row {line}")
            if row["split"] not in {"train", "test"}:
                raise ValueError(f"invalid split on row {line}")
            rows.append(row)
    if not rows:
        raise ValueError("no compound records")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", newline="", encoding="utf8", dir=destination.parent,
            prefix=f".{destination.name}.", suffix=".tmp", delete=False,
        ) as handle:
            temp = Path(handle.name)
            writer = csv.DictWriter(
                handle, fieldnames=["compound_id", "mol_weight", "logS", "split"],
                delimiter="\t", lineterminator="\n", extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temp, destination)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        prepare(args.input, args.output)
    except (OSError, ValueError, csv.Error) as exc:
        parser.exit(2, f"Compound preparation failed: {exc}\n")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
