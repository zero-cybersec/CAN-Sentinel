import csv
import math
from collections import defaultdict, Counter
from pathlib import Path

import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
MODEL_FILE = BASE_DIR / "can_model.joblib"
OUTPUT_FILE = RESULTS_DIR / "integration_results.csv"

WINDOW_SIZE = 100
FEATURES = [
    "message_count",
    "avg_interval_ms",
    "unique_can_ids",
    "unique_payloads",
    "payload_entropy",
]


def extract_features(csv_path):
    import math
    from collections import Counter
    import pandas as pd

    traffic = pd.read_csv(csv_path)
    required = {"timestamp_s", "can_id", "data"}
    if not required.issubset(traffic.columns):
        raise ValueError(f"{csv_path} must contain {sorted(required)}")

    traffic["timestamp_s"] = pd.to_numeric(
        traffic["timestamp_s"], errors="raise"
    )
    traffic = traffic.sort_values("timestamp_s").copy()
    if traffic.empty:
        return []

    traffic["window_id"] = (
        (traffic["timestamp_s"] - traffic["timestamp_s"].min()) / 0.5
    ).apply(math.floor)

    rows = []
    for _, window in traffic.groupby("window_id", sort=True):
        timestamps = window["timestamp_s"].tolist()
        intervals = [
            (timestamps[i] - timestamps[i - 1]) * 1000
            for i in range(1, len(timestamps))
        ]
        payload_counts = Counter(window["data"].astype(str))
        total = len(window)
        entropy = -sum(
            (count / total) * math.log2(count / total)
            for count in payload_counts.values()
        )

        rows.append({
            "source_file": Path(csv_path).name,
            "message_count": total,
            "avg_interval_ms": round(
                sum(intervals) / len(intervals), 3
            ) if intervals else 0.0,
            "unique_can_ids": window["can_id"].nunique(),
            "unique_payloads": len(payload_counts),
            "payload_entropy": round(entropy, 4),
        })
    return rows

def main():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_FILE}")

    input_files = [
        RESULTS_DIR / "normal_traffic.csv",
        RESULTS_DIR / "high_rate_traffic.csv",
    ]
    missing = [str(path) for path in input_files if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Waiting for Zeeshan's output files:\n" + "\n".join(missing)
        )

    model = joblib.load("can_model_candidate.joblib")
    all_rows = []

    for path in input_files:
        all_rows.extend(extract_features(path))

    if not all_rows:
        raise ValueError("No feature windows found in the input traffic.")

    df = pd.DataFrame(all_rows)
    predictions = model.predict(df[FEATURES])
    scores = model.decision_function(df[FEATURES])

    df["ml_prediction"] = [
        str(value).upper() if isinstance(value, str)
        else ("NORMAL" if value == 1 else "ANOMALY")
        for value in predictions
    ]
    df["anomaly_score"] = scores
    df["rate_based_prediction"] = [
        "HIGH_RATE_SUSPECTED" if interval < 10.0
        else "NORMAL_BY_BASELINE"
        for interval in df["avg_interval_ms"]
    ]
    df["prediction"] = [
        "HIGH_RATE_SUSPECTED" if interval < 10.0
        else ml_label
        for interval, ml_label in zip(
            df["avg_interval_ms"], df["ml_prediction"]
        )
    ]

    RESULTS_DIR.mkdir(exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(df[[
        "source_file", "message_count", "avg_interval_ms",
        "unique_can_ids", "unique_payloads", "payload_entropy",
        "ml_prediction", "anomaly_score", "rate_based_prediction",
        "prediction"
    ]].to_string(index=False))
    print(f"\nIntegration results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
