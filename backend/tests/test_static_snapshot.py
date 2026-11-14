"""The static demo answers from a committed snapshot of the catalogue.

Changing the seed, a response schema or COMPARISON_FIELDS without regenerating it would
leave the demo showing figures the API no longer returns. Regenerate with `make snapshot`.
"""
import json

from app.export_static import CASES_FILE, SNAPSHOT_FILE, build


def test_committed_snapshot_matches_the_backend():
    snapshot, cases = build()
    committed = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
    assert committed == snapshot, "catalog-snapshot.json is stale, run: make snapshot"
    committed_cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    assert committed_cases == cases, "compare-cases.json is stale, run: make snapshot"


def test_snapshot_covers_the_whole_catalogue():
    snapshot, cases = build()
    assert len(snapshot["items"]) == 90
    assert snapshot["comparison_fields"]["cop"] == "max"
    assert all(case["expected"]["models"] == case["models"] for case in cases)
