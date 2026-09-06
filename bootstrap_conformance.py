#!/usr/bin/env python3
"""Small exact ordinary-bootstrap reference for conformance testing.

Method boundary: Larry Wasserman, All of Statistics, chapter 8, and
"Bootstrapping and Subsampling: Part I" (Normal Deviate, 2013-01-19).
This is original code; it does not copy source prose.
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from typing import Any


MAX_EXACT_RESAMPLES = 100_000


class BootstrapInputError(ValueError):
    pass


def _finite_numbers(xs: Any, name: str) -> list[float]:
    if not isinstance(xs, list) or len(xs) < 2:
        raise BootstrapInputError(f"{name} must be an array with at least two numbers")
    out: list[float] = []
    for x in xs:
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            raise BootstrapInputError(f"{name} must contain only numbers")
        value = float(x)
        if not math.isfinite(value):
            raise BootstrapInputError(f"{name} must contain only finite numbers")
        out.append(value)
    return out


def _inverse_ecdf_quantile(sorted_values: list[float], probability: float) -> float:
    """inf{x: F_hat(x) >= probability}; no interpolation."""
    if not 0 <= probability <= 1:
        raise ValueError("probability must be between zero and one")
    index = max(0, math.ceil(probability * len(sorted_values)) - 1)
    return sorted_values[min(index, len(sorted_values) - 1)]


def bootstrap_mean(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise BootstrapInputError("input must be a JSON object")

    observed = _finite_numbers(record.get("observed"), "observed")

    if record.get("sampling") != "iid":
        raise BootstrapInputError(
            "sampling must be explicitly 'iid'; dependent, clustered, and time-series "
            "resampling are outside this conformance slice"
        )
    if record.get("resampling_unit") != "observation":
        raise BootstrapInputError(
            "resampling_unit must be explicitly 'observation' for this conformance slice"
        )
    if record.get("estimator", "mean") != "mean":
        raise BootstrapInputError("only estimator='mean' is implemented")
    if record.get("interval", "basic_bootstrap") != "basic_bootstrap":
        raise BootstrapInputError("only interval='basic_bootstrap' is implemented")
    if record.get("mode", "exact") != "exact":
        raise BootstrapInputError("only mode='exact' is implemented")
    if "weights" in record:
        raise BootstrapInputError("weighted observations are outside this conformance slice")

    alpha_raw = record.get("alpha", 0.05)
    if isinstance(alpha_raw, bool) or not isinstance(alpha_raw, (int, float)):
        raise BootstrapInputError("alpha must be a number between zero and one")
    alpha = float(alpha_raw)
    if not math.isfinite(alpha) or not 0 < alpha < 1:
        raise BootstrapInputError("alpha must be between zero and one")

    n = len(observed)
    resample_count = n ** n
    if resample_count > MAX_EXACT_RESAMPLES:
        raise BootstrapInputError(
            f"exact bootstrap would require {resample_count} resamples; "
            f"limit is {MAX_EXACT_RESAMPLES}; this reference refuses rather than "
            "silently switching to Monte Carlo"
        )

    estimate = sum(observed) / n
    replicates = [
        sum(sample) / n
        for sample in itertools.product(observed, repeat=n)
    ]
    bootstrap_distribution_mean = sum(replicates) / resample_count
    standard_error = math.sqrt(
        sum((value - bootstrap_distribution_mean) ** 2 for value in replicates)
        / resample_count
    )

    ordered = sorted(replicates)
    lower_quantile = _inverse_ecdf_quantile(ordered, alpha / 2)
    upper_quantile = _inverse_ecdf_quantile(ordered, 1 - alpha / 2)
    interval = [
        2 * estimate - upper_quantile,
        2 * estimate - lower_quantile,
    ]

    return {
        "test": "bootstrap_mean",
        "target": "population_mean",
        "estimate": estimate,
        "bootstrap_distribution_mean": bootstrap_distribution_mean,
        "standard_error": standard_error,
        "alpha": alpha,
        "confidence_level": 1 - alpha,
        "interval_method": "basic_bootstrap",
        "bootstrap_quantiles": [lower_quantile, upper_quantile],
        "interval": interval,
        "quantile_rule": "inverse_empirical_cdf_no_interpolation",
        "resampling": {
            "source": "empirical_distribution",
            "sample_size": n,
            "replacement": True,
            "mode": "exact",
            "resamples": resample_count,
        },
        "assumptions": [
            "iid_observations",
            "observation_is_resampling_unit",
            "scalar_arithmetic_mean",
        ],
        "monte_carlo_error": False,
        "guaranteed_valid_coverage": False,
    }


def main() -> int:
    failed = False
    for line_number, line in enumerate(sys.stdin, 1):
        if not line.strip():
            continue
        try:
            result = bootstrap_mean(json.loads(line))
            print(json.dumps({"ok": True, "result": result}, separators=(",", ":")))
        except (BootstrapInputError, json.JSONDecodeError, TypeError, ValueError) as exc:
            failed = True
            print(
                json.dumps(
                    {"ok": False, "line": line_number, "error": str(exc)},
                    separators=(",", ":"),
                )
            )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
