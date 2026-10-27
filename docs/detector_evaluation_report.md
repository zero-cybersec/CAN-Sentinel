# CAN-Sentinel — Detector Evaluation Report

**Contributor:** Avinash
**Role:** Team Lead & Integration
**Date:** 26 October 2026

## 1. Objective

Evaluate and compare the existing Machine Learning (ML), rate-based, and hybrid CAN traffic detectors using the project's available synthetic traffic datasets.

## 2. Evaluation Method

The evaluation script, `src/evaluate_detectors.py`, calculates the confusion-matrix values and standard classification metrics for each detector.

- **TP (True Positive):** An anomalous window correctly identified as anomalous.
- **FP (False Positive):** A normal window incorrectly flagged as anomalous.
- **TN (True Negative):** A normal window correctly identified as normal.
- **FN (False Negative):** An anomalous window incorrectly identified as normal.
- **Precision:** TP / (TP + FP)
- **Recall:** TP / (TP + FN)
- **F1-score:** Harmonic mean of precision and recall.
- **Accuracy:** (TP + TN) / total evaluated windows.

The evaluation covered 60 windows: 52 high-rate traffic windows and 8 normal traffic windows. Ground-truth labels were inferred from the synthetic dataset filenames.

## 3. Results

| Detector | Windows | TP | FP | TN | FN | Precision | Recall | F1-score | Accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ML | 60 | 0 | 2 | 6 | 52 | 0.0000 | 0.0000 | 0.0000 | 0.1000 |
| Rate-based | 60 | 52 | 0 | 8 | 0 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Hybrid | 60 | 52 | 2 | 6 | 0 | 0.9630 | 1.0000 | 0.9811 | 0.9667 |

## 4. Observations

- The ML detector missed all 52 high-rate windows in this evaluation and produced two false positives among normal windows.
- The rate-based detector identified all 52 high-rate windows and did not flag any of the eight normal windows in these datasets.
- The hybrid detector identified all 52 high-rate windows but also produced two false positives among normal windows.
- The hybrid output retains the original ML prediction and anomaly score alongside the rate-based result.

## 5. Limitations

- These results come from synthetic datasets and do not establish real-world CAN intrusion-detection performance.
- The ground-truth labels were inferred from filenames rather than independently verified labels.
- The 30 ms rate threshold was selected using the same synthetic datasets evaluated here; these results are not independent validation.
- The ML model was trained on only six feature samples, so its performance may be affected by limited training data and differences between training and test traffic.
- Additional datasets, independently labelled traffic, and edge-case testing are needed before drawing broader conclusions.

## 6. Tests and Artifacts

- Evaluation script: `src/evaluate_detectors.py`
- Metrics output: `results/detector_evaluation_metrics.csv`
- Evaluation tests: `tests/test_evaluate_detectors.py`
- Rule-baseline tests: `tests/test_rule_baseline.py`

Previously recorded test results were 5/5 evaluation tests passed and 4/4 rule-baseline tests passed, for a combined total of 9/9 tests.

## 7. Conclusion

On the current synthetic datasets, the rate-based detector achieved the strongest measured results. The hybrid detector also detected all tested high-rate windows, with two false positives on normal traffic. The ML detector requires further investigation and better representative training data. These findings are preliminary and should not be treated as proof of production readiness.
