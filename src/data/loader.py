from pathlib import Path
import pandas as pd
def load_dataset(file_path: str) -> pd.DataFrame:
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            raise ValueError(f"DataSet {file_path} is empty.")
        return df
    except Exception as e:
        raise ValueError(f"An error occurred while loading the dataset: {e}")