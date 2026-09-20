#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT"
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider
if [ -f sources/dakota_caster_recheck.py ]; then
  LEGACY=sources
elif [ -f ../dakota-caster-recheck/dakota_caster_recheck.py ]; then
  LEGACY=../dakota-caster-recheck
else
  printf '%s
' 'legacy caster archive not present; benchmark tests passed, legacy byte-reproduction skipped' >&2
  exit 0
fi
PYTHONDONTWRITEBYTECODE=1 python "$LEGACY/dakota_caster_recheck.py" > /tmp/dakota_caster_recheck_results.json
python - /tmp/dakota_caster_recheck_results.json "$LEGACY/dakota_caster_recheck_results.json" <<'PY'
import json
import math
import sys


def compare(actual, expected, path="$"):
    if isinstance(actual, bool) or isinstance(expected, bool):
        if actual is not expected:
            raise AssertionError(f"{path}: {actual!r} != {expected!r}")
        return
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        # The archived iterated robust fit is solver/version dependent in its
        # last digits even when every reported scientific result agrees.  This
        # sub-microdegree comparison is intentionally looser than the separate
        # deterministic receipt checks, which retain their tighter tolerances.
        if not math.isclose(actual, expected, rel_tol=1e-6, abs_tol=1e-8):
            raise AssertionError(f"{path}: {actual!r} != {expected!r}")
        return
    if type(actual) is not type(expected):
        raise AssertionError(
            f"{path}: type {type(actual).__name__} != {type(expected).__name__}"
        )
    if isinstance(actual, dict):
        if actual.keys() != expected.keys():
            raise AssertionError(f"{path}: object keys differ")
        for key in actual:
            # SciPy versions can converge to the same checked fit in a
            # different number of outer effective-variance iterations.
            # Convergence and every scientific output remain compared below;
            # the iteration count is diagnostic metadata, not an oracle.
            if key == "outer_iterations":
                continue
            compare(actual[key], expected[key], f"{path}.{key}")
        return
    if isinstance(actual, list):
        if len(actual) != len(expected):
            raise AssertionError(f"{path}: list lengths differ")
        for index, (left, right) in enumerate(zip(actual, expected)):
            compare(left, right, f"{path}[{index}]")
        return
    if actual != expected:
        raise AssertionError(f"{path}: {actual!r} != {expected!r}")


with open(sys.argv[1]) as generated_file:
    generated = json.load(generated_file)
with open(sys.argv[2]) as saved_file:
    saved = json.load(saved_file)
compare(generated, saved)
PY
printf '%s
' 'legacy caster script output: scientific fields/text exact; floats within rtol=1e-6, atol=1e-8; solver iteration metadata ignored'
