#!/usr/bin/env python3
"""Checked Pearson chi-square calculations with a JSON-lines interface."""

from __future__ import annotations

import json
import math
import sys
from typing import Any


class InputError(ValueError):
    pass


def _numbers(xs: Any, name: str) -> list[float]:
    if not isinstance(xs, list) or not xs:
        raise InputError(f"{name} must be a nonempty array")
    out = []
    for x in xs:
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            raise InputError(f"{name} must contain only numbers")
        x = float(x)
        if not math.isfinite(x) or x < 0:
            raise InputError(f"{name} must contain finite nonnegative numbers")
        out.append(x)
    return out


def _gamma_q(a: float, x: float) -> float:
    """Regularized upper incomplete gamma Q(a,x), Numerical Recipes method."""
    if a <= 0 or x < 0:
        raise ValueError("gamma arguments out of range")
    if x == 0:
        return 1.0
    eps, tiny, limit = 3e-14, 1e-300, 10000
    gln = math.lgamma(a)
    if x < a + 1:
        term = total = 1.0 / a
        ap = a
        for _ in range(limit):
            ap += 1
            term *= x / ap
            total += term
            if abs(term) < abs(total) * eps:
                p = total * math.exp(-x + a * math.log(x) - gln)
                return min(1.0, max(0.0, 1.0 - p))
        raise ArithmeticError("gamma series did not converge")
    b = x + 1 - a
    c = 1 / tiny
    d = 1 / b
    h = d
    for i in range(1, limit + 1):
        an = -i * (i - a)
        b += 2
        d = max(abs(an * d + b), tiny) * (1 if an * d + b >= 0 else -1)
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < eps:
            q = math.exp(-x + a * math.log(x) - gln) * h
            return min(1.0, max(0.0, q))
    raise ArithmeticError("gamma continued fraction did not converge")


def _finish(observed: Any, expected: Any, contributions: Any,
            statistic: float, df: int, alpha: float) -> dict[str, Any]:
    if not 0 < alpha < 1:
        raise InputError("alpha must be between zero and one")
    flat_expected = ([x for row in expected for x in row]
                     if expected and isinstance(expected[0], list) else expected)
    p_value = _gamma_q(df / 2, statistic / 2)
    warnings = []
    small = sum(x < 5 for x in flat_expected)
    if small:
        warnings.append(
            f"{small} expected count(s) are below 5; the asymptotic chi-square "
            "approximation may be unreliable"
        )
    return {
        "observed": observed,
        "expected": expected,
        "contributions": contributions,
        "statistic": statistic,
        "degrees_of_freedom": df,
        "p_value": p_value,
        "alpha": alpha,
        "decision": "reject" if p_value < alpha else "do_not_reject",
        "warnings": warnings,
    }


def goodness_of_fit(record: dict[str, Any]) -> dict[str, Any]:
    observed = _numbers(record.get("observed"), "observed")
    probabilities = _numbers(record.get("probabilities"), "probabilities")
    if len(observed) != len(probabilities) or len(observed) < 2:
        raise InputError("observed and probabilities must have the same length >= 2")
    if any(p == 0 for p in probabilities):
        raise InputError("probabilities must be strictly positive")
    if not math.isclose(sum(probabilities), 1.0, abs_tol=1e-9, rel_tol=0):
        raise InputError("probabilities must sum to one")
    n = sum(observed)
    if n == 0:
        raise InputError("the total observed count must be positive")
    expected = [n * p for p in probabilities]
    contributions = [(o - e) ** 2 / e for o, e in zip(observed, expected)]
    result = _finish(observed, expected, contributions, sum(contributions),
                     len(observed) - 1, float(record.get("alpha", 0.05)))
    result["test"] = "goodness_of_fit"
    result["null"] = "category probabilities equal the supplied probabilities"
    return result


def independence(record: dict[str, Any]) -> dict[str, Any]:
    raw = record.get("observed")
    if not isinstance(raw, list) or len(raw) < 2:
        raise InputError("observed must contain at least two rows")
    observed = [_numbers(row, f"observed row {i}") for i, row in enumerate(raw)]
    cols = len(observed[0])
    if cols < 2 or any(len(row) != cols for row in observed):
        raise InputError("observed must be a rectangular table with at least two columns")
    row_totals = [sum(row) for row in observed]
    col_totals = [sum(observed[i][j] for i in range(len(observed))) for j in range(cols)]
    if any(x == 0 for x in row_totals + col_totals):
        raise InputError("each row and column must have a positive total")
    n = sum(row_totals)
    expected = [[r * c / n for c in col_totals] for r in row_totals]
    contributions = [[(observed[i][j] - expected[i][j]) ** 2 / expected[i][j]
                      for j in range(cols)] for i in range(len(observed))]
    statistic = sum(sum(row) for row in contributions)
    result = _finish(observed, expected, contributions, statistic,
                     (len(observed) - 1) * (cols - 1),
                     float(record.get("alpha", 0.05)))
    result["test"] = "independence"
    result["null"] = "the row and column classifications are independent"
    return result


def calculate(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise InputError("input must be a JSON object")
    kind = record.get("test")
    if kind == "goodness_of_fit":
        return goodness_of_fit(record)
    if kind == "independence":
        return independence(record)
    raise InputError("test must be goodness_of_fit or independence")


def main() -> int:
    failed = False
    for line_number, line in enumerate(sys.stdin, 1):
        if not line.strip():
            continue
        try:
            print(json.dumps({"ok": True, "result": calculate(json.loads(line))},
                             separators=(",", ":")))
        except (InputError, json.JSONDecodeError, TypeError, ValueError) as exc:
            failed = True
            print(json.dumps({"ok": False, "line": line_number, "error": str(exc)},
                             separators=(",", ":")))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
