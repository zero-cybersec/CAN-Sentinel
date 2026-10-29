import csv
import random
from pathlib import Path

SEED = 13

INPUT = Path("results/normal_traffic.csv")
OUTPUT = Path("results/day13_mixed_scenario_traffic.csv")
DOCS = Path("docs/day13_mixed_scenario.md")

FIELDS = [
    "timestamp",
    "can_id",
    "dlc",
    "data",
    "scenario",
    "label",
]

CAN_IDS = [0x100, 0x200, 0x300, 0x400]


def generate():
    # Never overwrite existing deliverables.
    if OUTPUT.exists() or DOCS.exists():
        raise SystemExit(
            "ERROR: A Day 13 deliverable already exists. "
            "Inspect it before making changes."
        )

    if not INPUT.exists():
        raise SystemExit(f"ERROR: Input not found: {INPUT}")

    rng = random.Random(SEED)

    with INPUT.open(newline="", encoding="utf-8") as file:
        source_rows = list(csv.DictReader(file))

    if not source_rows:
        raise SystemExit("ERROR: Normal traffic input is empty.")

    rows = []
    timestamp = 0.0

    def add_frame(can_id, data, scenario, label, interval):
        nonlocal timestamp
        timestamp += interval

        payload = data.split()
        if not payload or len(payload) > 8:
            raise ValueError("Invalid CAN payload.")

        rows.append({
            "timestamp": f"{timestamp:.6f}",
            "can_id": can_id,
            "dlc": len(payload),
            "data": " ".join(payload),
            "scenario": scenario,
            "label": label,
        })

    def source_frame(index):
        source = source_rows[index % len(source_rows)]
        return source["can_id"], source["data"]

    # Stage 1: Normal traffic (40 frames)
    for i in range(40):
        can_id, data = source_frame(i)
        add_frame(
            can_id, data,
            "normal_traffic", "normal", 0.020
        )

    # Stage 2: High-rate burst traffic (40 frames)
    burst_frames = []

    for i in range(40):
        can_id = f"0x{rng.choice(CAN_IDS):03X}"
        data = " ".join(
            f"{rng.randrange(256):02X}" for _ in range(8)
        )

        add_frame(
            can_id, data,
            "burst_traffic", "attack", 0.002
        )

        burst_frames.append((can_id, data))

    # Stage 3: Replay the first 10 burst frames four times
    for i in range(40):
        can_id, data = burst_frames[i % 10]

        add_frame(
            can_id, data,
            "replay_traffic", "attack", 0.010
        )

    # Stage 4: Recovery to normal traffic (40 frames)
    for i in range(40):
        can_id, data = source_frame(40 + i)

        add_frame(
            can_id, data,
            "recovery_traffic", "normal", 0.020
        )

    # Validate chronological order and expected labels.
    times = [float(row["timestamp"]) for row in rows]

    if not all(a < b for a, b in zip(times, times[1:])):
        raise SystemExit("FAIL: Timestamps are not chronological.")

    expected_counts = {
        "normal_traffic": 40,
        "burst_traffic": 40,
        "replay_traffic": 40,
        "recovery_traffic": 40,
    }

    for scenario, expected in expected_counts.items():
        actual = sum(row["scenario"] == scenario for row in rows)
        if actual != expected:
            raise SystemExit(f"FAIL: Unexpected count for {scenario}")

    replay_pairs = {
        (can_id, data) for can_id, data in burst_frames[:10]
    }

    replay_valid = all(
        (row["can_id"], row["data"]) in replay_pairs
        for row in rows
        if row["scenario"] == "replay_traffic"
    )

    if not replay_valid:
        raise SystemExit("FAIL: Replay payload validation failed.")

    # Exclusive creation: existing files cannot be overwritten.
    with OUTPUT.open("x", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    counts = {
        scenario: sum(row["scenario"] == scenario for row in rows)
        for scenario in expected_counts
    }

    documentation = f"""# Day 13: Combined Mixed-Traffic Scenario

## Scenario design

A single reproducible, time-ordered CAN traffic sequence is generated
using seed {SEED} and the existing normal traffic dataset.

The sequence contains four consecutive stages:

1. Normal traffic: 40 frames at 20 ms intervals.
2. Burst traffic: 40 frames at 2 ms intervals.
3. Replay traffic: 40 frames repeating 10 previously generated
   burst CAN ID/payload pairs.
4. Recovery traffic: 40 frames at 20 ms intervals.

## Expected behavior

- Normal traffic should carry the normal label.
- Burst traffic should carry the attack label.
- Replay traffic should carry the attack label.
- Recovery traffic should carry the normal label.
- Timestamps should increase strictly throughout the sequence.
- Replay messages should match previously generated CAN ID/payload pairs.

## Actual observations

- Total generated frames: {len(rows)}
- Normal frames: {counts['normal_traffic']}
- Burst frames: {counts['burst_traffic']}
- Replay frames: {counts['replay_traffic']}
- Recovery frames: {counts['recovery_traffic']}
- Timestamp ordering: PASS
- Replay payload validation: PASS
- Reproducibility seed: {SEED}

## Limitations

These results validate the generated dataset and its structure.
They do not represent predictions or accuracy measurements from the
production ML intrusion detector.

## Input and output

- Input: results/normal_traffic.csv
- Output: results/day13_mixed_scenario_traffic.csv
"""

    with DOCS.open("x", encoding="utf-8") as file:
        file.write(documentation)

    print("Day 13 generation successful.")
    print(f"Total frames: {len(rows)}")
    for scenario, count in counts.items():
        print(f"{scenario}: {count}")
    print("Timestamp ordering: PASS")
    print("Replay validation: PASS")
    print("CSV:", OUTPUT)
    print("Documentation:", DOCS)


if __name__ == "__main__":
    generate()
