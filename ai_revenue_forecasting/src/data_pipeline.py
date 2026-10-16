from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {"date", "country", "revenue", "purchases", "total_views"}

def load_data(path="data/revenue.csv") -> pd.DataFrame:
    """Load and validate daily business metrics from a CSV file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}. Run scripts/generate_data.py first.")
    df = pd.read_csv(path, parse_dates=["date"])
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df.empty:
        raise ValueError("Input data is empty")
    if df[list(REQUIRED_COLUMNS - {"country", "date"})].isna().any().any():
        raise ValueError("Numeric business metrics cannot contain missing values")
    df["country"] = df["country"].astype(str)
    df = df.sort_values(["country", "date"]).reset_index(drop=True)
    return df
