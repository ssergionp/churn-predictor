import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.models.schemas import CustomerFeatures
from app.services import predictor

CATEGORICAL_FEATURES = ["contract_type"]
NUMERIC_FEATURES = ["tenure_months", "monthly_charges", "total_charges"]
BOOLEAN_FEATURES = ["has_internet_service", "has_tech_support"]


@pytest.fixture
def trained_pipeline():
    """Builds and fits a small pipeline shaped like train_model.py's, so
    tests exercise the same ColumnTransformer + RandomForestClassifier
    feature-naming path used in production.
    """
    rng = np.random.default_rng(0)
    n = 50
    df = pd.DataFrame(
        {
            "tenure_months": rng.integers(0, 72, n),
            "monthly_charges": rng.uniform(20, 120, n),
            "total_charges": rng.uniform(20, 8000, n),
            "contract_type": rng.choice(["month-to-month", "one_year", "two_year"], n),
            "has_internet_service": rng.choice([True, False], n),
            "has_tech_support": rng.choice([True, False], n),
        }
    )
    y = rng.choice([True, False], n)

    preprocessor = ColumnTransformer(
        transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES)],
        remainder="passthrough",
    )
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=10, random_state=0)),
        ]
    )
    pipeline.fit(df[NUMERIC_FEATURES + CATEGORICAL_FEATURES + BOOLEAN_FEATURES], y)
    return pipeline


@pytest.fixture(autouse=True)
def reset_explainer_cache():
    predictor._explainer = None
    yield
    predictor._explainer = None


def test_build_output_feature_sources_maps_one_hot_dummies_to_original_column(
    trained_pipeline,
):
    preprocessor = trained_pipeline.named_steps["preprocessor"]
    sources = predictor._build_output_feature_sources(preprocessor)

    # 3 one-hot dummies for contract_type + 5 passthrough columns.
    assert sources.count("contract_type") == 3
    for field in NUMERIC_FEATURES + BOOLEAN_FEATURES:
        assert sources.count(field) == 1
    assert len(sources) == 8


def test_explain_prediction_returns_top_three_ranked_by_abs_shap(trained_pipeline):
    df = pd.DataFrame(
        [
            {
                "tenure_months": 12,
                "monthly_charges": 80.0,
                "total_charges": 960.0,
                "contract_type": "month-to-month",
                "has_internet_service": True,
                "has_tech_support": False,
            }
        ]
    )

    ranked = predictor._explain_prediction(trained_pipeline, df)

    assert len(ranked) == 3
    names = [name for name, _ in ranked]
    assert len(set(names)) == len(names)  # no duplicate/unaggregated one-hot dummies

    magnitudes = [abs(value) for _, value in ranked]
    assert magnitudes == sorted(magnitudes, reverse=True)


def test_explainer_is_cached(trained_pipeline):
    first = predictor._get_explainer(trained_pipeline)
    second = predictor._get_explainer(trained_pipeline)
    assert first is second


@pytest.mark.parametrize(
    "shap_value,expected_direction",
    [(0.12, "increases risk"), (-0.08, "decreases risk")],
)
def test_format_factor_direction(shap_value, expected_direction):
    formatted = predictor._format_factor("tenure_months", shap_value)
    assert formatted == f"tenure_months ({expected_direction})"


def test_predict_churn_includes_shap_ranked_top_factors(monkeypatch, trained_pipeline):
    monkeypatch.setattr(predictor, "_get_model", lambda: trained_pipeline)

    features = CustomerFeatures(
        tenure_months=12,
        monthly_charges=80.0,
        total_charges=960.0,
        contract_type="month-to-month",
        has_internet_service=True,
        has_tech_support=False,
    )
    response = predictor.predict_churn(features)

    assert len(response.top_factors) == 3
    for factor in response.top_factors:
        assert factor.endswith("(increases risk)") or factor.endswith("(decreases risk)")
