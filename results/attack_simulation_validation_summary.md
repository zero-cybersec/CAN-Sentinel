# CAN-Sentinel
# Final Attack Simulation Validation Summary

**Contributor:** Zeeshan
**Branch:** zeeshan
**Date:** 05 November 2026
**Task:** Attack Simulation Evidence Finalization

## 1. Objective

Validate existing Normal, Burst, Replay and Recovery
CAN traffic datasets. Compare expected scenario labels
with observed outputs and document inconsistencies.

No new simulation code was developed.

## 2. Dataset Evidence

### Day 13 Mixed Scenario Dataset
File: results/day13_mixed_scenario_traffic.csv

Total records: 160

| Scenario | Records | Expected Label | Observed Label |
|---|---:|---|---|
| Normal | 40 | normal | normal |
| Burst | 40 | attack | attack |
| Replay | 40 | attack | attack |
| Recovery | 40 | normal | normal |

### Day 17 Mixed Traffic Dataset
File: results/day17_mixed_traffic.csv

Total records: 6500

| Scenario | Records | Expected Label | Observed Label |
|---|---:|---|---|
| Normal | 500 | normal | normal |
| Burst | 5000 | attack | attack |
| Replay | 500 | attack | attack |
| Recovery | 500 | normal | normal |

## 3. Scenario-wise Validation

### Normal Traffic
- Day 13: 40 records.
- Day 17: 500 records.
- Average interval: 20 ms.
- Labels consistently normal.
- Status: PASS.

### Burst Traffic
- Day 13: 40 records.
- Day 17: 5000 records.
- Average interval: 2 ms.
- Labels consistently attack.
- Status: PASS.

### Replay Traffic
- Day 13: 40 records.
- Average interval: 10 ms.
- 10 unique CAN ID/payload pairs.
- Maximum pair frequency: 4.

- Day 17: 500 records.
- Average interval: 20 ms.
- 3 unique CAN ID/payload pairs.
- Maximum pair frequency: 167.
- Repeated payload pattern observed.
- Status: PASS (dataset evidence).

### Recovery Traffic
- Day 13: 40 records.
- Day 17: 500 records.
- Average interval: 20 ms in both datasets.
- Labels consistently normal.
- Status: PASS.

## 4. Validation Checks

| Validation Check | Observed Result |
|---|---|
| Day 13 record count | 160 |
| Day 17 record count | 6500 |
| Timestamp ordering | PASS |
| Scenario label consistency | PASS |
| Label mismatches | 0 |
| Burst interval verification | PASS |
| Replay repetition evidence | PASS |
| Recovery normal labels | PASS |

## 5. Existing Edge Case Evidence

File: results/edge_case_validation.csv

Three existing edge-case records were inspected:
- Burst traffic
- Replay pattern
- Normal-to-high-rate transition

The baseline outputs matched the expected labels
in the recorded tests.

Important limitation:
The production detector output is marked NOT RUN.
These results must not be interpreted as production
ML detector accuracy or performance.

## 6. Findings and Limitations

1. Both mixed-scenario datasets contain all four scenarios.
2. No label mismatches were observed.
3. All timestamps were non-decreasing in the inspected datasets.
4. Replay repetition is evident in both datasets.
5. Recovery records have normal labels and 20 ms intervals.
6. All traffic is synthetic simulation evidence.
7. Production detector validation remains outside the
   confirmed evidence available for this report.

## 7. Final Conclusion

The existing Normal, Burst, Replay and Recovery datasets
passed the inspected structural, timestamp and label
consistency checks.

No simulation code redevelopment was required.

The final evidence supports dataset-level scenario
validation. Production detector accuracy is not claimed.

**Prepared by: Zeeshan**
**Project: CAN-Sentinel**

## 8. Day 19 Final Mixed-Traffic Review

### Scenario-wise Validation

| Scenario | Expected Label | Observed Dataset Label | Records | Mismatches |
|---|---|---|---:|---:|
| Normal | normal | normal | 500 | 0 |
| High-Rate / Burst | attack | attack | 5000 | 0 |
| Replay | attack | attack | 500 | 0 |
| Recovery | normal | normal | 500 | 0 |

### Traffic Validation Evidence

