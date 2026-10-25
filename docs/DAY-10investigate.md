### Title: [INVESTIGATION] Isolation Forest Fails to Detect High-Rate CAN DoS Traffic (7.25% FN, 10.69% FPR)

---

### 1. Problem Statement
Evaluation of the CAN-Sentinel ML anomaly detection module (`src/train_model_1.py`, `src/test_model.py`) reveals that the current Isolation Forest model is failing to identify high-rate CAN bus flood attacks, misclassifying extreme-frequency attack packets as `NORMAL`.

In accordance with project safety guidelines, **no model parameters have been changed and no retraining has been performed**. This issue documents the empirical test results, feature schema discrepancies, and identified root causes.

---

### 2. Empirical Test Benchmark (`ml_evaluation.csv`, $N = 200$)

* **Confusion Matrix:** $\text{TP} = 64 \quad|\quad \text{FP} = 14 \quad|\quad \text{TN} = 117 \quad|\quad \text{FN} = 5$
* **Recall:** 92.75%
* **Precision:** 82.05%
* **Overall Accuracy:** 90.50%
* **False Alarm Rate (FPR):** 10.69%

#### Critical False Negatives (Missed High-Rate Floods)
The model classified 5 critical high-rate injection frames as `normal`:

| Sample ID | Timestamp | CAN ID | Traffic Frequency | Payload Entropy | Prediction | Ground Truth | Threat Category |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **#6** | 0.06 s | `0x000` | 1,310.81 Hz | 0.261 | `normal` | `attack` | Bus-Off Priority DoS |
| **#14** | 0.14 s | `0x7DF` | 1,080.82 Hz | 0.120 | `normal` | `attack` | Diagnostic Broadcast Flood |
| **#65** | 0.65 s | `0x7DF` | 1,481.69 Hz | 0.325 | `normal` | `attack` | Diagnostic Broadcast Flood |
| **#109** | 1.09 s | `0x000` | 1,131.49 Hz | 0.134 | `normal` | `attack` | Bus-Off Priority DoS |
| **#199** | 1.99 s | `0x000` | 1,130.03 Hz | 0.286 | `normal` | `attack` | Bus-Off Priority DoS |

> **Security Impact:** Arbitration ID `0x000` holds the highest bus priority. Unflagged bursts at $>1,100\text{ Hz}$ can completely starve legitimate ECUs of bandwidth without triggering an intrusion alert.

#### Skewed False Positives (False Alarms on Benign Traffic)
False alarms cluster heavily on legitimate sensors with lower nominal transmission rates:
* **`0x316`:** 5 FP / 27 frames (**18.52% error rate**)
* **`0x2B0`:** 4 FP / 23 frames (**17.39% error rate**)

---

### 3. Feature Space Comparison (Training vs. Testing)

| Feature Dimension | Training Pipeline (`src/train_model_1.py`) | Testing/Integration Pipeline (`ml_evaluation.csv`) | Discrepancy & Impact |
| :--- | :--- | :--- | :--- |
| **Data Granularity** | Aggregated time windows (multi-packet) | Per-packet streaming frames | Single-frame inference lacks window burst context. |
| **Timing Metric** | `avg_interval_ms` (time delta in ms) | `msg_frequency_hz` (frequency in Hz) | **Inverse scale mismatch**: Trees split on millisecond thresholds cannot parse Hz rates directly. |
| **Volume Metric** | `message_count` (packets per window) | *None* (single packet) | Window density information is completely missing during per-frame tests. |
| **Payload Diversity** | `unique_payloads` (count of distinct bytes) | *None* | Zero-variance payload floods cannot be differentiated. |
| **Entropy** | `payload_entropy` (Shannon: 0.0 – 8.0) | `payload_entropy` (Shannon: 0.0 – 8.0) | Present in both, but entropy alone does not separate all attacks. |
| **Bus Context** | *None* | `can_id`, `dlc` | Model ignores CAN ID priority and expected baseline timing. |

---

### 4. Root Causes

1. **Window-Aggregation vs. Stream Inference Mismatch:** The model was trained expecting windowed summary metrics (`message_count`, `avg_interval_ms`, `unique_payloads`). Feeding per-packet streaming rows causes tree paths to misinterpret single-packet statistics.
2. **Hardcoded Contamination Cap (`contamination=0.05`):** In `src/train_model_1.py`, contamination is fixed to 5%. In scikit-learn, this forces the decision threshold to treat ~95% of incoming samples as `NORMAL`, causing attack bursts in evaluation batches to be suppressed.
3. **Absence of Per-ID Period Baselines:** Powertrain signals naturally cycle fast (10–20 ms), whereas body controllers cycle slowly (100–500 ms). Evaluating both under a single global threshold causes normal jitter on slow IDs to look anomalous (FP), while floods on fast IDs get absorbed into the distribution (FN).
4. **Potential Training Set Contamination:** If baseline training data (`can_features.csv`) contained unscrubbed burst traffic, the Isolation Forest learned high packet rates as nominal behavior.

---

### 5. Acceptance Criteria & Next Steps

- [ ] **CLI Decoupling:** Refactor `src/train_model_1.py` and `src/test_model.py` to take `--input`, `--model`, `--output`, and `--eval` CLI flags instead of hardcoded paths.
- [ ] **Streaming FIFO Window Buffer:** Implement a sliding FIFO buffer (5–10 frames) in stream ingestion to compute rolling window metrics before feeding the model.
- [ ] **Per-CAN ID Timing Normalization:** Normalize intervals relative to nominal broadcast period:
  $$\text{Interval Ratio} = \frac{\Delta t}{T_{\text{nominal}}(can\_id)}$$
- [ ] **Verification of Training Baseline:** Audit and verify clean, attack-free baseline traffic logs before any model retraining or parameter adjustments are approved.
- [ ] **Target Detection Thresholds:**
  - High-rate attack recall: $\ge 99.0\%$ (0 missed `0x000` frames).
  - Normal traffic false positive rate: $\le 2.0\%$ across all nominal IDs.
