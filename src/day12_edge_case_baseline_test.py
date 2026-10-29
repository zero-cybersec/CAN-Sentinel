import csv
from pathlib import Path

DATA = Path("results/day11_edge_case_traffic.csv")
REPORT = Path("results/edge_case_validation.csv")
FINDINGS = Path("docs/edge_case_findings.md")

with DATA.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    required = {"timestamp", "can_id", "dlc", "data", "scenario", "label"}
    if not required.issubset(reader.fieldnames or []):
        raise SystemExit("FAIL: Required CSV columns are missing.")
    rows = list(reader)

groups = {}
for row in rows:
    groups.setdefault(row["scenario"], []).append(row)

expected_counts = {
    "burst_traffic": 100,
    "replay_pattern": 100,
    "normal_to_high_rate": 200,
}
if set(groups) != set(expected_counts):
    raise SystemExit(f"FAIL: Unexpected scenario names: {list(groups)}")

for name, count in expected_counts.items():
    if len(groups[name]) != count:
        raise SystemExit(f"FAIL: {name} has {len(groups[name])} rows; expected {count}.")

results = []

# Baseline rule 1: identify frames arriving at intervals <= 2.1 ms.
burst = groups["burst_traffic"]
burst_predictions = []
previous = 0.0
for row in burst:
    current = float(row["timestamp"])
    burst_predictions.append((current - previous) <= 0.0021)
    previous = current

burst_expected = [row["label"] == "attack" for row in burst]
burst_ok = burst_predictions == burst_expected
results.append({
    "scenario": "burst_traffic",
    "input_count": len(burst),
    "detector_output_count": "NOT RUN",
    "baseline_output_count": sum(burst_predictions),
    "expected_behavior": "Flag high-rate burst frames as attack",
    "observed_result": (
        f"Baseline flagged {sum(burst_predictions)} frames; "
        f"labels matched: {burst_ok}. Production detector NOT RUN."
    ),
    "status": "PASS" if burst_ok else "FAIL",
})

# Baseline rule 2: flag CAN ID/payload pairs repeated in the scenario.
replay = groups["replay_pattern"]
pair_counts = {}
for row in replay:
    pair = (row["can_id"], row["data"])
    pair_counts[pair] = pair_counts.get(pair, 0) + 1

replay_predictions = [
    pair_counts[(row["can_id"], row["data"])] >= 2
    for row in replay
]
replay_expected = [row["label"] == "attack" for row in replay]
replay_ok = replay_predictions == replay_expected
results.append({
    "scenario": "replay_pattern",
    "input_count": len(replay),
    "detector_output_count": "NOT RUN",
    "baseline_output_count": sum(replay_predictions),
    "expected_behavior": "Flag repeated CAN ID/payload pattern as attack",
    "observed_result": (
        f"{len(pair_counts)} unique CAN ID/payload pair(s); "
        f"baseline flagged {sum(replay_predictions)} frames; "
        f"labels matched: {replay_ok}. Production detector NOT RUN."
    ),
    "status": "PASS" if replay_ok else "FAIL",
})

# Baseline rule 3: identify the high-rate portion of the transition.
transition = groups["normal_to_high_rate"]
transition_predictions = []
previous = None
for row in transition:
    current = float(row["timestamp"])
    if previous is None:
        interval = 0.020  # expected normal-rate interval for first frame
    else:
        interval = current - previous
    transition_predictions.append(interval <= 0.0021)
    previous = current

transition_expected = [row["label"] == "attack" for row in transition]
transition_ok = transition_predictions == transition_expected
results.append({
    "scenario": "normal_to_high_rate",
    "input_count": len(transition),
    "detector_output_count": "NOT RUN",
    "baseline_output_count": sum(transition_predictions),
    "expected_behavior": "Flag high-rate frames after normal traffic",
    "observed_result": (
        f"Baseline flagged {sum(transition_predictions)} frames; "
        f"labels matched: {transition_ok}. Production detector NOT RUN."
    ),
    "status": "PASS" if transition_ok else "FAIL",
})

fields = [
    "scenario", "input_count", "detector_output_count",
    "baseline_output_count", "expected_behavior",
    "observed_result", "status",
]
with REPORT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(results)

section = """
## Day 12 baseline rule-test results

The existing Day 11 CSV was tested without regenerating it.
These are results from a simple validation baseline, NOT the
project's production intrusion detector.

"""
for result in results:
    section += (
        f"### {result['scenario']} — {result['status']}\n"
        f"- Input rows: {result['input_count']}\n"
        f"- Baseline flagged rows: {result['baseline_output_count']}\n"
        f"- Production detector output: NOT RUN\n"
        f"- Observation: {result['observed_result']}\n\n"
    )

section += (
    "### Limitation\n"
    "Baseline PASS means this simple rule reproduced the expected "
    "labels on this dataset only. It does not demonstrate production "
    "model accuracy, generalization, or real-vehicle detection.\n"
)

existing = FINDINGS.read_text(encoding="utf-8")
marker = "## Day 12 baseline rule-test results"
if marker not in existing:
    FINDINGS.write_text(existing.rstrip() + "\n\n" + section, encoding="utf-8")

print("Baseline test results:")
for result in results:
    print(
        f"{result['scenario']}: {result['status']}; "
        f"input={result['input_count']}; "
        f"baseline flagged={result['baseline_output_count']}; "
        f"production detector={result['detector_output_count']}"
    )
print("Updated:", REPORT)
print("Updated:", FINDINGS)
