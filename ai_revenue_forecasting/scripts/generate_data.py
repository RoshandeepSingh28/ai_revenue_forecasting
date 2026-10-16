from pathlib import Path
import numpy as np
import pandas as pd

def generate(path="data/revenue.csv", days=540, seed=42):
    rng = np.random.default_rng(seed)
    end = pd.Timestamp.today().normalize()
    dates = pd.date_range(end=end, periods=days, freq="D")
    countries = {"India": 12000, "United States": 22000, "United Kingdom": 9000}
    rows = []
    for country, base in countries.items():
        for i, date in enumerate(dates):
            weekly = 1 + 0.16 * np.sin(2 * np.pi * date.dayofweek / 7)
            annual = 1 + 0.12 * np.sin(2 * np.pi * date.dayofyear / 365.25)
            growth = 1 + 0.00045 * i
            holiday = 1.18 if date.month in (11, 12) else 1.0
            revenue = max(0, base * weekly * annual * growth * holiday + rng.normal(0, base * 0.07))
            purchases = max(0, int(revenue / rng.uniform(85, 140)))
            views = max(purchases, int(purchases * rng.uniform(25, 55)))
            rows.append({"date": date.date().isoformat(), "country": country,
                         "revenue": round(float(revenue), 2), "purchases": purchases,
                         "total_views": views})
    df = pd.DataFrame(rows)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Wrote {len(df)} synthetic rows to {path}")
    return df

if __name__ == "__main__":
    generate()
