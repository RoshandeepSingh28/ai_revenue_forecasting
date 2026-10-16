from src.model import train_and_save, load_bundle, predict_for_country

def test_model_training_compares_baseline(tmp_path, sample_data, monkeypatch):
    monkeypatch.chdir(tmp_path)
    metrics = train_and_save(sample_data)
    assert metrics["train_rows"] > 0
    assert metrics["test_rows"] > 0
    assert "mae" in metrics["model"]
    assert "mae" in metrics["baseline_weekly_seasonal"]
    bundle = load_bundle()
    prediction = predict_for_country(bundle, "2026-10-20", "India")
    assert prediction >= 0

def test_unknown_country_raises(client):
    import app as flask_app
    import pytest
    with pytest.raises(ValueError):
        predict_for_country(flask_app.get_bundle(), "2026-10-20", "Unknown")
