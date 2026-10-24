
import csv
import random
from pathlib import Path

SEED = 11
OUTPUT = Path("results/day11_edge_case_traffic.csv")

FIELDS = [
    "timestamp",
    "can_id",
    "dlc",
    "data",
    "scenario",
    "label",
]


def make_frame(rng, timestamp, scenario, label):
    can_id = rng.choice([0x100, 0x200, 0x300, 0x400])
    payload = [rng.randrange(256) for _ in range(8)]

    return {
        "timestamp": f"{timestamp:.6f}",
        "can_id": f"0x{can_id:03X}",
        "dlc": 8,
        "data": " ".join(f"{b:02X}" for b in payload),
        "scenario": scenario,
        "label": label,
    }


def generate():
    rng = random.Random(SEED)
    rows = []
    timestamp = 0.0

    # Scenario 1: short burst of high-rate traffic
    for i in range(100):
        timestamp += 0.002
        rows.append(
            make_frame(rng, timestamp, "burst_traffic", "attack")
        )

    # Scenario 2: repeated payload / replay-like pattern
    replay_payload = "DE AD BE EF 01 02 03 04"
    for i in range(100):
        timestamp += 0.01
        row = make_frame(rng, timestamp, "replay_pattern", "attack")
        row["can_id"] = "0x100"
        row["data"] = replay_payload
        rows.append(row)

    # Scenario 3: normal traffic transitions to high rate
    for i in range(100):
        timestamp += 0.02
        rows.append(
            make_frame(rng, timestamp, "normal_to_high_rate", "normal")
        )

    for i in range(100):
        timestamp += 0.002
        rows.append(
            make_frame(
                rng, timestamp, "normal_to_high_rate", "attack"
            )
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    # Exclusive creation prevents overwriting an existing dataset.
    with OUTPUT.open("x", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {OUTPUT}")
    print("Scenarios: burst_traffic, replay_pattern, normal_to_high_rate")


if __name__ == "__main__":
    generate()
