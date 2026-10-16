def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

def test_prediction_for_country(client):
    response = client.get("/predict?target_date=2026-10-20&country=India")
    assert response.status_code == 200
    body = response.get_json()
    assert body["country"] == "India"
    assert body["predicted_revenue"] >= 0

def test_prediction_all_countries(client):
    response = client.get("/predict?target_date=2026-10-20")
    assert response.status_code == 200
    body = response.get_json()
    assert len(body["predictions"]) == 2
    assert body["combined_predicted_revenue"] > 0

def test_missing_date_is_rejected(client):
    response = client.get("/predict")
    assert response.status_code == 400

def test_invalid_date_is_rejected(client):
    response = client.get("/predict?target_date=20-10-2026&country=India")
    assert response.status_code == 400

def test_unknown_country_is_rejected(client):
    response = client.get("/predict?target_date=2026-10-20&country=Atlantis")
    assert response.status_code == 400

def test_actual_endpoint_validates_payload(client):
    response = client.post("/monitor/actual", json={"country": "India"})
    assert response.status_code == 400

def test_actual_endpoint_accepts_valid_payload(client):
    response = client.post("/monitor/actual", json={
        "target_date": "2026-10-20", "country": "India", "actual_revenue": 1234
    })
    assert response.status_code == 201
