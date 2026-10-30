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
