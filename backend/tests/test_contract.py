"""The committed openapi.yaml is the contract the frontend is written against.

If someone changes a route without regenerating the spec, this fails and the PR
stops. Regenerate with `make spec`.
"""
from pathlib import Path

import yaml

from app.main import app

SPEC = Path(__file__).resolve().parents[2] / "openapi.yaml"


def test_committed_spec_matches_the_running_app():
    committed = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    assert committed == app.openapi(), "openapi.yaml is stale, run: make spec"


def test_spec_documents_every_route_the_frontend_calls():
    committed = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    for path in ["/equipment", "/equipment/compare", "/equipment/{model}", "/facets"]:
        assert path in committed["paths"]
