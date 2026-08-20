"""
Trains a baseline churn prediction model and saves it to data/model.pkl.

Usage:
    python train_model.py

TODO:
    1. Download a churn dataset (e.g. Kaggle's "Telco Customer Churn") into data/raw.csv
    2. Adjust the feature columns below to match your dataset
    3. Replace the dummy data generation with real data loading
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

DATA_DIR = Path(__file__).parent / "data"
MODEL_PATH = DATA_DIR / "model.pkl"

CATEGORICAL_FEATURES = ["contract_type"]
NUMERIC_FEATURES = ["tenure_months", "monthly_charges", "total_charges"]
BOOLEAN_FEATURES = ["has_internet_service", "has_tech_support"]


def load_dummy_dataset(n: int = 500) -> pd.DataFrame:
    """Placeholder dataset generator so the pipeline runs out of the box.

    Replace this with `pd.read_csv(DATA_DIR / "raw.csv")` once you have
    downloaded a real dataset.
    """
    import numpy as np

    rng = np.random.default_rng(42)
    df = pd.DataFrame(
        {
            "tenure_months": rng.integers(0, 72, n),
            "monthly_charges": rng.uniform(20, 120, n),
            "total_charges": rng.uniform(20, 8000, n),
            "contract_type": rng.choice(
                ["month-to-month", "one_year", "two_year"], n
            ),
            "has_internet_service": rng.choice([True, False], n),
            "has_tech_support": rng.choice([True, False], n),
        }
    )
    # Simple synthetic churn rule for demonstration purposes only.
    churn_score = (
        (df["contract_type"] == "month-to-month").astype(int) * 0.4
        + (~df["has_tech_support"]).astype(int) * 0.3
        + (df["tenure_months"] < 12).astype(int) * 0.3
    )
    df["churn"] = (churn_score + rng.normal(0, 0.1, n)) > 0.5
    return df


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ],
        remainder="passthrough",
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=200, random_state=42)),
        ]
    )


def main():
    DATA_DIR.mkdir(exist_ok=True)
    df = load_dummy_dataset()

    feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES + BOOLEAN_FEATURES
    X = df[feature_cols]
    y = df["churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    accuracy = pipeline.score(X_test, y_test)
    print(f"Test accuracy: {accuracy:.3f}")

    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
