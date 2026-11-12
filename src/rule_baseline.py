import csv
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
THRESHOLD_MS = 30.0
WINDOW_SIZE = 100

INPUT_FILES = [
    ("normal_traffic.csv", "NORMAL_DATASET"),
    ("high_rate_traffic.csv", "HIGH_RATE_DATASET"),
]

def analyse_file(filename, dataset_label):
    path = RESULTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    traffic = defaultdict(list)

    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required = {"timestamp_s", "can_id"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"{filename} must contain columns: {sorted(required)}")

        for row in reader:
            traffic[row["can_id"]].append(float(row["timestamp_s"]))

    results = []

    for can_id, timestamps in sorted(traffic.items()):
        timestamps.sort()

        for start in range(0, len(timestamps), WINDOW_SIZE):
            window = timestamps[start:start + WINDOW_SIZE]
            if len(window) < 10:
                continue

            intervals_ms = [
                (window[i] - window[i - 1]) * 1000
                for i in range(1, len(window))
            ]

            avg_interval = sum(intervals_ms) / len(intervals_ms)
            prediction = (
                "HIGH_RATE_SUSPECTED"
                if avg_interval < THRESHOLD_MS
                else "NORMAL_BY_BASELINE"
            )

            results.append({
                "source_file": filename,
                "dataset": dataset_label,
                "can_id": can_id,
                "window_start_message": start + 1,
                "message_count": len(window),
                "avg_interval_ms": round(avg_interval, 4),
                "min_interval_ms": round(min(intervals_ms), 4),
                "threshold_ms": THRESHOLD_MS,
                "prediction": prediction,
            })

    return results

def main():
    all_results = []

    for filename, label in INPUT_FILES:
        all_results.extend(analyse_file(filename, label))

    if not all_results:
        raise ValueError("No valid traffic windows were produced.")

    output = RESULTS_DIR / "rule_baseline_results.csv"
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=all_results[0].keys())
        writer.writeheader()
        writer.writerows(all_results)

    print("Rule-based baseline evaluation complete")
    print(f"Threshold: {THRESHOLD_MS} ms")
    print(f"Window size: {WINDOW_SIZE} messages per CAN ID")
    print(f"Windows analysed: {len(all_results)}")

    for filename, _ in INPUT_FILES:
        rows = [r for r in all_results if r["source_file"] == filename]
        flagged = sum(r["prediction"] == "HIGH_RATE_SUSPECTED" for r in rows)
        normal = sum(r["prediction"] == "NORMAL_BY_BASELINE" for r in rows)
        print(f"\n{filename}:")
        print(f"  Windows flagged: {flagged}")
        print(f"  Windows not flagged: {normal}")

    print(f"\nResults saved to: {output}")

if __name__ == "__main__":
    main()
