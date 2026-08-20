from pathlib import Path

import joblib
import pandas as pd

from app.models.schemas import CustomerFeatures, PredictionResponse

MODEL_PATH = Path(__file__).resolve().parents[2] / "data" / "model.pkl"
TOP_FACTORS_COUNT = 3

_model = None
_top_factors: list[str] | None = None


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


def _clean_feature_name(name: str) -> str:
    """Strips the ColumnTransformer's `cat__`/`remainder__` prefixes."""
    return name.split("__", 1)[-1]


def _get_top_factors(model) -> list[str]:
    """Ranks features by the RandomForestClassifier's global
    `feature_importances_` and returns the top `TOP_FACTORS_COUNT` names.

    This is a global, model-wide ranking (not per-prediction), so it is the
    same for every request. TODO: replace with SHAP-based per-prediction
    explainability.
    """
    global _top_factors
    if _top_factors is None:
        preprocessor = model.named_steps["preprocessor"]
        classifier = model.named_steps["classifier"]

        feature_names = preprocessor.get_feature_names_out()
        importances = classifier.feature_importances_

        ranked = sorted(zip(feature_names, importances), key=lambda pair: pair[1], reverse=True)
        _top_factors = [_clean_feature_name(name) for name, _ in ranked[:TOP_FACTORS_COUNT]]
    return _top_factors


def predict_churn(features: CustomerFeatures) -> PredictionResponse:
    model = _get_model()

    df = pd.DataFrame([features.model_dump()])
    probability = float(model.predict_proba(df)[0][1])

    return PredictionResponse(
        churn_probability=round(probability, 4),
        will_churn=probability >= 0.5,
        top_factors=_get_top_factors(model),
    )
