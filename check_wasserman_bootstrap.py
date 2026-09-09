#!/usr/bin/env python3
"""Check structured language-model answers against Wasserman bootstrap oracles."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable


CASES_PATH = Path(__file__).with_name("wasserman_bootstrap_cases.jsonl")


class OracleError(ValueError):
    pass


def load_jsonl(lines: Iterable[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise OracleError(f"line {line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(record, dict):
            raise OracleError(f"line {line_number}: expected a JSON object")
        records.append(record)
    return records


def load_cases(path: Path = CASES_PATH) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        cases = load_jsonl(handle)
    ids = [case.get("id") for case in cases]
    if any(not isinstance(case_id, str) or not case_id for case_id in ids):
        raise OracleError("every case must have a nonempty string id")
    if len(set(ids)) != len(ids):
        raise OracleError("case ids must be unique")
    return cases


def _compare(expected: Any, actual: Any, tolerance: float, path: str) -> list[str]:
    if isinstance(expected, bool):
        return [] if actual is expected else [f"{path}: expected {expected!r}, got {actual!r}"]

    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        if isinstance(actual, bool) or not isinstance(actual, (int, float)):
            return [f"{path}: expected numeric {expected!r}, got {actual!r}"]
        if not math.isfinite(float(actual)):
            return [f"{path}: expected finite {expected!r}, got {actual!r}"]
        if abs(float(actual) - float(expected)) > tolerance:
            return [f"{path}: expected {expected!r} ± {tolerance:g}, got {actual!r}"]
        return []

    if isinstance(expected, list):
        if not isinstance(actual, list):
            return [f"{path}: expected list, got {type(actual).__name__}"]
        if len(actual) != len(expected):
            return [f"{path}: expected {len(expected)} items, got {len(actual)}"]
        errors: list[str] = []
        for index, (want, got) in enumerate(zip(expected, actual)):
            errors.extend(_compare(want, got, tolerance, f"{path}[{index}]"))
        return errors

    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [f"{path}: expected object, got {type(actual).__name__}"]
        errors: list[str] = []
        for key, want in expected.items():
            child = f"{path}.{key}" if path else key
            if key not in actual:
                errors.append(f"{child}: missing")
                continue
            errors.extend(_compare(want, actual[key], tolerance, child))
        return errors

    return [] if actual == expected else [f"{path}: expected {expected!r}, got {actual!r}"]


def check_case(case: dict[str, Any], answer: dict[str, Any]) -> list[str]:
    expected = case.get("expect")
    if not isinstance(expected, dict):
        raise OracleError(f"{case.get('id', '<unknown>')}: expect must be an object")
    if not isinstance(answer, dict):
        return ["answer: expected object"]

    tolerances = case.get("tolerance", {})
    if not isinstance(tolerances, dict):
        raise OracleError(f"{case['id']}: tolerance must be an object")

    errors: list[str] = []
    for key, want in expected.items():
        if key not in answer:
            errors.append(f"{key}: missing")
            continue
        tolerance = tolerances.get(key, 0.0)
        if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or tolerance < 0:
            raise OracleError(f"{case['id']}: invalid tolerance for {key}")
        errors.extend(_compare(want, answer[key], float(tolerance), key))
    return errors


def check_answers(
    cases: list[dict[str, Any]], submissions: list[dict[str, Any]]
) -> tuple[list[str], list[str]]:
    by_id: dict[str, dict[str, Any]] = {}
    failures: list[str] = []

    known_ids = {case["id"] for case in cases}
    for record in submissions:
        case_id = record.get("id")
        if not isinstance(case_id, str):
            failures.append("submission missing string id")
            continue
        if case_id not in known_ids:
            failures.append(f"{case_id}: unknown case id")
            continue
        if case_id in by_id:
            failures.append(f"{case_id}: duplicate submission")
            continue
        answer = record.get("answer")
        if not isinstance(answer, dict):
            failures.append(f"{case_id}: answer must be an object")
            continue
        by_id[case_id] = answer

    passes: list[str] = []
    for case in cases:
        case_id = case["id"]
        if case_id not in by_id:
            failures.append(f"{case_id}: missing submission")
            continue
        errors = check_case(case, by_id[case_id])
        if errors:
            failures.extend(f"{case_id}: {error}" for error in errors)
        else:
            passes.append(case_id)
    return passes, failures


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) > 1:
        print("usage: check_wasserman_bootstrap.py [answers.jsonl]", file=sys.stderr)
        return 2

    cases = load_cases()
    if argv:
        with Path(argv[0]).open(encoding="utf-8") as handle:
            submissions = load_jsonl(handle)
    else:
        submissions = load_jsonl(sys.stdin)

    passes, failures = check_answers(cases, submissions)
    for case_id in passes:
        print(f"PASS {case_id}")
    for failure in failures:
        print(f"FAIL {failure}")
    print(f"RESULT {len(passes)}/{len(cases)}")
    return 0 if not failures and len(passes) == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
