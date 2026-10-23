
import csv
import random
from pathlib import Path

OUT = Path("results")
OUT.mkdir(exist_ok=True)
random.seed(2026)

def generate(filename, mode, rate):
    path = OUT / filename
    count = 10 * rate
    ids = ["0x100", "0x120", "0x200", "0x300"]

    with path.open("x", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["timestamp_s", "mode", "can_id", "data"]
        )
        writer.writeheader()
        for i in range(count):
            writer.writerow({
                "timestamp_s": round(i / rate, 6),
                "mode": mode,
                "can_id": random.choice(ids),
                "data": " ".join(
                    f"{random.randrange(256):02X}" for _ in range(8)
                )
            })
    print(f"{path}: {count} messages at {rate}/sec")

if __name__ == "__main__":
    generate("normal_traffic_new.csv", "normal_new", 25)
    generate("high_rate_traffic_new.csv", "high_rate_new", 250)
