def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_search_returns_a_page(client):
    r = client.get("/equipment")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 3
    assert body["offset"] == 0
    assert [i["model"] for i in body["items"]] == ["FG-PU902", "NV-CH901", "TX-CH900"]


def test_filter_by_category(client):
    body = client.get("/equipment", params={"category": "chiller"}).json()
    assert body["total"] == 2
    assert {i["category"] for i in body["items"]} == {"chiller"}


def test_filter_by_capacity_window(client):
    body = client.get("/equipment", params={"min_capacity": 190}).json()
    assert [i["model"] for i in body["items"]] == ["TX-CH900"]


def test_inverted_capacity_window_is_rejected(client):
    r = client.get("/equipment", params={"min_capacity": 300, "max_capacity": 10})
    assert r.status_code == 422


def test_unknown_category_is_rejected(client):
    assert client.get("/equipment", params={"category": "boiler"}).status_code == 422


def test_pagination(client):
    first = client.get("/equipment", params={"limit": 1}).json()
    second = client.get("/equipment", params={"limit": 1, "offset": 1}).json()
    assert first["total"] == second["total"] == 3
    assert first["items"][0]["model"] != second["items"][0]["model"]


def test_detail_exposes_computed_cop(client):
    body = client.get("/equipment/TX-CH900").json()
    assert body["cop"] == 4.0


def test_detail_of_unknown_model(client):
    assert client.get("/equipment/NOPE-1").status_code == 404


def test_compare_two_models(client):
    body = client.get("/equipment/compare", params={"models": "TX-CH900,NV-CH901"}).json()
    assert body["models"] == ["TX-CH900", "NV-CH901"]
    rows = {r["field"]: r for r in body["rows"]}
    assert rows["capacity_kw"]["best"] == "TX-CH900"
    assert rows["sound_pressure_db"]["best"] == "NV-CH901"


def test_compare_needs_at_least_two(client):
    assert client.get("/equipment/compare", params={"models": "TX-CH900"}).status_code == 422


def test_compare_with_unknown_model(client):
    r = client.get("/equipment/compare", params={"models": "TX-CH900,NOPE-1"})
    assert r.status_code == 404


def test_facets_feed_the_filter_dropdowns(client):
    body = client.get("/facets").json()
    assert body["categories"] == ["chiller", "circulator_pump"]
    assert "R32" in body["refrigerants"]
    assert body["capacity_range"] == {"min": 12.0, "max": 200.0}


def test_create_then_read_back(client):
    payload = dict(model="CM-FC500", manufacturer="Cryomar", category="fan_coil",
                   refrigerant="R32", capacity_kw=6.0, power_input_kw=1.5,
                   voltage="230V/1ph/50Hz", sound_pressure_db=34.0,
                   weight_kg=29.0, price_eur=1250.0)
    assert client.post("/equipment", json=payload).status_code == 201
    assert client.get("/equipment/CM-FC500").json()["cop"] == 4.0


def test_duplicate_model_is_rejected(client):
    payload = dict(model="TX-CH900", manufacturer="Thermexa", category="chiller",
                   refrigerant="R32", capacity_kw=1.0, power_input_kw=1.0,
                   voltage="400V/3ph/50Hz", sound_pressure_db=1.0,
                   weight_kg=1.0, price_eur=1.0)
    assert client.post("/equipment", json=payload).status_code == 409


def test_negative_capacity_is_rejected(client):
    payload = dict(model="XX-1", manufacturer="Norvent", category="chiller",
                   refrigerant="R32", capacity_kw=-5.0, power_input_kw=1.0,
                   voltage="400V/3ph/50Hz", sound_pressure_db=1.0,
                   weight_kg=1.0, price_eur=1.0)
    assert client.post("/equipment", json=payload).status_code == 422
