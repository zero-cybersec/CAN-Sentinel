# CAN Sentinel ML Model and Preprocessing: Final Review

**Review date:** 6 November 2026  
**Scope:** Final review of the checked-in training and inference pipeline, ordered features, existing evaluation records, and validation limitations. No retraining, parameter changes, or threshold changes were made.

## Executive conclusion

The current CAN Sentinel project’s checked-in training and inference code are internally consistent: both use the same feature-extraction function, the same ordered eight-feature contract, and the same fixed 500 ms window protocol. The checked-in artifact is a statistical profile baseline (`profile_baseline_v0`), not an Isolation Forest `can_model.joblib`.

The saved evaluation CSV’s metrics can be independently recalculated from its recorded labels and predictions, but those predictions cannot be tied to the checked-in JSON artifact using available evidence. They are therefore documented as **saved-record metrics**, not confirmed fresh production-model performance. The exact production artifact and matching raw inputs must be identified before claiming that the evaluation verifies a particular deployed model.

## 1. Model and preprocessing review

### Checked-in CAN Sentinel baseline

- **Model:** Statistical profile baseline (`profile_baseline_v0`), storing per-feature means and standard deviations for normal traffic.
- **Training data size:** 20 normal windows in the checked-in artifact.
- **Window protocol:** Fixed, non-overlapping 0.5-second windows.
- **Decision rule:** Compute absolute per-feature z-scores; mark a window anomalous when its maximum absolute z-score exceeds the stored sigma threshold. The artifact records `threshold_sigma = 5.0`.
- **Preprocessing:** Sort frames by timestamp, bucket by `int(timestamp / window_s)`, and compute features from the frames in each window.

### Training and inference feature order

The training script’s `FEATURES` list, the saved artifact’s `features` array, and the inference code’s feature indexing use the same order:

1. `frame_count`
2. `frames_per_sec`
3. `mean_inter_arrival_ms`
4. `min_inter_arrival_ms`
5. `max_inter_arrival_ms`
6. `unique_can_ids`
7. `id_entropy`
8. `top_id_share`

This is positive evidence of feature-order consistency **within this checked-in JSON profile-baseline pipeline**. The prediction script reads feature names and window duration from that artifact and imports `extract_features` from the same training module, avoiding a separate inference-time feature implementation.

### Artifact/schema discrepancy

Other uploaded scripts describe a different model pipeline: the Isolation Forest training and test scripts list `message_count`, `avg_interval_ms`, `unique_payloads`, and `payload_entropy` in that order. They do not use `unique_can_ids` and do not match the checked-in eight-feature profile baseline. The previously saved holdout/evaluation CSV has a five-feature schema. No `can_model.joblib` or matching raw captures for a fresh run were available in the checked project files/uploads. These pipelines and their results must not be treated as interchangeable.

## 2. Existing evaluation results

### Saved evaluation CSV audit

The saved holdout and evaluation CSVs each contain 100 rows, with 25 rows for each saved scenario: Normal, Burst, Replay, and Recovery. The evaluation rows match the holdout by window ID, scenario, ground-truth label, and all five recorded feature values. The stored TP/FP/FN/TN outcomes are internally consistent with the stored predictions and labels.

Positive class: `ANOMALY`.

| Actual \\ Predicted | Predicted ANOMALY | Predicted NORMAL | Total |
|---|---:|---:|---:|
| Actual ANOMALY | 50 (TP) | 0 (FN) | 50 |
| Actual NORMAL | 1 (FP) | 49 (TN) | 50 |
| **Total** | **51** | **49** | **100** |

| Metric | Recalculated from saved records |
|---|---:|
| Accuracy | 99.00% |
| Precision | 98.04% |
| Recall | 100.00% |
| F1-score | 99.01% |

Scenario results in those saved records:

| Saved scenario | Rows | Saved outcomes |
|---|---:|---|
| Normal | 25 | 24 TN, 1 FP |
| Burst | 25 | 25 TP |
| Replay | 25 | 25 TP |
| Recovery | 25 | 25 TN |

These metrics describe only the saved prediction rows. A row-for-row consistency check validates the data joins and arithmetic, not which model artifact generated those predictions. The saved scenario labels are Burst and Recovery; they are not explicit High-rate and Mixed labels. Any equivalence between Burst and High-rate must be confirmed, and Recovery does not validate Mixed traffic.

### Checked-in baseline prediction record

The project’s `ml/artifacts/predictions.csv` contains 20 normal windows all predicted normal and 20 high-rate-attack windows all predicted anomalous. The output labels are derived from the dataset names by the test script; this artifact does not include independently sourced ground-truth labels. These counts document the saved inference output, but are not a substitute for a labeled, independent evaluation or for the separate 100-row evaluation above.

## 3. Limitations and real-world validation needs

- **Small training baseline:** The artifact is fitted from only 20 normal windows. It may not represent normal operating variation across vehicles, routes, speeds, operating states, or environmental conditions.
- **Narrow attack coverage:** The checked-in test script explicitly documents simulated high-rate flooding/DoS as the evaluated attack type. Replay, mixed traffic, spoofing, fuzzing, and subtle/low-rate attacks are not established by that test output.
- **Synthetic/simulated evidence:** Saved evaluation records alone do not establish performance on real vehicle CAN traffic. Their model provenance and scenario-label mapping remain unresolved.
- **Windowing trade-off:** A 500 ms window can smooth short transients but also adds observation latency and may obscure very brief events. Performance should be checked at the intended operating protocol with timestamped raw captures.
- **Baseline-specific assumptions:** The profile detector flags deviations from a learned normal profile; benign changes in vehicle state could appear anomalous, while attacks that stay within the profile may be missed. The stored near-zero timing standard deviations are handled by a 1.0 fallback in inference, which should be verified against representative data before operational use.
- **No live-system evidence:** These files do not validate end-to-end latency, robustness, false-alarm burden, or safety behavior on an in-vehicle deployment.

Real-world validation should use independently labeled, representative captures across normal operating modes and attack classes, preserve the exact feature order and 500 ms windowing contract, separate train/calibration/test captures, and report per-scenario confusion matrices and false-alarm rates. The authoritative model artifact and its provenance should be recorded with each evaluation.

## 4. Final status

- **Feature order:** Verified consistent across the checked-in JSON baseline training script, artifact, and inference script.
- **Preprocessing:** Verified consistent in code for timestamp sorting, 500 ms windowing, and feature extraction.
- **Existing metrics:** Recalculated and internally consistent for the saved 100-row evaluation CSV; not confirmed as freshly generated by the checked-in production artifact.
- **Production model identity:** Unresolved because the checked-in project uses JSON profile-baseline artifacts, while separate uploaded scripts refer to an Isolation Forest and no `can_model.joblib` was available.
- **Model changes:** None. No retraining or threshold adjustment was performed.
- **Next evidence needed:** Identify the authoritative deployed artifact and provide matching raw, independently labeled validation captures, including explicit Mixed traffic and an agreed mapping for any Burst/High-rate scenario.
