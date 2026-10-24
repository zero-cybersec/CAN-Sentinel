import math
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

WINDOW_S = 1.0

FEATURES = [
    "message_count",
    "avg_interval_ms",
    "unique_payloads",
    "payload_entropy",
]


def shannon_entropy(values: list[str]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    n = len(values)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def extract(raw_csv: Path, source_label: str | None = None) -> pd.DataFrame:
    df = pd.read_csv(raw_csv)
    df["timestamp_s"] = pd.to_numeric(df["timestamp_s"], errors="raise")
    df["window"] = (df["timestamp_s"] // WINDOW_S).astype(int) if WINDOW_S else 0

    rows = []
    for (win, cid), g in df.groupby(["window", "can_id"], sort=True):
        intervals = g["timestamp_s"].diff().dropna() * 1000.0
        payloads = g["data"].astype(str).str.strip().tolist()
        rows.append(
            {
                "source": source_label or raw_csv.stem,
                "window": int(win),
                "can_id": cid,
                "message_count": len(g),
                "avg_interval_ms": round(float(intervals.mean()), 3)
                if len(intervals)
                else 0.0,
                "unique_payloads": g["data"].nunique(),
                "payload_entropy": round(shannon_entropy(payloads), 4),
                "label": str(g["mode"].iloc[0]),
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python extract_features.py <raw_can.csv> [...]")
    out_frames = [extract(Path(p)) for p in sys.argv[1:]]
    out = pd.concat(out_frames, ignore_index=True)
    out.to_csv("can_features.csv", index=False)
    print(f"Wrote can_features.csv: {len(out)} rows")
    print(out.groupby("label")[FEATURES].mean().round(2))
