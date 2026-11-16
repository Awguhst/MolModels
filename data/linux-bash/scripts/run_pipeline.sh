#!/usr/bin/env bash
# Publish a complete, recorded teaching run; never overwrite an existing run.
set -euo pipefail
export LC_ALL=C

if (( $# != 2 )); then
    printf 'Usage: bash run_pipeline.sh INPUT_DIR NEW_OUTPUT_DIR\n' >&2
    exit 2
fi
input=$(cd -- "$1" && pwd)
output=${2%/}
[[ -n "$output" && ! -e "$output" && ! -L "$output" ]] || {
    printf 'Choose a new output directory: %s\n' "$output" >&2; exit 2;
}
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python=${PYTHON:-python3}
command -v "$python" > /dev/null || { printf 'Python not found: %s\n' "$python" >&2; exit 2; }
parent=$(dirname -- "$output")
mkdir -p -- "$parent"
parent=$(cd -- "$parent" && pwd)
output="$parent/$(basename -- "$output")"
stage=$(mktemp -d "$parent/.mm-pipeline.XXXXXX")
started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
cleanup() { if [[ -d "$stage" ]]; then rm -r -- "$stage"; fi; }
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

printf 'Starting sample QC\n' >&2
bash "$script_dir/qc_samples.sh" "$input/samples.tsv" "$stage/samples-qc.tsv"
printf 'Starting compound preparation\n' >&2
"$python" "$script_dir/prepare_compounds.py" "$input/compounds.tsv" "$stage/compounds-model.tsv"
(
    cd -- "$input"
    sha256sum samples.tsv compounds.tsv
) > "$stage/input-sha256.txt"
(
    cd -- "$script_dir"
    sha256sum qc_samples.sh prepare_compounds.py run_pipeline.sh
) > "$stage/script-sha256.txt"
{
    printf 'started_utc=%s\n' "$started_utc"
    printf 'input_dir=%s\n' "$input"
    printf 'sample_rule=qc_status:pass,reads_million:>=10\n'
    printf 'bash_version=%s\n' "$BASH_VERSION"
    "$python" --version
} > "$stage/run-info.txt"
(
    cd -- "$stage"
    sha256sum samples-qc.tsv compounds-model.tsv
) > "$stage/output-sha256.txt"
printf 'complete\n' > "$stage/_SUCCESS"
[[ ! -e "$output" && ! -L "$output" ]] || { printf 'Output appeared during run\n' >&2; exit 2; }
mv -T -- "$stage" "$output"
printf 'Complete: %s\n' "$output" >&2
