from pathlib import Path

import pandas as pd


INPUT_FILE = Path("results/integration_results.csv")
OUTPUT_FILE = Path("results/detector_evaluation_metrics.csv")

DETECTORS = {
    "ML": "ml_prediction",
    "Rate-based": "rate_based_prediction",
    "Hybrid": "prediction",
}


def actual_label(source_file):
    """Infer synthetic ground-truth label from the dataset filename."""
    name = str(source_file).lower()

    if "high_rate" in name or "high-rate" in name:
        return 1  # Attack / high-rate traffic
    if "normal" in name:
        return 0  # Normal traffic

    raise ValueError(f"Cannot infer ground truth from filename: {source_file}")


def predicted_label(value):
    """Convert detector output into binary labels: 1=attack, 0=normal."""
    label = str(value).strip().upper()

    if label in {"NORMAL", "NORMAL_BY_BASELINE"}:
        return 0
    if label in {"ANOMALY", "HIGH_RATE_SUSPECTED"}:
        return 1

    raise ValueError(f"Unknown detector prediction: {value}")


def calculate_metrics(actual, predicted):
    if len(actual) != len(predicted) or not actual:
        raise ValueError("Actual and predicted labels must be non-empty and equal in length.")

    tp = sum(a == 1 and p == 1 for a, p in zip(actual, predicted))
    fp = sum(a == 0 and p == 1 for a, p in zip(actual, predicted))
    tn = sum(a == 0 and p == 0 for a, p in zip(actual, predicted))
    fn = sum(a == 1 and p == 0 for a, p in zip(actual, predicted))

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    accuracy = (tp + tn) / len(actual)

    return {
        "evaluated_windows": len(actual),
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "accuracy": round(accuracy, 4),
    }


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input results not found: {INPUT_FILE}")

    data = pd.read_csv(INPUT_FILE)

    required = {"source_file", *DETECTORS.values()}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing required CSV columns: {sorted(missing)}")
    if data.empty:
        raise ValueError("Integration results CSV is empty.")

    actual = [actual_label(name) for name in data["source_file"]]
    rows = []

    for detector_name, column in DETECTORS.items():
        predicted = [predicted_label(value) for value in data[column]]
        rows.append({
            "detector": detector_name,
            **calculate_metrics(actual, predicted),
        })

    metrics = pd.DataFrame(rows)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(OUTPUT_FILE, index=False)

    print(metrics.to_string(index=False))
    print(f"\nEvaluation metrics saved to: {OUTPUT_FILE}")
    print("Note: Results use synthetic filename-derived labels, not independent real-world validation.")


if __name__ == "__main__":
    main()
