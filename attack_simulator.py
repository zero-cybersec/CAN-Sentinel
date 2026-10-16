
import csv
import random
from pathlib import Path
from collections import Counter

# Synthetic CAN traffic simulator
OUTPUT_DIR = Path("results")
OUTPUT_DIR.mkdir(exist_ok=True)

DURATION_SECONDS = 10
NORMAL_RATE = 50       # simulated messages per second
HIGH_RATE = 500        # simulated messages per second
RANDOM_SEED = 42

random.seed(RANDOM_SEED)


def generate_traffic(mode, rate):
    messages = []
    total = DURATION_SECONDS * rate

    for i in range(total):
        timestamp = i / rate

        # Generate synthetic CAN identifiers and 8-byte payloads
        can_id = random.choice([0x100, 0x120, 0x200, 0x300])
        data = " ".join(
            f"{random.randint(0, 255):02X}" for _ in range(8)
        )

        messages.append({
            "timestamp_s": round(timestamp, 6),
            "mode": mode,
            "can_id": f"0x{can_id:03X}",
            "data": data
        })

    return messages


def save_csv(filename, messages):
    path = OUTPUT_DIR / filename

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp_s", "mode", "can_id", "data"
            ]
        )
        writer.writeheader()
        writer.writerows(messages)

    return path


def summarize(mode, messages):
    count = len(messages)
    rate = count / DURATION_SECONDS
    ids = Counter(message["can_id"] for message in messages)

    # This is a demonstration threshold, not a real CAN standard.
    status = (
        "HIGH-RATE PATTERN"
        if rate > 100
        else "NORMAL-RATE PATTERN"
    )

    return {
        "mode": mode,
        "duration_seconds": DURATION_SECONDS,
        "message_count": count,
        "messages_per_second": round(rate, 2),
        "unique_can_ids": len(ids),
        "most_common_can_id": ids.most_common(1)[0][0],
        "simulator_observation": status
    }


def main():
    normal = generate_traffic("normal", NORMAL_RATE)
    high = generate_traffic("simulated_high_rate", HIGH_RATE)

    save_csv("normal_traffic.csv", normal)
    save_csv("high_rate_traffic.csv", high)

    summaries = [
        summarize("normal", normal),
        summarize("simulated_high_rate", high)
    ]

    with (OUTPUT_DIR / "summary.csv").open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=list(summaries[0].keys())
        )
        writer.writeheader()
        writer.writerows(summaries)

    with (OUTPUT_DIR / "observations.txt").open(
        "w", encoding="utf-8"
    ) as file:
        for result in summaries:
            file.write(f"Test: {result['mode']}\n")
            file.write(
                f"Message count: {result['message_count']}\n"
            )
            file.write(
                f"Messages/second: "
                f"{result['messages_per_second']}\n"
            )
            file.write(
                f"Observation: "
                f"{result['simulator_observation']}\n\n"
            )

    print("=== SYNTHETIC CAN TRAFFIC TEST RESULTS ===")
    for result in summaries:
        print(f"\nTest: {result['mode']}")
        print(f"Messages: {result['message_count']}")
        print(f"Rate: {result['messages_per_second']} messages/sec")
        print(f"Observation: {result['simulator_observation']}")

    print(f"\nFiles saved in: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
