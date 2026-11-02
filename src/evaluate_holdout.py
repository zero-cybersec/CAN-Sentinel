import tempfile
import math
from pathlib import Path

import joblib
import pandas as pd

from src.integration_test import extract_features, FEATURES, MODEL_FILE
from src.evaluate_detectors import calculate_metrics
from src.sequence_detector import sequence_match_ratio, hybrid_prediction

BASE_DIR = Path(__file__).resolve().parent.parent
HOLDOUT_FILE = BASE_DIR / "results" / "holdout_traffic.csv"
METRICS_FILE = BASE_DIR / "results" / "holdout_evaluation_metrics.csv"
PREDICTIONS_FILE = BASE_DIR / "results" / "holdout_window_predictions.csv"


def main():
    if not HOLDOUT_FILE.exists():
        raise FileNotFoundError(HOLDOUT_FILE)
    if not MODEL_FILE.exists():
        raise FileNotFoundError(MODEL_FILE)

    traffic = pd.read_csv(HOLDOUT_FILE)
    required = {"timestamp_s", "can_id", "data", "scenario", "label"}
    if not required.issubset(traffic.columns):
        raise ValueError(f"Missing columns: {sorted(required - set(traffic.columns))}")

    if traffic[list(required)].isnull().any().any():
        raise ValueError("Holdout contains missing required values.")

    model = joblib.load(MODEL_FILE)
    metric_rows = []
    prediction_rows = []

    with tempfile.TemporaryDirectory() as temp_dir:
        for scenario, group in traffic.groupby("scenario", sort=True):
            labels = group["label"].astype(str).str.lower().unique()
            if len(labels) != 1 or labels[0] not in {"normal", "attack"}:
                raise ValueError(f"Invalid ground-truth labels for {scenario}: {labels}")

            scenario_file = Path(temp_dir) / f"{scenario}.csv"
            group[["timestamp_s", "can_id", "data"]].to_csv(
                scenario_file, index=False
            )

            windows = extract_features(scenario_file)
            if not windows:
                raise ValueError(f"No feature windows generated for {scenario}")

            sequence_traffic = group.copy()
            sequence_traffic["timestamp_s"] = pd.to_numeric(
                sequence_traffic["timestamp_s"], errors="raise"
            )
            sequence_traffic = sequence_traffic.sort_values("timestamp_s").copy()
            sequence_traffic["window_id"] = (
                (sequence_traffic["timestamp_s"] -
                 sequence_traffic["timestamp_s"].min()) / 0.5
            ).apply(math.floor)

            sequence_windows = [
                window for _, window in
                sequence_traffic.groupby("window_id", sort=True)
            ]

            if len(sequence_windows) != len(windows):
                raise ValueError(
                    f"Sequence/feature window mismatch for {scenario}: "
                    f"{len(sequence_windows)} vs {len(windows)}"
                )

            features = pd.DataFrame(windows)[FEATURES]
            ml_raw = model.predict(features)

            for index, row in enumerate(windows):
                sequence_ratio = sequence_match_ratio(sequence_windows[index])
                sequence_label = (
                    "REPLAY_SUSPECTED"
                    if sequence_ratio >= 0.8
                    else "NORMAL_BY_SEQUENCE"
                )

                ml_value = ml_raw[index]
                ml_label = (
                    str(ml_value).upper()
                    if isinstance(ml_value, str)
                    else ("NORMAL" if ml_value == 1 else "ANOMALY")
                )

                rate_label = (
                    "HIGH_RATE_SUSPECTED"
                    if row["avg_interval_ms"] <= 10.0
                    else "NORMAL_BY_BASELINE"
                )

                hybrid_label = hybrid_prediction(rate_label, sequence_label, ml_label)

                prediction_rows.append({
                    "scenario": scenario,
                    "actual_label": labels[0],
                    "window": index + 1,
                    "sequence_match_ratio": round(sequence_ratio, 4),
                    "sequence_prediction": sequence_label,
                    **{feature: row[feature] for feature in FEATURES},
                    "ml_prediction": ml_label,
                    "rate_prediction": rate_label,
                    "hybrid_prediction": hybrid_label,
                })

            scenario_predictions = prediction_rows[-len(windows):]
            actual = [1 if labels[0] == "attack" else 0] * len(windows)

            for detector, column in [
                ("ML", "ml_prediction"),
                ("Rate-based", "rate_prediction"),
                ("Hybrid", "hybrid_prediction"),
                ("Sequence-based", "sequence_prediction"),
            ]:
                predicted = [
                    1 if item[column] in {
                        "ANOMALY", "HIGH_RATE_SUSPECTED", "REPLAY_SUSPECTED"
                    }
                    else 0
                    for item in scenario_predictions
                ]
                metric_rows.append({
                    "scenario": scenario,
                    "detector": detector,
                    **calculate_metrics(actual, predicted),
                })

    metrics = pd.DataFrame(metric_rows)
    predictions = pd.DataFrame(prediction_rows)

    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(METRICS_FILE, index=False)
    predictions.to_csv(PREDICTIONS_FILE, index=False)

    print("\nHOLDOUT SCENARIO COUNTS:")
    print(traffic.groupby(["scenario", "label"]).size().to_string())
    print("\nDETECTOR METRICS:")
    print(metrics.to_string(index=False))
    print(f"\nMetrics saved: {METRICS_FILE}")
    print(f"Window predictions saved: {PREDICTIONS_FILE}")

if __name__ == "__main__":
    main()
