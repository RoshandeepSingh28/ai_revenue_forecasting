import json
from pathlib import Path
import pytest
from src.logging_utils import write_prediction_log
from src.monitoring import record_actual, monitoring_summary

def test_prediction_logging_is_jsonl(tmp_path):
    path = tmp_path / "isolated" / "predictions.jsonl"
    event = write_prediction_log({"target_date": "2026-10-20", "country": "India",
                                  "predicted_revenue": 100.0}, path=path)
    assert event["country"] == "India"
    assert len(path.read_text().splitlines()) == 1
    assert json.loads(path.read_text().splitlines()[0])["predicted_revenue"] == 100.0

def test_monitoring_matches_actual_and_prediction(tmp_path):
    pred = tmp_path / "predictions.jsonl"
    actual = tmp_path / "actuals.jsonl"
    write_prediction_log({"target_date": "2026-10-20", "country": "India",
                          "predicted_revenue": 100.0}, path=pred)
    record_actual("2026-10-20", "India", 120.0, path=actual)
    summary = monitoring_summary(pred, actual)
    assert summary["matched_observations"] == 1
    assert summary["mae_on_matched_observations"] == 20.0

def test_negative_actual_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        record_actual("2026-10-20", "India", -1, path=tmp_path / "actuals.jsonl")
