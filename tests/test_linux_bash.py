"""Exercise the downloadable scientific workflow, including failure and rerun paths."""
from __future__ import annotations

import csv
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

from conftest import ROOT
from build_linux_bash_bundle import OUTPUT, bundle_files, main as build_bundle

DATA = ROOT / "data" / "linux-bash"


@pytest.fixture
def bash():
    git_bash = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe"
    binary = str(git_bash) if os.name == "nt" and git_bash.exists() else shutil.which("bash")
    if not binary:
        pytest.skip("Bash is required to exercise the shell workflow")
    return binary


@pytest.fixture
def workspace(tmp_path):
    work = tmp_path / "scientific project with spaces"
    shutil.copytree(DATA, work)
    return work


def run(bash, work, script, *args):
    env = os.environ.copy()
    env["PYTHON"] = sys.executable.replace("\\", "/")
    return subprocess.run(
        [bash, (work / "scripts" / script).as_posix(), *(str(arg).replace("\\", "/") for arg in args)],
        cwd=work, env=env, text=True, capture_output=True, timeout=30,
    )


def rows(path):
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_practice_zip_matches_sources_and_checksums():
    build_bundle()
    first_hash = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    build_bundle()
    assert hashlib.sha256(OUTPUT.read_bytes()).hexdigest() == first_hash
    with ZipFile(OUTPUT) as archive:
        assert set(archive.namelist()) == set(bundle_files())
        for name, content in bundle_files().items():
            assert archive.read(name) == content
        for line in archive.read("SHA256SUMS").decode().splitlines():
            digest, name = line.split("  ", 1)
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest


def test_qc_preserves_original_and_rejects_malformed_rows(bash, workspace):
    source = workspace / "samples.tsv"
    original = source.read_bytes()
    output = workspace / "results" / "passing samples.tsv"
    result = run(bash, workspace, "qc_samples.sh", source, output)
    assert result.returncode == 0, result.stderr
    assert [row["sample_id"] for row in rows(output)] == ["S01", "S02", "S04", "S05"]
    assert source.read_bytes() == original
    valid_output = output.read_bytes()
    source.write_text(original.decode().replace("12.4", "not-a-number"), encoding="utf8", newline="\n")
    result = run(bash, workspace, "qc_samples.sh", source, output)
    assert result.returncode != 0
    assert output.read_bytes() == valid_output
    assert not list(output.parent.glob("*.tmp.*"))


@pytest.mark.parametrize("contents", ["", "wrong\theader\n", "sample_id\tcondition\treads_million\tqc_status\n"])
def test_qc_rejects_empty_and_invalid_input(bash, workspace, contents):
    source = workspace / "invalid.tsv"
    source.write_text(contents, encoding="utf8", newline="\n")
    output = workspace / "invalid-output.tsv"
    result = run(bash, workspace, "qc_samples.sh", source, output)
    assert result.returncode != 0
    assert not output.exists()


def test_pipeline_preserves_split_and_refuses_overwrite(bash, workspace):
    destination = workspace / "results" / "first run"
    result = run(bash, workspace, "run_pipeline.sh", workspace, destination)
    assert result.returncode == 0, result.stderr
    assert (destination / "_SUCCESS").read_text().strip() == "complete"
    expected = {row["compound_id"]: row["split"] for row in rows(workspace / "compounds.tsv")}
    actual = {row["compound_id"]: row["split"] for row in rows(destination / "compounds-model.tsv")}
    assert actual == expected
    assert len(rows(destination / "samples-qc.tsv")) == 4
    before = {p.name: p.read_bytes() for p in destination.iterdir()}
    rerun = run(bash, workspace, "run_pipeline.sh", workspace, destination)
    assert rerun.returncode != 0
    assert before == {p.name: p.read_bytes() for p in destination.iterdir()}
    for manifest, base in (("input-sha256.txt", workspace), ("script-sha256.txt", workspace / "scripts"), ("output-sha256.txt", destination)):
        for line in (destination / manifest).read_text().splitlines():
            digest, name = line.split(maxsplit=1)
            assert hashlib.sha256((base / name.lstrip("*")).read_bytes()).hexdigest() == digest


def test_pipeline_does_not_publish_failed_run(bash, workspace):
    (workspace / "compounds.tsv").write_text("invalid\n", encoding="utf8", newline="\n")
    destination = workspace / "results" / "failed run"
    result = run(bash, workspace, "run_pipeline.sh", workspace, destination)
    assert result.returncode != 0
    assert not destination.exists()
    assert not list(destination.parent.glob(".mm-pipeline.*"))


def test_qc_requires_a_file_destination(bash, workspace):
    output = workspace / "results"
    output.mkdir()
    result = run(bash, workspace, "qc_samples.sh", workspace / "samples.tsv", output)
    assert result.returncode != 0
    assert list(output.iterdir()) == []
