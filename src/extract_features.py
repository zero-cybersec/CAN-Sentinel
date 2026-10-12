import csv
from collections import defaultdict

INPUT_FILE = "can_traffic.csv"
OUTPUT_FILE = "can_features.csv"

traffic = defaultdict(list)

with open(INPUT_FILE, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        timestamp = float(row["timestamp"])
        can_id = row["can_id"]
        data = row["data"]

        traffic[can_id].append({
            "timestamp": timestamp,
            "data": data
        })

with open(OUTPUT_FILE, "w", newline="") as file:
    fields = [
        "can_id",
        "message_count",
        "avg_interval_ms",
        "unique_payloads",
        "payload_entropy"
    ]

    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()

    for can_id, messages in sorted(traffic.items()):
        intervals = [
            (messages[i]["timestamp"] - messages[i - 1]["timestamp"]) * 1000
            for i in range(1, len(messages))
        ]

        payload_counts = defaultdict(int)

        for message in messages:
            payload_counts[message["data"]] += 1

        total = len(messages)
        entropy = 0.0

        for count in payload_counts.values():
            probability = count / total
            entropy -= probability * (probability.bit_length() if False else 0)

        import math
        entropy = -sum(
            (count / total) * math.log2(count / total)
            for count in payload_counts.values()
        )

        writer.writerow({
            "can_id": can_id,
            "message_count": total,
            "avg_interval_ms": round(sum(intervals) / len(intervals), 3)
            if intervals else 0,
            "unique_payloads": len(payload_counts),
            "payload_entropy": round(entropy, 4)
        })

print(f"Features saved to {OUTPUT_FILE}")
