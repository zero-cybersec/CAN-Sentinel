import argparse
import csv
import random

random.seed(42)

PERIODIC_SIGNALS = [
    (0x0C0, 8, 10,  1,  "Engine RPM"),
    (0x0D0, 8, 10,  1,  "Vehicle Speed"),
    (0x0D1, 8, 20,  2,  "Coolant Temp"),
    (0x1A0, 8, 20,  2,  "Wheel Speed FL"),
    (0x1A1, 8, 20,  2,  "Wheel Speed FR"),
    (0x1A2, 8, 20,  2,  "Wheel Speed RL"),
    (0x1A3, 8, 20,  2,  "Wheel Speed RR"),
    (0x2C0, 8, 50,  5,  "Throttle Position"),
    (0x2C1, 8, 50,  5,  "Brake Pressure"),
    (0x3B0, 8, 100, 10, "Gear Position"),
    (0x3B4, 8, 100, 10, "Fuel Level"),
    (0x4E0, 8, 200, 20, "Door Status"),
    (0x4E1, 8, 250, 25, "Light Status"),
]

SPORADIC_SIGNALS = [
    (0x5A0, 4, "Diagnostic Request"),
    (0x5A1, 4, "Diagnostic Response"),
    (0x6C0, 2, "Odometer"),
]

ALL_IDS = [s[0] for s in PERIODIC_SIGNALS] + [s[0] for s in SPORADIC_SIGNALS]


def payload_for(can_id: int) -> bytes:
    """Generate a plausible payload for a given CAN ID (slowly varying signal)."""
    if can_id == 0x0C0:  
        rpm = random.randint(800, 6000)
        raw = int(rpm / 0.25)
        return bytes([(raw >> 8) & 0xFF, raw & 0xFF, random.randint(0, 40), 0, 0, 0, 0, 0])
    if can_id == 0x0D0:  
        speed = random.randint(0, 120)
        raw = int(speed / 0.01)
        return bytes([(raw >> 8) & 0xFF, raw & 0xFF, random.randint(0, 20), 0, 0, 0, 0, 0])
    if can_id == 0x0D1:  
        return bytes([random.randint(70, 105), random.randint(0, 8), 0, 0, 0, 0, 0, 0])
    if 0x1A0 <= can_id <= 0x1A3:  
        return bytes([random.randint(0, 120), random.randint(0, 255), random.randint(0, 3), 0, 0, 0, 0, 0])
    if can_id == 0x2C0:  
        return bytes([random.randint(0, 100), random.randint(0, 50), 0, 0, 0, 0, 0, 0])
    if can_id == 0x2C1:  
        return bytes([random.randint(0, 200), random.randint(0, 30), 0, 0, 0, 0, 0, 0])
    if can_id == 0x3B0:  
        return bytes([random.choice([0, 1, 2, 3, 4, 5, 6]), 0, 0, 0, 0, 0, 0, 0])
    if can_id == 0x3B4:  
        return bytes([random.randint(5, 100), random.randint(0, 10), 0, 0, 0, 0, 0, 0])
    if can_id == 0x4E0:  
        return bytes([random.randint(0, 15), 0, 0, 0, 0, 0, 0, 0])
    if can_id == 0x4E1:  
        return bytes([random.randint(0, 63), 0, 0, 0, 0, 0, 0, 0])
    if can_id == 0x5A0: 
        return bytes([0x02, 0x01, random.randint(0, 0x0C), 0x55, 0x55, 0x55, 0x55, 0x55])
    if can_id == 0x5A1: 
        return bytes([0x06, 0x41, random.randint(0, 0x0C), random.randint(0, 0xFF),
                      0x55, 0x55, 0x55, 0x55])
    if can_id == 0x6C0:  
        odo = random.randint(10000, 250000)
        return bytes([(odo >> 8) & 0xFF, odo & 0xFF, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55])
    return bytes(random.randint(0, 255) for _ in range(8))


def generate(duration_s: int, attack_rate: float, out_path: str):
    rows = []
    t = 0.0 

    
    schedule = []
    for can_id, dlc, mean_ms, jitter, _desc in PERIODIC_SIGNALS:
        next_t = random.uniform(0, mean_ms)
        while next_t < duration_s * 1000:
            schedule.append((next_t, can_id, dlc))
            next_t += max(1.0, random.gauss(mean_ms, jitter))
    schedule.sort(key=lambda r: r[0])

    
    for can_id, dlc, _desc in SPORADIC_SIGNALS:
        n = int(duration_s * random.uniform(0.2, 1.0))
        for _ in range(n):
            schedule.append((random.uniform(0, duration_s * 1000), can_id, dlc))
    schedule.sort(key=lambda r: r[0])
  
    for ts, can_id, dlc in schedule:
        data = payload_for(can_id)
        rows.append([round(ts, 3), f"0x{can_id:03X}", dlc, *[f"{b:02X}" for b in data],
                     0, "normal"])

   
    n_attacks = max(1, int(duration_s * attack_rate / 10))
    for _ in range(n_attacks):
        attack_type = random.choice(["DoS", "Fuzzing", "Replay", "Spoofing"])
        start = random.uniform(0, duration_s * 900)
        length = random.uniform(50, 400)  
        t = start
        while t < start + length and t < duration_s * 1000:
            if attack_type == "DoS":
                can_id = random.choice([0x000, 0x0C0]) 
                dlc = 8
                data = bytes(random.randint(0, 255) for _ in range(dlc))
                gap = random.uniform(0.2, 0.8)
            elif attack_type == "Fuzzing":
                can_id = random.randint(0x000, 0x7FF)
                dlc = random.randint(0, 8)
                data = bytes(random.randint(0, 255) for _ in range(dlc)) \
                    + bytes(0x55 for _ in range(8 - dlc))
                gap = random.uniform(0.5, 2.0)
            elif attack_type == "Replay":
                can_id = random.choice(ALL_IDS)
                data = payload_for(can_id)
                dlc = 8
                gap = random.uniform(1.0, 3.0)
            else:  
                can_id = random.choice([0x0C0, 0x0D0])
                if can_id == 0x0C0: 
                    raw = int(random.randint(7000, 9000) / 0.25)
                else: 
                    raw = int(random.randint(200, 255) / 0.01)
                data = bytes([(raw >> 8) & 0xFF, raw & 0xFF, 0, 0, 0, 0, 0, 0])
                dlc = 8
                gap = random.uniform(8.0, 12.0)

            rows.append([round(t, 3), f"0x{can_id:03X}", dlc,
                         *[f"{b:02X}" for b in data], 1, attack_type])
            t += gap

    rows.sort(key=lambda r: r[0])

    header = ["timestamp", "can_id", "dlc",
              "b0", "b1", "b2", "b3", "b4", "b5", "b6", "b7",
              "attack", "attack_type"]
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

    n_att = sum(1 for r in rows if r[11] == 1)
    print(f"Wrote {len(rows)} frames to {out_path}")
    print(f"  normal : {len(rows) - n_att}")
    print(f"  attack : {n_att}")
    for at in ["DoS", "Fuzzing", "Replay", "Spoofing"]:
        c = sum(1 for r in rows if r[12] == at)
        print(f"    {at:<9}: {c}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Synthetic CAN bus dataset generator")
    ap.add_argument("--duration", type=int, default=60, help="duration in seconds")
    ap.add_argument("--attack-rate", type=float, default=8.0,
                    help="attack instances per 10 seconds (roughly)")
    ap.add_argument("--out", default="can_bus_dataset.csv", help="output CSV path")
    args = ap.parse_args()
    generate(args.duration, args.attack_rate, args.out)
