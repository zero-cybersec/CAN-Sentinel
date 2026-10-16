import argparse, csv, random, os, sys
from collections import Counter


def generate_sample(path, n=200, seed=42):
    """Generate synthetic CAN bus feature rows with labels and mock predictions."""
    random.seed(seed)
    rows = []
    for i in range(n):
        attack = random.random() < 0.3
        can_id = random.choice(["0x000", "0x7DF"]) if attack else random.choice(
            ["0x0C1", "0x1A0", "0x2B0", "0x316", "0x43F"])
        dlc = 8
        freq = round(random.uniform(800, 1500) if attack else random.uniform(10, 120), 2)
        entropy = round(random.uniform(0.1, 0.4) if attack else random.uniform(0.5, 0.95), 3)
        label = "attack" if attack else "normal"
        pred = label if random.random() < 0.9 else ("normal" if attack else "attack")
        rows.append({"sample_id": i, "timestamp": round(i * 0.01, 3), "can_id": can_id,
                     "dlc": dlc, "msg_frequency_hz": freq, "payload_entropy": entropy,
                     "label": label, "prediction": pred})
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    return path


def evaluate(rows, label_col, pred_col, positive, strict=False):
    """Compare predictions vs expected labels. Returns (detailed_rows, summary)."""
    c = Counter()
    out = []
    skipped = 0
    for idx, r in enumerate(rows, start=1):
        y = str(r.get(label_col, "")).strip()
        p = str(r.get(pred_col, "")).strip()
        if not y or not p:
            if strict:
                raise SystemExit(f"Row {idx}: blank label or prediction (strict mode)")
            skipped += 1
            continue
        correct = y == p
        if p == positive and y == positive:
            kind = "TP"
        elif p == positive and y != positive:
            kind = "FP"
        elif p != positive and y == positive:
            kind = "FN"
        else:
            kind = "TN"
        c["correct" if correct else "incorrect"] += 1
        c[kind] += 1
        out.append({**r, "is_correct": correct, "outcome": kind})
    total = len(out)
    tp, fp, fn, tn = c["TP"], c["FP"], c["FN"], c["TN"]
    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn) if tp + fn else 0
    summary = {"total": total, "skipped": skipped,
               "correct": c["correct"], "incorrect": c["incorrect"],
               "true_positives": tp, "false_positives": fp,
               "false_negatives": fn, "true_negatives": tn,
               "accuracy": round(c["correct"] / total, 4) if total else 0,
               "precision": round(prec, 4), "recall": round(rec, 4),
               "f1": round(2 * prec * rec / (prec + rec), 4) if prec + rec else 0,
               "false_positive_rate": round(fp / (fp + tn), 4) if fp + tn else 0}
    return out, summary


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def print_confusion_matrix(s):
    print("\nConfusion matrix (positive = attack):")
    print(f"              predicted attack   predicted normal")
    print(f"actual attack {s['true_positives']:>16} {s['false_negatives']:>18}")
    print(f"actual normal {s['false_positives']:>16} {s['true_negatives']:>18}\n")


def main():
    ap = argparse.ArgumentParser(description="CAN bus ML evaluation")
    ap.add_argument("--input")
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("--label-col", default="label")
    ap.add_argument("--pred-col", default="prediction")
    ap.add_argument("--positive", default="attack", help="positive (anomaly) class value")
    ap.add_argument("--out-dir", default="results")
    ap.add_argument("--strict", action="store_true", help="fail on blank labels/predictions")
    a = ap.parse_args()

    if a.sample or not a.input or not os.path.exists(a.input):
        if not a.sample:
            print("Input not found -> using sample data")
        a.input = generate_sample("sample_can_features.csv")

    with open(a.input) as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit("Input CSV has no data rows")
    for col in (a.label_col, a.pred_col):
        if col not in rows[0]:
            raise SystemExit(f"Missing column: {col} (available: {', '.join(rows[0].keys())})")

    detailed, summary = evaluate(rows, a.label_col, a.pred_col, a.positive, strict=a.strict)
    os.makedirs(a.out_dir, exist_ok=True)
    write_csv(os.path.join(a.out_dir, "evaluation_detailed.csv"), detailed)
    write_csv(os.path.join(a.out_dir, "evaluation_summary.csv"), [summary])

    for k, v in summary.items():
        print(f"{k:>20}: {v}")
    print_confusion_matrix(summary)
    print(f"Saved results to {a.out_dir}/")
    if a.sample:
        print("NOTE: these are synthetic sample results, not real model performance.")


if __name__ == "__main__":
    main()
