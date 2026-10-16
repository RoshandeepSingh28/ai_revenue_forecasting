from pathlib import Path
from flask import Flask, jsonify, request
from src.data_pipeline import load_data
from src.model import load_bundle, predict_for_country
from src.logging_utils import write_prediction_log
from src.monitoring import record_actual, monitoring_summary

app = Flask(__name__)
BUNDLE = None

def get_bundle():
    global BUNDLE
    if BUNDLE is None:
        BUNDLE = load_bundle()
    return BUNDLE

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "ai-revenue-forecast"})

@app.get("/predict")
def predict():
    target_date = request.args.get("target_date", "").strip()
    country = request.args.get("country", "").strip()
    if not target_date:
        return jsonify({"error": "target_date is required (YYYY-MM-DD)"}), 400
    try:
        parsed = __import__("datetime").date.fromisoformat(target_date)
    except ValueError:
        return jsonify({"error": "target_date must use YYYY-MM-DD format"}), 400
    try:
        bundle = get_bundle()
        countries = [country] if country else sorted(bundle["history"]["country"].unique())
        predictions = []
        for name in countries:
            value = predict_for_country(bundle, parsed.isoformat(), name)
            record = {"target_date": parsed.isoformat(), "country": name,
                      "predicted_revenue": round(value, 2), "model": "random_forest"}
            write_prediction_log(record)
            predictions.append(record)
        if country:
            return jsonify(predictions[0])
        return jsonify({"target_date": parsed.isoformat(), "predictions": predictions,
                        "combined_predicted_revenue": round(sum(x["predicted_revenue"] for x in predictions), 2)})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 503
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/monitor/actual")
def actual():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "JSON body is required"}), 400
    required = {"target_date", "country", "actual_revenue"}
    if not required.issubset(payload):
        return jsonify({"error": f"Required fields: {sorted(required)}"}), 400
    try:
        __import__("datetime").date.fromisoformat(str(payload["target_date"]))
        actual_value = float(payload["actual_revenue"])
        if not __import__("math").isfinite(actual_value):
            raise ValueError("actual_revenue must be finite")
        record_actual(str(payload["target_date"]), str(payload["country"]), actual_value)
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"status": "actual_recorded"}), 201

@app.get("/monitor")
def monitor():
    return jsonify(monitoring_summary())

if __name__ == "__main__":
    # Use a production WSGI server rather than Flask's dev server for real deployments.
    app.run(host="0.0.0.0", port=5000, debug=False)