- Total records: 6500
- Timestamp ordering: PASS
- Scenario label consistency: PASS
- Total label mismatches: 0
- All four scenario groups verified.
- Existing datasets were preserved.
- No traffic regeneration was performed.

### Simulator Review

- attack_simulator.py generates synthetic Normal and High-Rate traffic.
- Its CSV output uses write mode and may overwrite existing files.
- attack-simulation/simulate_can.py records setup observations.
- Its logs/observations.csv also uses write mode.
- The vcan0 test is explicitly marked as not yet run.
- No confirmed critical simulator defect was established during this code review.
- Existing simulator files were not modified.

### Detection and Integration Limitations

The observed labels above are dataset ground-truth labels, not production ML detector predictions.

Production detector evaluation and final integration cross-validation are not independently confirmed by the available evidence.

No thresholds or model parameters were changed.

### Day 19 Conclusion

All four traffic scenarios passed the inspected dataset-level
structural, timestamp and label consistency checks.

Existing simulation outputs were preserved. No unnecessary
simulator redevelopment was performed.

Production detector accuracy and final integration are not
claimed without separate evaluation evidence.

Prepared by: Zeeshan
Branch: zeeshan

---

## Day 20 — Integration, Detector and Holdout Validation

### Validation Scope and Provenance

The integration and detector validation was independently executed
in an isolated temporary worktree based on
origin/zero-cybersec at commit b4f13e5.

The original zeeshan branch was not merged or modified during
that validation. Only this report is being updated on zeeshan.

### Automated Test Results

- Full test suite: 23 passed.
- Mixed-scenario tests: 8 passed.
- One test fixture in the isolated worktree was adapted because
  results/balanced_traffic_features.csv was unavailable.
- The adapted test used existing Normal and High-Rate traffic
  files and the integration feature extraction function.
- These results therefore apply to the adapted test suite,
  not an unchanged execution of the original test files.

### Model and Integration Validation

- The inspected model uses five features:
  message_count, avg_interval_ms, unique_can_ids,
  unique_payloads and payload_entropy.
- A 40-window model check produced 20 NORMAL and 20 ANOMALY
  predictions, with finite and non-constant anomaly scores.
- The integration pipeline processed 120 windows:
  - Normal traffic: 20 NORMAL predictions.
  - High-Rate traffic: 20 HIGH_RATE_SUSPECTED predictions.
  - Mixed traffic: 20 NORMAL, 20 HIGH_RATE_SUSPECTED,
    20 REPLAY_SUSPECTED and 20 NORMAL recovery predictions.

### Holdout Evaluation

The holdout evaluation used 6,500 synthetic traffic records
across Burst, Normal, Recovery and Replay scenarios.
The evaluation generated 80 windows, 20 per scenario.

Combined detector results across all 80 windows:

| Detector | TP | FP | TN | FN | Accuracy |
|---|---:|---:|---:|---:|---:|
| ML | 20 | 0 | 40 | 20 | 75% |
| Rate-based | 20 | 0 | 40 | 20 | 75% |
| Sequence-based | 20 | 0 | 40 | 20 | 75% |
| Hybrid | 40 | 0 | 40 | 0 | 100% |

The Hybrid result achieved 100% accuracy on this particular
synthetic holdout evaluation. This result must not be interpreted
as a guarantee of real-world detection performance.

### Observed Limitations

- The Sequence-based detector missed the Burst windows.
- ML and Rate-based detectors missed the Replay windows.
- The Hybrid detector combined the evaluated detector outputs
  using rate-based, sequence-based and ML priority logic.
- The replay sequence check uses a specific periodic repetition
  comparison and does not establish detection of every possible
  replay attack.
- All validation was performed on synthetic datasets.
- No live vehicle or physical CAN-bus validation was performed.
- No model parameters or detection thresholds were changed.
- The integration model and code inspected on the teammate branch
  have not been merged into zeeshan.
- Integration and holdout output files were generated separately
  in the temporary worktree to avoid overwriting existing results.

### Day 20 Conclusion

The isolated integration pipeline processed Normal, High-Rate,
mixed and recovery traffic successfully. The synthetic holdout
evaluation showed that the Hybrid detector correctly classified
all 80 evaluated windows in this run.

The individual detector limitations and synthetic-only scope
are documented above. These results establish controlled
offline validation, not production or real-vehicle validation.

Prepared by: Zeeshan
Branch: zeeshan
