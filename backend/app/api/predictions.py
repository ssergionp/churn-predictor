from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.db_models import PredictionRecord
from app.models.schemas import CustomerFeatures, PredictionHistoryItem, PredictionResponse
from app.services import predictor

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict(features: CustomerFeatures, db: Session = Depends(get_db)):
    try:
        result = predictor.predict_churn(features)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    record = PredictionRecord(
        **features.model_dump(),
        churn_probability=result.churn_probability,
        will_churn=result.will_churn,
        top_factors=result.top_factors,
    )
    db.add(record)
    db.commit()

    return result


@router.get("/predictions", response_model=list[PredictionHistoryItem])
def list_predictions(db: Session = Depends(get_db)):
    return (
        db.query(PredictionRecord)
        .order_by(PredictionRecord.created_at.desc(), PredictionRecord.id.desc())
        .limit(20)
        .all()
    )
