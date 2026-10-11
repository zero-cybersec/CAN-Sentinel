import argparse
import csv
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

LINE_RE = re.compile(
    r"^\((?P<ts>\d+\.\d+)\)\s+(?P<iface>\S+)\s+(?P<id>[0-9A-Fa-f]+)#(?P<data>[0-9A-Fa-f]*)\s*$"
)

HEADER = ["timestamp", "delta_t", "iface", "can_id", "dlc", "data_hex"] + [
    f"b{i}" for i in range(8)
]


def parse_line(line):
    """Return a dict for a candump -L line, or None if it doesn't match."""
    m = LINE_RE.match(line.strip())
    if not m:
        return None
    data_hex = m.group("data").upper()
    if len(data_hex) % 2:          # malformed payload
        return None
    payload = [int(data_hex[i:i + 2], 16) for i in range(0, len(data_hex), 2)]
    return {
        "timestamp": float(m.group("ts")),
        "iface": m.group("iface"),
        "can_id": f"0x{int(m.group('id'), 16):03X}",
        "dlc": len(payload),
        "data_hex": data_hex,
        "bytes": payload,
    }


def lines_from_source(args):
    """Yield raw text lines from stdin, a file, or a live candump process."""
    if args.stdin:
        yield from sys.stdin
    elif args.infile:
        with open(args.infile, "r") as fh:
            yield from fh
    else:
        proc = subprocess.Popen(
            ["candump", "-L", args.iface],
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        try:
            for line in proc.stdout:
                yield line
        finally:
            proc.terminate()


def main():
    ap = argparse.ArgumentParser(description="Log SocketCAN traffic to CSV")
    ap.add_argument("--iface", default="vcan0", help="CAN interface (live mode)")
    ap.add_argument("--out", default="data/normal_traffic.csv", help="output CSV path")
    ap.add_argument("--duration", type=float, default=0.0,
                    help="stop after N seconds (0 = until Ctrl+C / EOF)")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--stdin", action="store_true", help="read candump -L from stdin")
    src.add_argument("--infile", help="read candump -L log from a file")
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    stop = {"flag": False}
    signal.signal(signal.SIGINT, lambda *_: stop.update(flag=True))

    last_seen = {}     # can_id -> last timestamp
    count = 0
    skipped = 0
    t0 = time.monotonic()

    with open(out_path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(HEADER)

        for raw in lines_from_source(args):
            if stop["flag"]:
                break
            if args.duration and (time.monotonic() - t0) >= args.duration:
                break

            frame = parse_line(raw)
            if frame is None:
                skipped += 1
                continue

            prev = last_seen.get(frame["can_id"])
            delta = round(frame["timestamp"] - prev, 6) if prev is not None else 0.0
            last_seen[frame["can_id"]] = frame["timestamp"]

            padded = frame["bytes"] + [0] * (8 - len(frame["bytes"]))
            writer.writerow([
                f"{frame['timestamp']:.6f}", delta, frame["iface"], frame["can_id"],
                frame["dlc"], frame["data_hex"], *padded,
            ])
            count += 1
            if count % 1000 == 0:
                fh.flush()
                print(f"[logger] {count} frames...", file=sys.stderr)

    print(f"[logger] Done. {count} frames saved to {out_path} "
          f"({skipped} unparsable lines skipped).", file=sys.stderr)


if __name__ == "__main__":
    main()
