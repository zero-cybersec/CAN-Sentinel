
import csv
from pathlib import Path

SOURCE = Path("results/holdout_traffic.csv")
OUTPUT = Path("results/day17_mixed_traffic.csv")

FIELDS = ["timestamp_s", "can_id", "data", "scenario", "label"]

SCENARIOS = [
    ("Normal", "normal", 0),
    ("Burst", "attack", 10),
    ("Replay", "attack", 20),
    ("Recovery", "normal", 30),
]

if not SOURCE.exists():
    raise FileNotFoundError(f"Missing source: {SOURCE}")

with SOURCE.open(newline="") as file:
    reader = csv.DictReader(file)

    if reader.fieldnames != FIELDS:
        raise ValueError("Source CSV schema does not match")

    source_rows = list(reader)

mixed_rows = []

for scenario, expected_label, offset in SCENARIOS:
    rows = [
        row for row in source_rows
        if row["scenario"] == scenario
    ]

    if not rows:
        raise ValueError(f"Missing scenario: {scenario}")

    if any(row["label"] != expected_label for row in rows):
        raise ValueError(f"Unexpected label in {scenario}")

    for row in rows:
        mixed_rows.append({
            "timestamp_s": round(
                float(row["timestamp_s"]) + offset, 3
            ),
            "can_id": row["can_id"],
            "data": row["data"],
            "scenario": row["scenario"],
            "label": row["label"],
        })

mixed_rows.sort(key=lambda row: float(row["timestamp_s"]))

timestamps = [float(row["timestamp_s"]) for row in mixed_rows]

if timestamps != sorted(timestamps):
    raise ValueError("Timestamps are not chronological")

if len(mixed_rows) != 6500:
    raise ValueError("Unexpected frame count")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(mixed_rows)

print(f"Generated: {OUTPUT}")
print(f"Total frames: {len(mixed_rows)}")
print(f"Timestamp range: {timestamps[0]} - {timestamps[-1]} seconds")
print("Scenario order: Normal -> Burst -> Replay -> Recovery")
print("Chronological validation: PASS")
