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
    "unique_payloads",
    "payload_entropy",
]


def extract_features(csv_path):
    traffic = defaultdict(list)

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"timestamp_s", "can_id", "data"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(
                f"{csv_path.name} must contain columns: "
                f"{', '.join(sorted(required))}"
            )

        for row in reader:
            traffic[row["can_id"]].append({
                "timestamp": float(row["timestamp_s"]),
                "data": row["data"],
            })

    rows = []
    for can_id, messages in sorted(traffic.items()):
        messages.sort(key=lambda m: m["timestamp"])

        for start in range(0, len(messages), WINDOW_SIZE):
            window = messages[start:start + WINDOW_SIZE]
            if len(window) < 10:
                continue

            intervals = [
                (window[i]["timestamp"] - window[i - 1]["timestamp"]) * 1000
                for i in range(1, len(window))
            ]

            counts = Counter(message["data"] for message in window)
            total = len(window)
            entropy = -sum(
                (count / total) * math.log2(count / total)
                for count in counts.values()
            )

            rows.append({
                "source_file": csv_path.name,
                "can_id": can_id,
                "message_count": total,
                "avg_interval_ms": round(
                    sum(intervals) / len(intervals), 3
                ) if intervals else 0.0,
                "unique_payloads": len(counts),
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

    model = joblib.load(MODEL_FILE)
    all_rows = []

    for path in input_files:
        all_rows.extend(extract_features(path))

    if not all_rows:
        raise ValueError("No feature windows found in the input traffic.")

    df = pd.DataFrame(all_rows)
    predictions = model.predict(df[FEATURES])
    scores = model.decision_function(df[FEATURES])

    df["ml_prediction"] = [
        "NORMAL" if value == 1 else "ANOMALY"
        for value in predictions
    ]
    df["anomaly_score"] = scores
    df["rate_based_prediction"] = [
        "HIGH_RATE_SUSPECTED" if interval < 30.0
        else "NORMAL_BY_BASELINE"
        for interval in df["avg_interval_ms"]
    ]
    df["prediction"] = [
        "HIGH_RATE_SUSPECTED" if interval < 30.0
        else ml_label
        for interval, ml_label in zip(
            df["avg_interval_ms"], df["ml_prediction"]
        )
    ]

    RESULTS_DIR.mkdir(exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(df[[
        "source_file", "can_id", "message_count",
        "prediction", "anomaly_score"
    ]].to_string(index=False))
    print(f"\nIntegration results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
