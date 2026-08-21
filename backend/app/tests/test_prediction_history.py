from app.db import SessionLocal
from app.models.db_models import PredictionRecord
from app.models.schemas import PredictionResponse

SAMPLE_PAYLOAD = {
    "tenure_months": 3,
    "monthly_charges": 95.0,
    "total_charges": 285.0,
    "contract_type": "month-to-month",
    "has_internet_service": True,
    "has_tech_support": False,
}


def _mock_predict_churn(monkeypatch, probability: float, will_churn: bool):
    from app.services import predictor

    monkeypatch.setattr(
        predictor,
        "predict_churn",
        lambda features: PredictionResponse(
            churn_probability=probability, will_churn=will_churn, top_factors=["tenure_months"]
        ),
    )


def test_predict_saves_a_prediction_record(client, monkeypatch):
    _mock_predict_churn(monkeypatch, probability=0.73, will_churn=True)

    response = client.post("/api/predict", json=SAMPLE_PAYLOAD)
    assert response.status_code == 200

    db = SessionLocal()
    try:
        records = db.query(PredictionRecord).all()
        assert len(records) == 1
        record = records[0]
        assert record.tenure_months == 3
        assert record.contract_type == "month-to-month"
        assert record.churn_probability == 0.73
        assert record.will_churn is True
        assert record.top_factors == ["tenure_months"]
        assert record.created_at is not None
    finally:
        db.close()


def test_list_predictions_returns_most_recent_first(client, monkeypatch):
    _mock_predict_churn(monkeypatch, probability=0.5, will_churn=False)

    for tenure in (1, 2, 3):
        response = client.post(
            "/api/predict", json={**SAMPLE_PAYLOAD, "tenure_months": tenure}
        )
        assert response.status_code == 200

    response = client.get("/api/predictions")
    assert response.status_code == 200
    assert [item["tenure_months"] for item in response.json()] == [3, 2, 1]


def test_list_predictions_caps_at_twenty(client):
    db = SessionLocal()
    try:
        for i in range(25):
            db.add(
                PredictionRecord(
                    tenure_months=i,
                    monthly_charges=50.0,
                    total_charges=500.0,
                    contract_type="month-to-month",
                    has_internet_service=True,
                    has_tech_support=False,
                    churn_probability=0.5,
                    will_churn=False,
                    top_factors=[],
                )
            )
        db.commit()
    finally:
        db.close()

    response = client.get("/api/predictions")
    assert response.status_code == 200
    assert len(response.json()) == 20
