# AI-Powered Revenue Forecasting and Anomaly Detection

A reproducible Flask API project for forecasting daily revenue by country. It includes synthetic demo data, data ingestion, exploratory visualizations, model comparison, automated tests, prediction logging, simple performance monitoring, and Docker packaging.

> **Data note:** This project generates clearly labeled synthetic demo data. Replace it with your authorized business data before using it for real decisions.

## Features
- Generate and ingest daily revenue, purchases, and views by country.
- Train and compare a seasonal-naive baseline against a Random Forest model.
- Forecast revenue for a requested `target_date` and `country`, or all countries.
- Validate API inputs and return useful error messages.
- Log predictions separately from source data.
- Monitor recent prediction errors when actual values are supplied.
- Unit tests for API, model, logging, and monitoring.
- EDA charts and a model-vs-baseline visualization.
- Dockerfile and one-command test runner.

## Quick start

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_data.py
python scripts/run_eda.py
python scripts/train_model.py
python app.py
```

The API starts at `http://127.0.0.1:5000`.

### Example requests

Forecast one country:

```bash
curl "http://127.0.0.1:5000/predict?target_date=2026-10-20&country=India"
```

Forecast all available countries:

```bash
curl "http://127.0.0.1:5000/predict?target_date=2026-10-20"
```

Submit an actual result for monitoring:

```bash
curl -X POST http://127.0.0.1:5000/monitor/actual \
  -H "Content-Type: application/json" \
  -d '{"target_date":"2026-10-20","country":"India","actual_revenue":12500}'
```

Check monitoring summary:

```bash
curl http://127.0.0.1:5000/monitor
```

Health check:

```bash
curl http://127.0.0.1:5000/health
```

## Tests

Run all tests with one script:

```bash
python scripts/run_tests.py
```

or:

```bash
pytest -q
```

Tests use temporary paths / isolated test files where appropriate; they do not depend on production logs.

## EDA and model comparison

```bash
python scripts/run_eda.py
python scripts/train_model.py
```

Generated artifacts:
- `artifacts/eda_revenue_by_country.png`
- `artifacts/eda_daily_metrics.png`
- `artifacts/model_comparison.png`
- `artifacts/model_metrics.json`
- `artifacts/model.joblib`

## Docker

```bash
docker build -t ai-revenue-forecast .
docker run --rm -p 5000:5000 ai-revenue-forecast
```

The container generates demo data and trains the model at startup if required.

## API response examples

Single country:

```json
{
  "target_date": "2026-10-20",
  "country": "India",
  "predicted_revenue": 12345.67,
  "model": "random_forest"
}
```

All countries returns a list of predictions and a combined total.

## Project structure

```text
ai_revenue_forecasting/
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── data/
├── artifacts/
├── logs/
├── src/
│   ├── data_pipeline.py
│   ├── features.py
│   ├── model.py
│   ├── logging_utils.py
│   └── monitoring.py
├── scripts/
│   ├── generate_data.py
│   ├── train_model.py
│   ├── run_eda.py
│   └── run_tests.py
└── tests/
```

## Limitations and next steps
- Demo data is synthetic and should not be interpreted as real business performance.
- The demo model is intended for an educational capstone, not production financial decisions.
- For deployment, add authentication, rate limiting, secure secrets management, structured centralized logging, and a proper database.
