#!/bin/sh
set -eu

receipt=${1:?usage: check_receipt.sh RECEIPT IMPLEMENTATION}
implementation=${2:?usage: check_receipt.sh RECEIPT IMPLEMENTATION}

field() {
  awk -F '\t' -v key="$1" '$1 == key { print $2; found = 1 } END { if (!found) exit 1 }' "$receipt"
}

assert_close() {
  key=$1
  expected=$2
  tolerance=$3
  actual=$(field "$key")
  awk -v actual="$actual" -v expected="$expected" -v tolerance="$tolerance" \
    'BEGIN { difference = actual - expected; if (difference < 0) difference = -difference; exit !(difference <= tolerance) }'
}

test "$(field status)" = PASS
test "$(field implementation)" = "$implementation"
test "$(field theta_source_kind)" = manual_17.4_to_1_nominal_conversion
test "$(field error_bar_status)" = not_computed
test "$(field bounds_status)" = historical_stress_test_not_measurement_uncertainty

if [ "$implementation" = Haskell ]; then
  test "$(field calculation_role)" = measurement_path
  test "$(field numeric_carrier)" = ieee754_binary32
  test "$(field caster_magnitude_deg)" = 5.6
  test "$(field final_report_status)" = blocked_missing_empirical_uncertainty_scale
  # The long G2 decimal is a regression oracle only. Binary32 is expected to
  # agree at its own scale, not reproduce binary64 digits.
  assert_close internal_caster_magnitude_deg 5.568798743106686 0.00001
  numeric_tolerance=0.00001
else
  test "$(field calculation_role)" = regression_oracle
  test "$(field numeric_carrier)" = binary64_reference
  assert_close caster_magnitude_deg 5.568798743106686 0.000000001
  numeric_tolerance=0.000000001
fi

assert_close three_pair_correlated_variance 1.083333333333 "$numeric_tolerance"
assert_close three_pair_naive_variance 0.416666666667 "$numeric_tolerance"

nonlinear_interval=$(field nonlinear_interval_deg)
nonlinear_lower=${nonlinear_interval%%,*}
nonlinear_upper=${nonlinear_interval#*,}
awk -v actual="$nonlinear_lower" -v tolerance="$numeric_tolerance" 'BEGIN { expected = 3.778894920165921; d = actual - expected; if (d < 0) d = -d; exit !(d <= tolerance) }'
awk -v actual="$nonlinear_upper" -v tolerance="$numeric_tolerance" 'BEGIN { expected = 10.735418793944593; d = actual - expected; if (d < 0) d = -d; exit !(d <= tolerance) }'

printf 'PASS\t%s receipt\n' "$implementation"
