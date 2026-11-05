# ML Model and Preprocessing Verification Audit

**Audit date:** 5 November 2026  
**Scope:** Existing trained model and preprocessing only; no retraining or threshold changes.

## Executive conclusion

The saved prediction records can be arithmetically validated, but a fresh inference run against the production artifact cannot be verified from the available evidence. The current CAN Sentinel project contains a frozen **500 ms statistical profile baseline** in `ml/artifacts/can_sentinel_model.json`, not a `can_model.joblib` Isolation Forest. The available prediction CSV uses a separate five-feature schema and does not establish which artifact produced its predictions.

Accordingly, the metrics below are an audit of the saved `evaluation_results.csv` predictions, **not newly generated or independently reproduced model predictions**. Do not treat them as confirmed production-model performance until the artifact and matching inputs are supplied or identified.

## Saved prediction results (record-level audit)

I checked all 100 rows in the saved evaluation CSV against the holdout CSV. All 100 rows matched on window ID, scenario, ground-truth label, and all five recorded feature values. The saved TP/FP/FN/TN outcomes were also internally consistent with the saved labels and predictions.

Positive class is `ANOMALY`.

| Actual \\ Predicted | ANOMALY | NORMAL | Total |
|---|---:|---:|---:|
| ANOMALY | 50 (TP) | 0 (FN) | 50 |
| NORMAL | 1 (FP) | 49 (TN) | 50 |
| **Total** | **51** | **49** | **100** |

| Metric | Audited saved-record result |
|---|---:|
| Accuracy | 99.00% |
| Precision | 98.04% |
| Recall | 100.00% |
| F1-score | 99.01% |

These values are recomputed from the saved predictions: TP=50, FP=1, TN=49, FN=0.

### Scenario coverage in the saved holdout

| Saved scenario | Rows | Saved prediction outcomes |
|---|---:|---|
| Normal | 25 | 24 TN, 1 FP |
| Burst | 25 | 25 TP |
| Replay | 25 | 25 TP |
| Recovery | 25 | 25 TN |

The holdout labels **Burst** and **Recovery**, not **High-rate** and **Mixed**. Burst may represent the requested high-rate case only if the dataset owner confirms that mapping. Recovery is not evidence for Mixed traffic. Therefore, results for a distinct Mixed scenario are unavailable, and no Mixed performance claim is made.

## Model and preprocessing consistency evidence

### Current CAN Sentinel project artifact

The project training script and checked-in artifact identify the active project baseline as:

- **Artifact:** `ml/artifacts/can_sentinel_model.json` (`profile_baseline_v0`)
- **Window duration:** 0.5 seconds
- **Threshold:** 5.0 sigma, stored as `threshold_sigma`
- **Ordered feature contract:** `frame_count`, `frames_per_sec`, `mean_inter_arrival_ms`, `min_inter_arrival_ms`, `max_inter_arrival_ms`, `unique_can_ids`, `id_entropy`, `top_id_share`
- **Preprocessing:** sort CAN frames by timestamp, assign them to fixed 500 ms windows, then compute the eight features in the order above. The inference script loads the artifact's `features`, `mean`, `std`, `threshold_sigma`, and `window_s`; it computes absolute z-scores and flags a window when its maximum absolute z-score exceeds the threshold.

The training script uses that same ordered feature list and preprocessing function. This verifies internal feature-order consistency for the project's JSON profile-baseline pipeline.

### Separate uploaded Isolation Forest scripts

The uploaded `train_model_1.py` and `test_model.py` instead specify this ordered four-feature contract: `message_count`, `avg_interval_ms`, `unique_payloads`, `payload_entropy`. Neither script includes `unique_can_ids`. That is not the same schema as either the project's eight-feature baseline or the five-feature saved holdout/evaluation CSV.

No `can_model.joblib` artifact or matching raw CAN input captures for Normal, High-rate, Replay, and Mixed were available in the checked project files or uploads. Thus, the Isolation Forest's fitted feature names/order and its actual preprocessing cannot be verified from the model artifact, and the saved CSV cannot bridge that mismatch.

## Validation status and next step

- **Verified:** the project's JSON baseline's ordered features match its training and inference code; the saved CSVs align row-for-row; saved confusion counts and metrics recalculate correctly.
- **Not verified:** that the saved CSV predictions came from the current production artifact; a new inference run; a distinct Mixed scenario; or a `can_model.joblib` preprocessing contract.
- **No model, parameter, or threshold changes were made.**

To complete a production inference verification, provide or identify the authoritative production artifact and the matching raw or correctly preprocessed holdout inputs for all four requested scenarios. If the JSON profile baseline is authoritative, the inputs must support its eight-feature 500 ms contract; if the Isolation Forest is authoritative, provide its exact artifact and matching four-feature inputs (or the authoritative five-feature model and its training contract). Confirm whether the saved Burst and Recovery labels correspond to High-rate and Mixed before mapping those results.
