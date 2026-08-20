from fastapi import APIRouter, HTTPException

from app.models.schemas import CustomerFeatures, PredictionResponse
from app.services.predictor import predict_churn

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict(features: CustomerFeatures):
    try:
        return predict_churn(features)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
