import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.data_pipeline import load_data
from src.model import train_and_save

if __name__ == "__main__":
    data = load_data()
    metrics = train_and_save(data)
    print("Training complete. Metrics:")
    for name, values in metrics.items():
        print(f"{name}: {values}")

    labels = ["Random Forest", "Weekly seasonal baseline"]
    maes = [metrics["model"]["mae"], metrics["baseline_weekly_seasonal"]["mae"]]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, maes)
    ax.set_ylabel("Mean Absolute Error (lower is better)")
    ax.set_title("Model vs Baseline")
    ax.tick_params(axis="x", rotation=10)
    fig.tight_layout()
    Path("artifacts").mkdir(exist_ok=True)
    fig.savefig("artifacts/model_comparison.png")
    plt.close(fig)
    print("Comparison chart saved to artifacts/model_comparison.png")
