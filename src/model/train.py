from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from src.data.feature_engineering import engineer_features
from src.data.loader import load_dataset
from src.data.preprocessing import preprocess_dataset


def train_model(dataset_path: str):
    df = load_dataset(dataset_path)
    df = preprocess_dataset(df)

    X, y, preprocessor = engineer_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.transform(X_test)

    feature_names = preprocessor.get_feature_names_out()

    model = LinearRegression()
    model.fit(X_train, y_train)

    return{
    "model": model,
    "preprocessor": preprocessor,
    "feature_names": feature_names,
    "X_train": X_train,
    "X_test": X_test,
    "y_train": y_train,
    "y_test": y_test,
    }
