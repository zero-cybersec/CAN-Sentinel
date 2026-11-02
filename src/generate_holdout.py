
import csv
from pathlib import Path

OUTPUT = Path("results/holdout_traffic.csv")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

FIELDS = ["timestamp_s", "can_id", "data", "scenario", "label"]

SCENARIOS = [
    ("Normal", 20, "normal"),
    ("Burst", 2, "attack"),
    ("Replay", 20, "attack"),
    ("Recovery", 20, "normal"),
]

all_frames = []

for scenario, interval_ms, label in SCENARIOS:
    count = 10000 // interval_ms

    replay_sequence = [
        ("0x120", "1122334455667788"),
        ("0x121", "AABBCCDDEEFF0011"),
        ("0x122", "1234567890ABCDEF"),
    ]

    for i in range(count):
        if scenario == "Replay":
            can_id, data = replay_sequence[i % 3]
        else:
            can_id = hex(0x200 + (i % 8))
            data = f"{i % 256:02X}11223344556677"

        all_frames.append({
            "timestamp_s": round(i * interval_ms / 1000, 3),
            "can_id": can_id,
            "data": data,
            "scenario": scenario,
            "label": label,
        })

with OUTPUT.open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(all_frames)

print(f"Generated: {OUTPUT}")
print(f"Total frames: {len(all_frames)}")
