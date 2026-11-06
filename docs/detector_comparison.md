# CAN-Sentinel Detector Comparison

## Objective
Compare the existing Isolation Forest output with the experimental rule-based baseline on the available synthetic CAN traffic datasets.

## Observed Results

| Dataset | Windows | Rule-based flagged | ML ANOMALY | ML NORMAL |
|---|---:|---:|---:|---:|
| Normal traffic | 8 | 0 | 2 | 6 |
| High-rate traffic | 52 | 52 | 0 | 52 |
| Total | 60 | 52 | 2 | 58 |

## Findings
- The rule-based baseline flagged all 52 evaluated high-rate windows and did not flag the 8 normal windows.
- The Isolation Forest marked all 52 high-rate windows NORMAL and marked 2 normal windows ANOMALY.
- The ML model requires further investigation; its current output does not demonstrate high-rate attack detection.

## Limitations
- These results use small synthetic datasets and do not establish real-world detection accuracy.
- The 30 ms baseline threshold was selected after examining the same datasets, so these results are not an independent evaluation.
- Validate the threshold on separate unseen traffic and more varied normal scenarios before drawing broader conclusions.
- The rule-based baseline and ML model are separate detectors; the baseline result does not mean the ML model has been fixed.

## Hybrid Detection Results — 22 October 2026

### Test results

| Dataset | Windows | Hybrid prediction | Original ML anomalies |
|---|---:|---|---:|
| High-rate synthetic traffic | 52 | 52 HIGH_RATE_SUSPECTED | 0 |
| Normal synthetic traffic | 8 | 0 HIGH_RATE_SUSPECTED | 2 |

The provisional rate rule flags a window when `avg_interval_ms < 30.0`.
The original model output is preserved in `ml_prediction`, and the original
model score remains in `anomaly_score`. The `prediction` column now represents
the hybrid output: the rate rule overrides the final label for windows below
the threshold; otherwise the original ML label is retained.

### Interpretation and limitations

On these synthetic test datasets, the rate rule flagged all 52 high-rate
windows and none of the 8 normal windows. The original ML model labelled all
52 high-rate windows NORMAL and labelled 2 normal windows ANOMALY.

These results do not establish real-world detection performance. The 30 ms
threshold is provisional and was selected using the synthetic datasets; it
must be validated on independent traffic before any production use. The
hybrid rule supplements the ML model and does not fix the underlying ML
model's failure to detect the tested high-rate traffic.

## Verification Log — 23 October 2026

- Rule-baseline tests: 4 passed.
- Integration test: completed successfully and regenerated `results/integration_results.csv`.
- Hybrid output: 52 high-rate windows were labelled `HIGH_RATE_SUSPECTED`.
- Normal traffic output: 6 windows were labelled `NORMAL` and 2 were labelled `ANOMALY` by the hybrid output.
- The original ML predictions and anomaly scores remain available in the results CSV.
- These are repeat-run verification results on the existing synthetic datasets, not independent validation or evidence of improved ML performance.

## Latest Detector Evaluation — 28 October 2026

### Evaluation Results

| Detector | Windows | TP | FP | TN | FN | Precision | Recall | F1 | Accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ML | 52 | 48 | 0 | 4 | 0 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Rate-based | 52 | 48 | 0 | 4 | 0 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Hybrid | 52 | 48 | 0 | 4 | 0 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

### Interpretation and Limitations

- All three detectors correctly classified the 48 high-rate and 4 normal evaluated windows in the current synthetic test.
- Integration results are saved in `results/integration_results.csv`.
- Evaluation metrics are saved in `results/detector_evaluation_metrics.csv`.
- These results use synthetic datasets and filename-derived ground-truth labels. They do not establish real-world detection accuracy or independent generalization.
- Further validation requires independent datasets containing varied normal traffic and attack scenarios.
