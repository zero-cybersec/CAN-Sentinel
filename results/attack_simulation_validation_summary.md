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
