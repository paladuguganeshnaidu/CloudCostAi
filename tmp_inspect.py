from pathlib import Path
from src.data.loader import load_dataset
from src.data.preprocessing import preprocess_dataset
from src.model.predict import predict_cost

path = Path('data/raw/gcp_final_approved_dataset.csv')
df = load_dataset(str(path))
df = preprocess_dataset(df)

for i in range(min(10, len(df))):
    sample = df.iloc[[i]].copy()
    pred = predict_cost(sample)[0]
    actual = sample['Total Cost (INR)'].iloc[0]
    print(i, actual, pred)
