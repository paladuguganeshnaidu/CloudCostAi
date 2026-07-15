import joblib
import pandas as pd

from src.data.feature_engineering import prepare_model_frame
from src.utils.config import MODEL_DIR
from src.utils.logger import logger


def load_artifacts():
    model = joblib.load(MODEL_DIR / "linear_regression.pkl")
    preprocessor = joblib.load(MODEL_DIR / "preprocessor.pkl")
    return model, preprocessor


def predict_cost(input_df: pd.DataFrame):
    model, preprocessor = load_artifacts()
    prepared_frame = prepare_model_frame(input_df)
    X = prepared_frame.drop(columns=["Total Cost (INR)"], errors="ignore")
    X_processed = preprocessor.transform(X)
    predictions = model.predict(X_processed)
    clipped_predictions = []
    for prediction in predictions:
        if prediction < 0:
            logger.warning("Negative prediction detected; clipping to zero. Value=%s", prediction)
            clipped_predictions.append(0.0)
        else:
            clipped_predictions.append(float(prediction))
    return clipped_predictions