import csv
import math
from collections import defaultdict

INPUT_FILE = "can_traffic.csv"
OUTPUT_FILE = "can_features.csv"
WINDOW_SIZE = 100

traffic = defaultdict(list)

with open(INPUT_FILE, "r", newline="") as file:
    for row in csv.DictReader(file):
        traffic[row["can_id"]].append({
            "timestamp": float(row["timestamp"]),
            "data": row["data"]
        })

fields = [
    "can_id",
    "message_count",
    "avg_interval_ms",
    "unique_payloads",
    "payload_entropy"
]

with open(OUTPUT_FILE, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()

    for can_id, messages in sorted(traffic.items()):
        for start in range(0, len(messages), WINDOW_SIZE):
            window = messages[start:start + WINDOW_SIZE]

            if len(window) < 10:
                continue

            intervals = [
                (window[i]["timestamp"] -
                 window[i - 1]["timestamp"]) * 1000
                for i in range(1, len(window))
            ]

            counts = defaultdict(int)
            for message in window:
                counts[message["data"]] += 1

            total = len(window)
            entropy = -sum(
                (count / total) * math.log2(count / total)
                for count in counts.values()
            )

            writer.writerow({
                "can_id": can_id,
                "message_count": total,
                "avg_interval_ms": round(
                    sum(intervals) / len(intervals), 3
                ),
                "unique_payloads": len(counts),
                "payload_entropy": round(entropy, 4)
            })

print(f"Features saved to {OUTPUT_FILE}")
