#!/bin/sh
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH='' cd -- "$script_dir/.." && pwd)
case_g2=$script_dir/cases/g2-passenger-half-turn
case_h006=$script_dir/cases/h006-illustrative
case_shared_zero=$script_dir/cases/shared-camber-zero
regressions=$script_dir/regressions
work_dir=$(mktemp -d /tmp/econometrician-caster-checks.XXXXXX)
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM

require_all=${REQUIRE_ALL_LANGUAGES:-0}

blocked() {
  language=$1
  reason=$2
  printf 'BLOCKED\t%s\t%s\n' "$language" "$reason"
  if [ "$require_all" = 1 ]; then
    exit 1
  fi
}

expect_rejection() {
  expected=$1
  output=$2
  shift 2
  if "$@" >"$output" 2>&1; then
    printf 'FAIL\texpected rejection: %s\n' "$expected" >&2
    exit 1
  fi
  grep -F "$expected" "$output" >/dev/null
}

if command -v Rscript >/dev/null 2>&1; then
  Rscript "$script_dir/r/caster_receipt.R" "$case_g2" >"$work_dir/r-g2.tsv"
  "$script_dir/check_receipt.sh" "$work_dir/r-g2.tsv" R
  Rscript "$script_dir/r/caster_receipt.R" "$case_h006" >"$work_dir/r-h006.tsv"
  grep -F 'error_bar_status	illustrative_only_not_error_bar' "$work_dir/r-h006.tsv" >/dev/null
  grep -F 'propagated_standard_deviation_deg	0.863804278906' "$work_dir/r-h006.tsv" >/dev/null
  Rscript "$script_dir/r/caster_receipt.R" "$case_shared_zero" >"$work_dir/r-shared-zero.tsv"
  grep -F 'propagated_variance_deg2	0.000000000000' "$work_dir/r-shared-zero.tsv" >/dev/null
  expect_rejection designed_positions_not_iid "$work_dir/r-designed.txt" \
    Rscript "$script_dir/r/caster_receipt.R" "$case_g2" \
      --resampling "$regressions/designed-steering-positions.tsv"
  expect_rejection bootstrap_measurement_error_double_count "$work_dir/r-overlap.txt" \
    Rscript "$script_dir/r/caster_receipt.R" "$case_h006" \
      --resampling "$regressions/bootstrap-error-overlap.tsv"
  expect_rejection incompatible_observation_provenance "$work_dir/r-state.txt" \
    Rscript "$script_dir/r/caster_receipt.R" "$regressions/incompatible-state"
  printf 'PASS\tR regressions\n'
else
  blocked R 'Rscript not found'
fi

ithon_bin=${ITHON_BIN:-}
if [ -n "$ithon_bin" ] && [ -x "$ithon_bin" ]; then
  ITHON_CHECK_RECEIPT="$work_dir/ithon-check.jsonl" \
    "$ithon_bin" "$script_dir/ithon/caster_receipt.pi" >"$work_dir/ithon.tsv"
  "$script_dir/check_receipt.sh" "$work_dir/ithon.tsv" Ithon
  test -s "$work_dir/ithon-check.jsonl"
  grep -F '"schema": "ithon.checked.v1"' "$work_dir/ithon-check.jsonl" >/dev/null
  grep -F 'designed_steering_positions_bootstrap	REJECTED' "$work_dir/ithon.tsv" >/dev/null
  grep -F 'bootstrap_explicit_error_overlap	REJECTED' "$work_dir/ithon.tsv" >/dev/null
  printf 'PASS\tIthon whole-module check receipt\n'
else
  blocked Ithon 'set ITHON_BIN to the pinned Ithon launcher'
fi

