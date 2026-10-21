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
