import can
import csv
import time

bus = can.Bus(interface="socketcan", channel="vcan0")

filename = "can_traffic.csv"

print(f"Logging CAN traffic to {filename}. Press Ctrl+C to stop.")

try:
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "can_id", "dlc", "data"])

        while True:
            msg = bus.recv(timeout=1.0)

            if msg is not None:
                timestamp = time.time()
                data = msg.data.hex().upper()

                writer.writerow([
                    timestamp,
                    hex(msg.arbitration_id),
                    msg.dlc,
                    data
                ])

                file.flush()
                print(f"ID: {hex(msg.arbitration_id)} | Data: {data}")

except KeyboardInterrupt:
    print("\nLogging stopped.")

finally:
    bus.shutdown()
