from pathlib import Path

import joblib
import pandas as pd

from app.models.schemas import CustomerFeatures, PredictionResponse

MODEL_PATH = Path(__file__).resolve().parents[2] / "data" / "model.pkl"

_model = None


def _get_model():
    """Lazily load the trained model from disk."""
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Run `python train_model.py` first."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_churn(features: CustomerFeatures) -> PredictionResponse:
    model = _get_model()

    df = pd.DataFrame([features.model_dump()])
    probability = float(model.predict_proba(df)[0][1])

    return PredictionResponse(
        churn_probability=round(probability, 4),
        will_churn=probability >= 0.5,
        top_factors=[],  # TODO: add SHAP-based explainability
    )
