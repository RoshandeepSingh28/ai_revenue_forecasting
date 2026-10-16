import pandas as pd

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create calendar and lag features without using future observations."""
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"])
    out = out.sort_values(["country", "date"]).reset_index(drop=True)
    out["day_of_week"] = out["date"].dt.dayofweek
    out["day_of_month"] = out["date"].dt.day
    out["month"] = out["date"].dt.month
    out["day_of_year"] = out["date"].dt.dayofyear
    out["is_weekend"] = (out["day_of_week"] >= 5).astype(int)
    out["revenue_lag_7"] = out.groupby("country")["revenue"].shift(7)
    out["revenue_lag_28"] = out.groupby("country")["revenue"].shift(28)
    out["revenue_roll_7"] = (
        out.groupby("country")["revenue"].transform(lambda s: s.shift(1).rolling(7, min_periods=7).mean())
    )
    return out

FEATURE_COLUMNS = [
    "country_code", "day_of_week", "day_of_month", "month", "day_of_year",
    "is_weekend", "revenue_lag_7", "revenue_lag_28", "revenue_roll_7"
]

def country_codes(df):
    return {name: idx for idx, name in enumerate(sorted(df["country"].unique()))}