if command -v runghc >/dev/null 2>&1; then
  runghc "$script_dir/haskell/CasterReceipt.hs" "$case_g2" >"$work_dir/haskell-g2.tsv"
  "$script_dir/check_receipt.sh" "$work_dir/haskell-g2.tsv" Haskell
  runghc "$script_dir/haskell/CasterReceipt.hs" "$case_h006" >"$work_dir/haskell-h006.tsv"
  grep -F 'error_bar_status	illustrative_only_not_error_bar' "$work_dir/haskell-h006.tsv" >/dev/null
  grep -F 'propagated_standard_deviation_deg	0.863804278906' "$work_dir/haskell-h006.tsv" >/dev/null
  runghc "$script_dir/haskell/CasterReceipt.hs" "$case_shared_zero" >"$work_dir/haskell-shared-zero.tsv"
  grep -F 'propagated_variance_deg2	0.000000000000' "$work_dir/haskell-shared-zero.tsv" >/dev/null
  expect_rejection designed_positions_not_iid "$work_dir/haskell-designed.txt" \
    runghc "$script_dir/haskell/CasterReceipt.hs" "$case_g2" \
      --resampling "$regressions/designed-steering-positions.tsv"
  expect_rejection bootstrap_measurement_error_double_count "$work_dir/haskell-overlap.txt" \
    runghc "$script_dir/haskell/CasterReceipt.hs" "$case_h006" \
      --resampling "$regressions/bootstrap-error-overlap.tsv"
  expect_rejection incompatible_observation_provenance "$work_dir/haskell-state.txt" \
    runghc "$script_dir/haskell/CasterReceipt.hs" "$regressions/incompatible-state"
  printf 'PASS\tHaskell regressions\n'
else
  blocked Haskell 'runghc not found'
fi

if command -v agda >/dev/null 2>&1; then
  mkdir -p "$work_dir/agda"
  (
    cd "$script_dir/agda"
    agda --compile --compile-dir="$work_dir/agda" CasterReceipt.agda
  )
  "$work_dir/agda/CasterReceipt" >"$work_dir/agda.tsv"
  "$script_dir/check_receipt.sh" "$work_dir/agda.tsv" Agda
  grep -F 'designed_steering_positions_bootstrap	REJECTED' "$work_dir/agda.tsv" >/dev/null
  printf 'PASS\tAgda compiled kernel\n'
else
  blocked Agda 'agda not found'
fi

idric_bin=${IDRIC_BIN:-}
if [ -n "$idric_bin" ] && [ -x "$idric_bin" ]; then
  idric_bootstrap_root=${IDRIC_BOOTSTRAP_ROOT:-}
  if [ -n "$idric_bootstrap_root" ]; then
    idric_library_path=
    for idric_library in prelude base linear network contrib test; do
      idric_library_path="${idric_library_path}${idric_bootstrap_root}/_/libs/${idric_library}/build/ttc:"
    done
    export IDRIS2_PATH="$idric_library_path"
    export IDRIS2_DATA="$idric_bootstrap_root/_/support"
    idric_runtime_library=$idric_bootstrap_root/_/support/c
  else
    idric_runtime_library=
  fi
  (
    cd "$script_dir/idric"
    "$idric_bin" --check CasterReceipt.idric
    "$idric_bin" --output-dir "$work_dir" -o idric-caster-receipt \
      CasterReceipt.idric
  )
  if [ -n "$idric_runtime_library" ]; then
    LD_LIBRARY_PATH="${idric_runtime_library}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
      "$work_dir/idric-caster-receipt" >"$work_dir/idric.tsv"
  else
    "$work_dir/idric-caster-receipt" >"$work_dir/idric.tsv"
  fi
  "$script_dir/check_receipt.sh" "$work_dir/idric.tsv" 'Idriç'
  grep -F 'designed_steering_positions_bootstrap	REJECTED' "$work_dir/idric.tsv" >/dev/null
  printf 'PASS\tIdriç compiled kernel\n'
else
  blocked 'Idriç' 'set IDRIC_BIN to the pinned Idriç compiler'
fi

printf 'PASS\tcaster checks complete at %s\n' "$(git -C "$repo_root" rev-parse HEAD)"
