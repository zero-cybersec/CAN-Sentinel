
import csv
import json
from pathlib import Path

# This script compares existing simulation results.
# It does NOT generate any attack traffic.

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "traffic_results.json"
CSV_FILE = BASE_DIR / "traffic_comparison.csv"
REPORT_FILE = BASE_DIR / "findings_report.md"


def load_results():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Missing {INPUT_FILE.name}. "
            "Add your actual existing simulation results first."
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        results = json.load(file)

    for traffic_type in ("normal", "high_rate"):
        if traffic_type not in results:
            raise ValueError(
                f"Missing '{traffic_type}' results in "
                f"{INPUT_FILE.name}"
            )

        for field in (
            "message_count",
            "messages_per_second",
            "duration_seconds",
        ):
            value = results[traffic_type].get(field)

            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or value < 0
            ):
                raise ValueError(
                    f"Invalid {field} for {traffic_type}"
                )

    return results


def create_comparison(results):
    rows = []

    for traffic_type in ("normal", "high_rate"):
        data = results[traffic_type]

        rows.append({
            "traffic_type": traffic_type,
            "message_count": data["message_count"],
            "messages_per_second": data["messages_per_second"],
            "duration_seconds": data["duration_seconds"],
            "observation": (
                "Normal traffic baseline"
                if traffic_type == "normal"
                else "High-rate traffic test"
            ),
        })

    with CSV_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys()
        )
        writer.writeheader()
        writer.writerows(rows)

    return rows


def create_report(rows):
    normal = rows[0]
    high = rows[1]

    if normal["messages_per_second"] > 0:
        rate_change = (
            high["messages_per_second"]
            / normal["messages_per_second"]
        )
        rate_finding = (
            f"High-rate traffic ran at {rate_change:.2f} "
            "times the normal traffic rate."
        )
    else:
        rate_finding = (
            "A rate ratio cannot be calculated because "
            "normal traffic has a zero rate."
        )

    report = f"""# Traffic Comparison Findings Report

## Objective
Compare existing normal and high-rate simulation results.

## Results

| Metric | Normal | High-rate |
|---|---:|---:|
| Message count | {normal['message_count']} | {high['message_count']} |
| Messages per second | {normal['messages_per_second']} | {high['messages_per_second']} |
| Duration (seconds) | {normal['duration_seconds']} | {high['duration_seconds']} |

## Findings
- {rate_finding}
- Message count difference: {high['message_count'] - normal['message_count']}.
- Duration difference (high-rate minus normal):
  {high['duration_seconds'] - normal['duration_seconds']:.3f} seconds.

## Conclusion
These findings compare the supplied simulation results.
They describe observed traffic metrics and do not by
themselves establish that an intrusion occurred.
"""

    REPORT_FILE.write_text(report, encoding="utf-8")


def main():
    results = load_results()
    rows = create_comparison(results)
    create_report(rows)

    print("Comparison completed successfully.")
    print(f"CSV saved: {CSV_FILE}")
    print(f"Report saved: {REPORT_FILE}")


if __name__ == "__main__":
    main()
