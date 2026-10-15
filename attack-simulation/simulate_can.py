
import time
import csv
from pathlib import Path

def main():
    print("CAN-Sentinel Attack Simulation")
    print("Mode: Synthetic traffic planning")
    print("Target interface: vcan0")

    Path("logs").mkdir(exist_ok=True)

    with open(
        "logs/observations.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["time", "test_mode", "observation"])
        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            "setup",
            "Script saved; vcan0 test not yet run"
        ])

    print("Setup observation saved in logs/observations.csv")
    print("Next: verify vcan0 in a supported Linux environment.")

if __name__ == "__main__":
    main()
