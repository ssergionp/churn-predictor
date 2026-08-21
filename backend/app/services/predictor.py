from pathlib import Path

import joblib
import pandas as pd
import shap
from sklearn.compose import ColumnTransformer

from app.models.schemas import CustomerFeatures, PredictionResponse

MODEL_PATH = Path(__file__).resolve().parents[2] / "data" / "model.pkl"
TOP_FACTORS_COUNT = 3
CHURN_CLASS_INDEX = 1

_model = None
_explainer = None


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


def _get_explainer(model) -> shap.TreeExplainer:
    """Lazily builds a SHAP TreeExplainer for the pipeline's classifier.

    Building the explainer walks the whole forest, so it's done once and
    cached - evaluating it per prediction afterwards is cheap.
    """
    global _explainer
    if _explainer is None:
        _explainer = shap.TreeExplainer(model.named_steps["classifier"])
    return _explainer


def _build_output_feature_sources(preprocessor: ColumnTransformer) -> list[str]:
    """Maps each column of the preprocessor's transformed output back to the
    original CustomerFeatures field it came from, in output order.

    A one-hot-encoded column like "contract_type_month-to-month" collapses
    back to "contract_type", so SHAP contributions for the encoder's dummy
    columns can be summed into a single, customer-facing factor name.
    """
    input_columns = list(preprocessor.feature_names_in_)
    sources: list[str] = []
    for _, transformer, columns in preprocessor.transformers_:
        if transformer == "drop" or len(columns) == 0:
            continue
        resolved = [c if isinstance(c, str) else input_columns[c] for c in columns]
        if hasattr(transformer, "categories_"):
            # OneHotEncoder: one output column per (input column, category) pair.
            for column, categories in zip(resolved, transformer.categories_):
                sources.extend([column] * len(categories))
        else:
            sources.extend(resolved)
    return sources


def _explain_prediction(model, df: pd.DataFrame) -> list[tuple[str, float]]:
    """Computes this customer's SHAP contribution per input field and
    returns the top `TOP_FACTORS_COUNT`, sorted by absolute impact on the
    predicted churn probability (largest first).
    """
    preprocessor = model.named_steps["preprocessor"]
    transformed = preprocessor.transform(df)
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()

    explainer = _get_explainer(model)
    explanation = explainer(transformed)

    row_values = explanation.values[0]
    if row_values.ndim == 2:
        # (n_features, n_classes) for a binary/multiclass classifier.
        row_values = row_values[:, CHURN_CLASS_INDEX]

    sources = _build_output_feature_sources(preprocessor)

    contributions: dict[str, float] = {}
    for source, value in zip(sources, row_values):
        contributions[source] = contributions.get(source, 0.0) + float(value)

    ranked = sorted(contributions.items(), key=lambda pair: abs(pair[1]), reverse=True)
    return ranked[:TOP_FACTORS_COUNT]


def _format_factor(name: str, shap_value: float) -> str:
    direction = "increases risk" if shap_value > 0 else "decreases risk"
    return f"{name} ({direction})"


def predict_churn(features: CustomerFeatures) -> PredictionResponse:
    model = _get_model()

    df = pd.DataFrame([features.model_dump()])
    probability = float(model.predict_proba(df)[0][1])

    top_factors = [
        _format_factor(name, value) for name, value in _explain_prediction(model, df)
    ]

    return PredictionResponse(
        churn_probability=round(probability, 4),
        will_churn=probability >= 0.5,
        top_factors=top_factors,
    )
