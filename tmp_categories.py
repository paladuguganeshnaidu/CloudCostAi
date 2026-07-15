from src.data.loader import load_dataset
from src.data.preprocessing import preprocess_dataset

path='data/raw/gcp_final_approved_dataset.csv'
df=preprocess_dataset(load_dataset(path))
print('services', sorted(df['Service Name'].dropna().astype(str).str.strip().unique().tolist()))
print('regions', sorted(df['Region/Zone'].dropna().astype(str).str.strip().unique().tolist()))
print('units', sorted(df['Usage Unit'].dropna().astype(str).str.strip().unique().tolist()))
