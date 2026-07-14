import joblib
import pandas as pd

from src.data.feature_engineering import create_features
from src.utils.config import MODEL_DIR


def load_artifacts():
    model = joblib.load(MODEL_DIR / "linear_regression.pkl")
    preprocessor = joblib.load(MODEL_DIR / "preprocessor.pkl")
    return model, preprocessor


def predict_cost(input_df: pd.DataFrame):
    model, preprocessor = load_artifacts()
    prepared_frame = create_features(input_df)
    X = prepared_frame.drop(columns=["Total Cost (INR)"], errors="ignore")
    X_processed = preprocessor.transform(X)
    return model.predict(X_processed)