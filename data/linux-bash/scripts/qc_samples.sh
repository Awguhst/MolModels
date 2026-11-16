#!/usr/bin/env bash
# Validate the teaching TSV, then keep passing samples with >=10 million reads.
set -euo pipefail
export LC_ALL=C

if (( $# != 2 )); then
    printf 'Usage: bash qc_samples.sh INPUT_TSV OUTPUT_TSV\n' >&2
    exit 2
fi
input=$1
output=$2
[[ -f "$input" && -r "$input" ]] || { printf 'Unreadable input: %s\n' "$input" >&2; exit 2; }
[[ ! "$input" -ef "$output" ]] || { printf 'Input and output must differ\n' >&2; exit 2; }
[[ -n "$output" && ! -d "$output" ]] || { printf 'Output must name a file\n' >&2; exit 2; }
mkdir -p -- "$(dirname -- "$output")"
temp=$(mktemp "${output}.tmp.XXXXXX")
trap 'rm -f -- "$temp"' EXIT

if ! awk -F '\t' '
BEGIN { OFS = "\t" }
NR == 1 {
    if ($0 != "sample_id\tcondition\treads_million\tqc_status") {
        print "Invalid sample header" > "/dev/stderr"; bad = 1; exit 2
    }
    print "sample_id", "condition", "reads_million"; next
}
{
    if (NF != 4 || $1 !~ /^S[0-9]+$/ || seen[$1]++ ||
        ($2 != "control" && $2 != "treated") ||
        $3 !~ /^[0-9]+([.][0-9]+)?$/ ||
        ($4 != "pass" && $4 != "fail")) {
        print "Invalid sample row " NR > "/dev/stderr"; bad = 1; exit 2
    }
    if ($4 == "pass" && $3 + 0 >= 10) print $1, $2, $3
}
END {
    if (NR < 2 && !bad) {
        print "No sample records" > "/dev/stderr"; bad = 1
    }
    if (bad) exit 2
}' "$input" > "$temp"; then
    printf 'Sample QC failed; output was not replaced\n' >&2
    exit 2
fi
mv -- "$temp" "$output"
printf 'Wrote %s\n' "$output" >&2
