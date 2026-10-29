# Day 12: Edge-Case Validation Findings

## Scope
Validate the existing Day 11 synthetic CAN traffic dataset without
regenerating or overwriting it.

## Dataset validation results
- Dataset: `results/day11_edge_case_traffic.csv`
- Total data rows: 400
- Expected headers present: yes
- Missing values: 0
- Invalid DLC values: 0
- Timestamps strictly increasing: yes
- Burst scenario: 100 rows, all labelled attack; interval 0.002 seconds
- Replay scenario: 100 rows, same CAN ID and payload; all labelled attack
- Transition scenario: 100 normal rows followed by 100 attack rows

These checks validate dataset structure and scenario construction,
not intrusion-detector performance.

## Scenario findings

### 1. burst_traffic
The dataset contains 100 attack-labelled frames at 0.002-second
intervals. This is a synthetic burst pattern. Detector execution
has not been verified.

### 2. replay_pattern
The dataset contains 100 frames with the same CAN ID and payload.
All rows are labelled attack. This validates the repeated-payload
pattern, not successful replay detection by a model.

### 3. normal_to_high_rate
The dataset contains 100 normal-labelled frames followed by 100
attack-labelled frames. The transition label ordering is correct.
Actual transition detection has not been tested.

## Limitations
- `attack_simulator.py` generates normal and high-rate synthetic
  traffic and reports a rate-based observation; it is not an
  intrusion detector for these three scenarios.
- `compare_traffic.py` compares existing simulation metrics and
  requires `traffic_results.json`.
- `attack-simulation/simulate_can.py` records setup status and
  says the vcan0 test has not yet been run.
- No actual detector output was available during this validation.
- Detector output counts and detection pass/fail remain NOT RUN.

## Conclusion
Dataset structure, scenario checks, and reproducibility test passed.
Overall completion is pending actual detector testing.
No claim of successful attack detection is made.


## Reproducibility test
- Result: PASS
- Generator exit code: 0
- Generated dataset: 400 rows
- Original dataset unchanged: yes
- Regenerated CSV byte-for-byte identical to original: yes
- Method: ran the generator in a temporary working directory.


## Day 12 baseline rule-test results

The existing Day 11 CSV was tested without regenerating it.
These are results from a simple validation baseline, NOT the
project's production intrusion detector.

### burst_traffic — PASS
- Input rows: 100
- Baseline flagged rows: 100
- Production detector output: NOT RUN
- Observation: Baseline flagged 100 frames; labels matched: True. Production detector NOT RUN.

### replay_pattern — PASS
- Input rows: 100
- Baseline flagged rows: 100
- Production detector output: NOT RUN
- Observation: 1 unique CAN ID/payload pair(s); baseline flagged 100 frames; labels matched: True. Production detector NOT RUN.

### normal_to_high_rate — PASS
- Input rows: 200
- Baseline flagged rows: 100
- Production detector output: NOT RUN
- Observation: Baseline flagged 100 frames; labels matched: True. Production detector NOT RUN.

### Limitation
Baseline PASS means this simple rule reproduced the expected labels on this dataset only. It does not demonstrate production model accuracy, generalization, or real-vehicle detection.
