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
def reset_top_factors_cache():
    predictor._top_factors = None
    yield
    predictor._top_factors = None


def test_get_top_factors_returns_three_clean_feature_names(trained_pipeline):
    top_factors = predictor._get_top_factors(trained_pipeline)

    assert len(top_factors) == 3
    for name in top_factors:
        assert not name.startswith("cat__")
        assert not name.startswith("remainder__")


def test_get_top_factors_is_cached(trained_pipeline):
    first = predictor._get_top_factors(trained_pipeline)
    second = predictor._get_top_factors(trained_pipeline)
    assert first is second


def test_predict_churn_includes_top_factors(monkeypatch, trained_pipeline):
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
