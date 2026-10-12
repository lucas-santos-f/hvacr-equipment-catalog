"""The write route is the only way into the database from outside, so it gets its own
test file. CORS does not protect it: a browser is not the threat, curl is.
"""

import pytest

from app.config import settings

PAYLOAD = dict(model="AU-TH100", manufacturer="Valbrand", category="chiller",
               refrigerant="R32", capacity_kw=10.0, power_input_kw=2.5,
               voltage="400V/3ph/50Hz", sound_pressure_db=50.0,
               weight_kg=100.0, price_eur=9000.0)


def test_write_without_a_key_is_rejected(client):
    r = client.post("/equipment", json=PAYLOAD)
    assert r.status_code == 401
    assert "X-API-Key" in r.json()["detail"]


def test_write_with_a_wrong_key_is_rejected(client):
    r = client.post("/equipment", json=PAYLOAD, headers={"X-API-Key": "nope"})
    assert r.status_code == 401


def test_a_rejected_write_does_not_reach_the_database(client):
    client.post("/equipment", json=PAYLOAD)
    assert client.get(f"/equipment/{PAYLOAD['model']}").status_code == 404


def test_the_key_is_checked_before_the_body(client):
    """An unauthenticated caller should not be able to use 422 responses to map out
    which fields the schema wants."""
    assert client.post("/equipment", json={}).status_code == 401


def test_writes_are_refused_when_no_key_is_configured(client, monkeypatch):
    """Fail closed. A deploy that forgets API_KEY must not become an open endpoint."""
    monkeypatch.setattr(settings, "api_key", "")
    r = client.post("/equipment", json=PAYLOAD, headers={"X-API-Key": "test-key"})
    assert r.status_code == 503


@pytest.mark.parametrize("method", ["put", "patch", "delete"])
def test_there_is_no_other_way_to_mutate_a_unit(client, method):
    """Nothing else writes. If a route is added later this fails and forces a decision
    about its gate."""
    r = getattr(client, method)("/equipment/TX-CH900")
    assert r.status_code == 405


def test_reads_stay_open(client):
    assert client.get("/equipment?limit=1").status_code == 200
