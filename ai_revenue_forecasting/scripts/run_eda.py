from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.data_pipeline import load_data

def run():
    out = Path("artifacts")
    out.mkdir(parents=True, exist_ok=True)
    df = load_data()
    by_country = df.groupby("country")["revenue"].mean().sort_values()
    ax = by_country.plot(kind="bar", title="Average Daily Revenue by Country", ylabel="Revenue")
    ax.figure.tight_layout()
    ax.figure.savefig(out / "eda_revenue_by_country.png")
    plt.close(ax.figure)
    daily = df.groupby("date")[["revenue", "purchases", "total_views"]].sum()
    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    for col, axis in zip(daily.columns, axes):
        axis.plot(daily.index, daily[col])
        axis.set_title(f"Daily total {col}")
        axis.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "eda_daily_metrics.png")
    plt.close(fig)
    print(f"EDA charts saved to {out}/")

if __name__ == "__main__":
    run()
