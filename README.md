# CAN-Sentinel
Automotive ECU Intrusion Detection System

## Identical Anomaly Score Investigation

- **Root cause:** The previous RBF-SVC model produced nearly zero kernel similarities for the tested feature vectors. Its decision scores therefore collapsed to the model intercept.
- **Artifact issue:** The previous saved model was inconsistent with the committed training script and its IsolationForest workflow.
- **Fix:** Rebuilt the training and inference pipeline around the same five features and preprocessing: message count, average interval, unique CAN IDs, unique payloads, and payload entropy.
- **Model validation:** Added a regression test to detect constant decision scores and verify both NORMAL and ANOMALY predictions on the balanced dataset.
- **Test result:** 13 tests passed.
- **Scope limitation:** Validation currently uses synthetic traffic. Real-world CAN traffic is still required to establish generalization and production reliability.
- **Separate adjustment:** The rate-based detection threshold was adjusted for the current synthetic traffic dataset; it is not a universally validated threshold.

## Day 15 – Attack Integration Validation

- Integrated the production model (`can_model.joblib`) into the integration pipeline.
- Validated normal and high-rate synthetic CAN traffic.
- Evaluated Burst, Replay, Normal, and Recovery scenarios from the attack-simulation dataset.
- Updated the rate-based boundary condition from `< 10 ms` to `<= 10 ms` to detect the synthetic Replay scenario.
- Added `tests/test_mixed_scenarios.py` with four scenario regression tests.
- Full test suite result: 17 passed.

Note: Burst and Replay were flagged by the rate-based rule, not independently by the ML model. Results are limited to the current synthetic datasets and do not establish universal CAN detection performance.

## Day 16 – Evaluation Reliability Improvements

- Audited the detector evaluation pipeline and identified filename-derived synthetic ground-truth labels.
- Regenerated evaluation metrics using the current 40 integration windows.
- Replaced substring-based ground-truth inference with strict supported filename mapping.
- Added regression tests for ambiguous filenames and directory-prefixed supported filenames.
- Targeted evaluator tests: 7 passed.
- Full test suite: 19 passed.

Note: Evaluation metrics use synthetic normal and high-rate traffic labels. They do not establish independent real-world CAN detection performance.
