import pytest
import pandas as pd
from pathlib import Path
from src.model import train_and_save
import app as flask_app

@pytest.fixture
def sample_data():
    dates = pd.date_range("2025-01-01", periods=100, freq="D")
    rows = []
    for country, base in [("India", 1000), ("Canada", 800)]:
        for i, date in enumerate(dates):
            rows.append({"date": date, "country": country,
                         "revenue": float(base + i * 2 + (date.dayofweek * 5)),
                         "purchases": int((base + i * 2) / 100), "total_views": int(base + i * 20)})
    return pd.DataFrame(rows)

@pytest.fixture
def client(tmp_path, monkeypatch, sample_data):
    # Isolate model artifacts and all logs from any real app data.
    monkeypatch.chdir(tmp_path)
    Path("artifacts").mkdir()
    train_and_save(sample_data)
    flask_app.BUNDLE = None
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as test_client:
        yield test_client
    flask_app.BUNDLE = None
