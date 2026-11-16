#!/usr/bin/env python
"""Build the offline practice ZIP from its tracked source files, reproducibly."""
from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "linux-bash"
OUTPUT = DATA / "linux-bash-practice.zip"
FIXTURES = ("samples.tsv", "compounds.tsv", "sequences.fasta", "pipeline.log")


def bundle_files() -> dict[str, bytes]:
    files = {f"data/raw/{name}": (DATA / name).read_bytes() for name in FIXTURES}
    files["README.md"] = (DATA / "README.md").read_bytes()
    scripts = sorted((DATA / "scripts").glob("*"))
    for script in scripts:
        if script.is_file() and script.suffix in {".py", ".sh"}:
            files[f"scripts/{script.name}"] = script.read_bytes()
    checksums = "".join(f"{hashlib.sha256(data).hexdigest()}  {name}\n" for name, data in sorted(files.items()))
    files["SHA256SUMS"] = checksums.encode("utf8")
    return files


def main() -> None:
    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as archive:
        for name, content in sorted(bundle_files().items()):
            entry = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = (0o100644 << 16)
            archive.writestr(entry, content)
    print(f"[build_linux_bash_bundle] wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
