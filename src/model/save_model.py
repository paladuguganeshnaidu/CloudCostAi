import joblib
from pathlib import Path


def save_training_artifacts(training_result: dict):

    model_dir = Path("models")
    model_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        training_result["model"],
        model_dir / "linear_regression.pkl"
    )

    joblib.dump(
        training_result["preprocessor"],
        model_dir / "preprocessor.pkl"
    )

    joblib.dump(
        training_result["feature_names"],
        model_dir / "feature_names.pkl"
    )