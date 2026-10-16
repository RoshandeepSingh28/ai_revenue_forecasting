from pathlib import Path
import json
import math

def record_actual(target_date, country, actual_revenue, path="logs/actuals.jsonl"):
    if actual_revenue < 0:
        raise ValueError("actual_revenue must be non-negative")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"target_date": target_date, "country": country,
                            "actual_revenue": float(actual_revenue)}) + "\n")

def monitoring_summary(predictions_path="logs/predictions.jsonl", actuals_path="logs/actuals.jsonl"):
    predictions_path, actuals_path = Path(predictions_path), Path(actuals_path)
    predictions = []
    actuals = []
    if predictions_path.exists():
        for line in predictions_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                predictions.append(json.loads(line))
    if actuals_path.exists():
        for line in actuals_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                actuals.append(json.loads(line))
    actual_map = {(a["target_date"], a["country"]): a["actual_revenue"] for a in actuals}
    errors = []
    for p in predictions:
        key = (p.get("target_date"), p.get("country"))
        if key in actual_map:
            errors.append(abs(float(p["predicted_revenue"]) - float(actual_map[key])))
    return {
        "prediction_count": len(predictions),
        "actual_count": len(actuals),
        "matched_observations": len(errors),
        "mae_on_matched_observations": round(sum(errors) / len(errors), 4) if errors else None,
        "status": "monitoring_active" if predictions else "waiting_for_predictions"
    }
