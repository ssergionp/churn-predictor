def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_requires_valid_payload(client):
    response = client.post("/api/predict", json={})
    assert response.status_code == 422


def test_predict_returns_probability_when_model_exists(client, monkeypatch):
    from app.models.schemas import PredictionResponse
    from app.services import predictor

    monkeypatch.setattr(
        predictor,
        "predict_churn",
        lambda features: PredictionResponse(
            churn_probability=0.73, will_churn=True, top_factors=[]
        ),
    )

    payload = {
        "tenure_months": 3,
        "monthly_charges": 95.0,
        "total_charges": 285.0,
        "contract_type": "month-to-month",
        "has_internet_service": True,
        "has_tech_support": False,
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
