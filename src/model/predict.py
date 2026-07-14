from pathlib import Path

import joblib
import pandas as pd

from src.data.feature_engineering import create_features

MODEL_DIR = Path("models")


def load_artifacts():

    model = joblib.load(MODEL_DIR / "linear_regression.pkl")

    preprocessor = joblib.load(MODEL_DIR / "preprocessor.pkl")

    return model, preprocessor


def predict_cost(input_df: pd.DataFrame):

    model, preprocessor = load_artifacts()

    input_df = create_features(input_df)

    X = input_df.drop(columns=["Total Cost (INR)"], errors="ignore")

    X_processed = preprocessor.transform(X)

    prediction = model.predict(X_processed)

    return prediction