from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from src.features import add_features, FEATURE_COLUMNS, country_codes

ARTIFACT_DIR = Path("artifacts")
MODEL_PATH = ARTIFACT_DIR / "model.joblib"
METRICS_PATH = ARTIFACT_DIR / "model_metrics.json"

def train_and_save(data: pd.DataFrame):
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    featured = add_features(data)
    codes = country_codes(data)
    featured["country_code"] = featured["country"].map(codes)
    usable = featured.dropna(subset=FEATURE_COLUMNS + ["revenue"]).copy()
    # Time-based split: never randomly mix future and past rows.
    usable = usable.sort_values("date")
    cutoff = usable["date"].quantile(0.8)
    train = usable[usable["date"] <= cutoff]
    test = usable[usable["date"] > cutoff]
    if train.empty or test.empty:
        raise ValueError("Not enough data for a time-based train/test split")
    model = RandomForestRegressor(n_estimators=160, min_samples_leaf=3, random_state=42, n_jobs=-1)
    model.fit(train[FEATURE_COLUMNS], train["revenue"])
    predictions = model.predict(test[FEATURE_COLUMNS])
    # Seasonal-naive baseline: same country, same weekday one week earlier.
    baseline = test["revenue_lag_7"].to_numpy()
    metrics = {
        "model": {
            "mae": float(mean_absolute_error(test["revenue"], predictions)),
            "rmse": float(np.sqrt(mean_squared_error(test["revenue"], predictions))),
        },
        "baseline_weekly_seasonal": {
            "mae": float(mean_absolute_error(test["revenue"], baseline)),
            "rmse": float(np.sqrt(mean_squared_error(test["revenue"], baseline))),
        },
        "test_rows": int(len(test)),
        "train_rows": int(len(train)),
        "split": "chronological 80/20",
        "data_note": "Synthetic demo data unless replaced by the user"
    }
    bundle = {"model": model, "country_codes": codes, "feature_columns": FEATURE_COLUMNS,
              "history": data.copy(), "trained_through": str(data["date"].max().date())}
    joblib.dump(bundle, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    return metrics

def load_bundle(path=MODEL_PATH):
    if not Path(path).exists():
        raise FileNotFoundError("Model artifact missing. Run scripts/train_model.py first.")
    return joblib.load(path)

def predict_for_country(bundle, target_date, country):
    history = bundle["history"].copy()
    history["date"] = pd.to_datetime(history["date"])
    country_history = history[history["country"] == country].sort_values("date")
    if country_history.empty:
        raise ValueError(f"Unknown country: {country}")
    target = pd.Timestamp(target_date)
    if target <= country_history["date"].max():
        # For historical dates, the app still forecasts using the most recent known lag values.
        pass
    values = country_history["revenue"].to_numpy()
    if len(values) < 28:
        raise ValueError("At least 28 days of historical data are required")
    last_date = country_history["date"].max()
    lag7 = float(values[-7])
    lag28 = float(values[-28])
    roll7 = float(np.mean(values[-7:]))
    row = pd.DataFrame([{
        "country_code": bundle["country_codes"][country],
        "day_of_week": target.dayofweek,
        "day_of_month": target.day,
        "month": target.month,
        "day_of_year": target.dayofyear,
        "is_weekend": int(target.dayofweek >= 5),
        "revenue_lag_7": lag7,
        "revenue_lag_28": lag28,
        "revenue_roll_7": roll7,
    }])
    prediction = float(bundle["model"].predict(row[bundle["feature_columns"]])[0])
    return max(0.0, prediction)
