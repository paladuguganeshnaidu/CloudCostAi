import pandas as pd

REQUIRED_COLUMNS = [
    "Resource ID",
    "Service Name",
    "Usage Quantity",
    "Usage Unit",
    "Region/Zone",
    "CPU Utilization (%)",
    "Memory Utilization (%)",
    "Network Inbound Data (Bytes)",
    "Network Outbound Data (Bytes)",
    "Usage Start Date",
    "Usage End Date",
    "Cost per Quantity ($)",
    "Unrounded Cost ($)",
    "Rounded Cost ($)",
    "Total Cost (INR)",
]

NUMERIC_COLUMNS = [
    "Usage Quantity",
    "CPU Utilization (%)",
    "Memory Utilization (%)",
    "Network Inbound Data (Bytes)",
    "Network Outbound Data (Bytes)",
    "Cost per Quantity ($)",
    "Unrounded Cost ($)",
    "Rounded Cost ($)",
    "Total Cost (INR)",
]


def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and preprocess the cloud cost dataset."""
    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    for column in df.select_dtypes(include=["object"]).columns:
        df[column] = df[column].astype(str).str.strip()

    try:
        df["Usage Start Date"] = pd.to_datetime(
            df["Usage Start Date"],
            format="%d-%m-%Y %H:%M",
        )
        df["Usage End Date"] = pd.to_datetime(
            df["Usage End Date"],
            format="%d-%m-%Y %H:%M",
        )
    except Exception as exc:
        raise ValueError(
            f"Invalid date format found in dataset.\n{exc}"
        ) from exc

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="raise")

    return df