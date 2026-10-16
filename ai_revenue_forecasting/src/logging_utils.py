from pathlib import Path
from datetime import datetime, timezone
import json

def write_prediction_log(record, path="logs/predictions.jsonl"):
    """Append a prediction event to a JSONL log."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {"logged_at": datetime.now(timezone.utc).isoformat(), **record}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    return event
