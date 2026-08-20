"""
Trains a baseline churn prediction model and saves it to data/model.pkl.

Dataset: Telco Customer Churn (Kaggle)
    https://www.kaggle.com/datasets/blastchar/telco-customer-churn

Download instructions:
    Option A - manual:
        1. Open the Kaggle page above and click "Download".
        2. Unzip and copy the CSV (WA_Fn-UseC_-Telecom-Customer-Churn.csv)
           into backend/data/telco_churn.csv

    Option B - Kaggle CLI (requires a Kaggle account + API token in
    ~/.kaggle/kaggle.json, see https://github.com/Kaggle/kaggle-api#api-credentials):
        pip install kaggle
        kaggle datasets download -d blastchar/telco-customer-churn -p data --unzip
        mv "data/WA_Fn-UseC_-Telecom-Customer-Churn.csv" data/telco_churn.csv

Usage:
    python train_model.py
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
RAW_CSV_PATH = DATA_DIR / "telco_churn.csv"

CATEGORICAL_FEATURES = ["contract_type"]
NUMERIC_FEATURES = ["tenure_months", "monthly_charges", "total_charges"]
BOOLEAN_FEATURES = ["has_internet_service", "has_tech_support"]

# Maps the raw Kaggle "Contract" values to the values used by the app's
# CustomerFeatures schema (see app/models/schemas.py).
CONTRACT_TYPE_MAP = {
    "Month-to-month": "month-to-month",
    "One year": "one_year",
    "Two year": "two_year",
}


def load_dataset() -> pd.DataFrame:
    """Loads the Telco Customer Churn dataset from data/telco_churn.csv and
    maps its raw columns onto the feature schema used by the app.
    """
    if not RAW_CSV_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {RAW_CSV_PATH}.\n"
            "Download the Telco Customer Churn dataset from "
            "https://www.kaggle.com/datasets/blastchar/telco-customer-churn "
            "and save it as backend/data/telco_churn.csv "
            "(see the instructions at the top of train_model.py)."
        )

    raw = pd.read_csv(RAW_CSV_PATH)

    # TotalCharges is stored as a string and has blank values for a
    # handful of customers with zero tenure; coerce and fill those with 0.
    total_charges = pd.to_numeric(raw["TotalCharges"], errors="coerce").fillna(0.0)

    df = pd.DataFrame(
        {
            "tenure_months": raw["tenure"],
            "monthly_charges": raw["MonthlyCharges"],
            "total_charges": total_charges,
            "contract_type": raw["Contract"].map(CONTRACT_TYPE_MAP),
            "has_internet_service": raw["InternetService"] != "No",
            "has_tech_support": raw["TechSupport"] == "Yes",
            "churn": raw["Churn"] == "Yes",
        }
    )
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
    df = load_dataset()

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
