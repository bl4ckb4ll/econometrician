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
cmp /tmp/dakota_caster_recheck_results.json "$LEGACY/dakota_caster_recheck_results.json"
printf '%s
' 'legacy caster script output: byte-identical'
