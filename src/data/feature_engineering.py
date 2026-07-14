import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def create_features(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df["Usage Duration (Hours)"] = (
        (df["Usage End Date"] - df["Usage Start Date"])
        .dt.total_seconds() / 3600
    )

    df["Total Network Traffic"] = (
        df["Network Inbound Data (Bytes)"]
        + df["Network Outbound Data (Bytes)"]
    )

    df.drop(
        columns=[
            "Resource ID",
            "Usage Start Date",
            "Usage End Date",
            "Rounded Cost ($)",
            "Unrounded Cost ($)",
        ],
        inplace=True,
    )

    return df


def build_preprocessor(X: pd.DataFrame):

    categorical_columns = [
        "Service Name",
        "Usage Unit",
        "Region/Zone",
    ]

    numerical_columns = [
        column
        for column in X.columns
        if column not in categorical_columns
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_columns,
            ),
            (
                "numerical",
                StandardScaler(),
                numerical_columns,
            ),
        ]
    )

    return preprocessor


def engineer_features(df: pd.DataFrame):

    df = create_features(df)

    X = df.drop(columns=["Total Cost (INR)"])

    y = df["Total Cost (INR)"]

    preprocessor = build_preprocessor(X)

    return X, y, preprocessor