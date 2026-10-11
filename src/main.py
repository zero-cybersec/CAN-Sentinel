print("CAN-Sentinel: Automotive ECU Intrusion Detection System")

can_messages = [
    {"can_id": 0x100, "dlc": 8},
    {"can_id": 0x101, "dlc": 8},
    {"can_id": 0x999, "dlc": 8},   # unknown ID
    {"can_id": 0x100, "dlc": 10},  # invalid DLC
]

allowed_ids = {0x100, 0x101, 0x102}

alerts = []

for message in can_messages:
    can_id = message["can_id"]
    dlc = message["dlc"]

    if can_id not in allowed_ids:
        print(f"WARNING: Unknown CAN ID: {hex(can_id)}")
        alerts.append(("unknown_id", can_id))

    if not isinstance(dlc, int) or not 0 <= dlc <= 8:
        print(f"WARNING: Invalid CAN data length: {dlc} (ID: {hex(can_id)})")
        alerts.append(("invalid_dlc", can_id))

print(f"Initial detection test completed. Total alerts: {len(alerts)}")
