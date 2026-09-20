from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(name: str):
    with (ROOT / name).open(newline="") as f:
        return list(csv.DictReader(f))


def test_source_manifest_hashes_and_ids_are_unique():
    rows = read_csv("data/source_manifest.csv")
    assert len(rows) == 40
    assert len({r["source_id"] for r in rows}) == len(rows)
    for row in rows:
        p = ROOT / "sources" / row["filename"]
        if p.is_file():
            assert hashlib.sha256(p.read_bytes()).hexdigest() == row["sha256"]
            assert p.stat().st_size == int(row["size_bytes"])
        else:
            assert len(row["sha256"]) == 64
            int(row["sha256"], 16)
            assert int(row["size_bytes"]) > 0


def test_evidence_ledger_references_known_sources_and_has_unique_ids():
    evidence = []
    for name in ("data/evidence_ledger_001-030.csv","data/evidence_ledger_031-060.csv","data/evidence_ledger_061-087.csv"):
        evidence.extend(read_csv(name))
    manifest = read_csv("data/source_manifest.csv")
    known = {r["source_id"] for r in manifest}
    assert len(evidence) == 87
    assert len({r["evidence_id"] for r in evidence}) == len(evidence)
    assert {r["category"] for r in evidence} <= {"observation","convention","derived_result","uncertainty_statement","interpretation_model"}
    for row in evidence:
        if row["source_id"]:
            assert row["source_id"] in known


def test_discrepancy_ledger_keeps_unresolved_conflicts():
    rows = read_csv("data/discrepancy_ledger.csv")
    ids = {r["id"] for r in rows}
    assert len(ids) == len(rows)
    for required in {"D-001","D-002","D-006","D-014","D-015","D-016"}:
        assert required in ids
    by_id = {r["id"]: r for r in rows}
    assert "UNRESOLVED" in by_id["D-001"]["current_disposition"]
    assert "UNRESOLVED" in by_id["D-014"]["current_disposition"]
    assert "UNRECOVERED" in by_id["D-015"]["current_disposition"]


def test_caster_failure_ledger_preserves_embarrassing_results_and_error_status():
    rows = read_csv("data/caster_failure_ledger.csv")
    assert len(rows) == 12
    by_id = {row["id"]: row for row in rows}
    assert len(by_id) == len(rows)
    assert "12.0292" in by_id["H-002"]["estimate"]
    assert "8.0643" in by_id["H-005"]["estimate"]
    assert "5.5687987431" in by_id["H-007"]["estimate"]
    assert "4.6 +/-1.0" in by_id["H-012"]["estimate"]
    assert "arithmetic" in by_id["H-002"]["what_was_correct"]
    assert "not caused by a bad Jacobian" in by_id["H-005"]["corrected_interpretation"]
    assert "construction not recovered" in by_id["H-008"]["reported_uncertainty"]
    assert "cannot be reconstructed" in by_id["H-012"]["what_was_wrong"]


def test_G5_reset_sweep_is_one_state_and_one_ordered_sweep():
    rows = read_csv("../dakota-caster-scalar-slice/g5_reset_sweep.csv")
    assert len(rows) == 14
    assert {row["generation"] for row in rows} == {"G5"}
    assert {row["adjustment_state"] for row in rows} == {
        "passenger_front_returned_only_driver_rear_displaced"
    }
    assert {row["sweep_id"] for row in rows} == {"sep16_reset"}
    assert {row["approach_direction"] for row in rows} == {
        "max_left_to_max_right"
    }
    assert {row["side"] for row in rows} == {"driver", "passenger"}


def test_cam_rotation_viewpoint_is_rear_looking_forward():
    conventions = json.loads((ROOT / "data/conventions.json").read_text())
    cam = conventions["cam_rotation"]
    assert cam["viewpoint"] == "looking from the rear of the truck toward the front"
    assert "must not be silently converted" in cam["warning"]


def test_benchmark_refuses_unrecovered_physical_objects():
    benchmark = json.loads((ROOT / "data/benchmark.json").read_text())
    assert benchmark["acceptance_status"].startswith("PARTIAL")
    assert benchmark["jacobian"]["full_physical_status"] != "recovered"
    assert benchmark["curvature"]["truck_specific_curvature"] == "not recovered"
    assert benchmark["curvature"]["curvature_jacobian"] == "definition not recovered; implementation refuses to invent one"
    assert benchmark["epsilon"]["mixed_products"].startswith("unresolved in recovered design record")
