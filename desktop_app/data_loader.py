import pandas as pd
from pathlib import Path

def load_exoplanet_data():
    data_path = Path('/workspace/data/processed/exoplanets_cleaned.parquet')
    if not data_path.exists():
        print(f"Data file not found: {data_path}")
        return []
    df = pd.read_parquet(data_path)
    # Return as list of dicts for easy iteration
    return df.to_dict(orient='records') 