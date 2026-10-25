# CAN-Sentinel: Model Evaluation & Attack Detection Report

**File:** `docs/ml_evaluation.md`  
**Generated:** 2026-10-25  
**System:** CAN-Sentinel Automotive Intrusion Detection System (IDS)  
**Evaluated Artifacts:** `ml_evaluation.csv` (labeled evaluation set), `model_test_results.csv` (Isolation Forest window benchmark), `normal_traffic.csv`, `high_rate_traffic.csv` (raw CAN traffic)

---

## 1. Executive Summary & Verdict

* **Verdict:** **NOT YET PRODUCTION-READY / NOT FULLY SUITABLE FOR DEPLOYMENT AS AN ATTACK DETECTOR.**
* **Core Rationale:**
  * While the model shows high recall against conspicuous high-rate traffic ($92.75\%$ on `ml_evaluation.csv` and $100\%$ on synthetic window test sets), it exhibits a **high False Positive Rate (FPR) of 10.69%** (14 false alarms out of 131 normal frames) and **5 critical False Negatives (7.25% FN rate)** where high-frequency DoS ($0\text{x}000$) and diagnostic fuzzing ($0\text{x}7DF$) packets completely bypassed detection.
  * In automotive safety-critical systems, an FPR of $>10\%$ triggers constant false alarms, ECU resets, or driver alert fatigue. More critically, missed injection frames on arbitration ID $0\text{x}000$ (CAN bus dominant priority) allow bus-off DoS attacks to succeed undetected.
  * **Crucial Rule Upheld:** Legitimate predictions on normal traffic or synthetic high-rate traffic alone do not constitute proof of comprehensive attack detection capability.

---

## 2. Review of Existing Model & Feature Columns

The CAN-Sentinel architecture employs two complementary evaluation representations across the project pipeline:

### 2.1 Per-Sample Detection Features (`ml_evaluation.csv`)
Used in per-message streaming evaluation:
* **`msg_frequency_hz`**: Instantaneous transmission rate / frequency in Hertz. Primary discriminator for high-rate flooding.
* **`payload_entropy`**: Information entropy of the payload bytes ($H(X)$). Measures payload repetition vs. diversity. Low entropy indicates fixed repetitive attack payloads (e.g., DoS zero-byte padding); higher entropy indicates dynamic legitimate vehicle signals.
* **`can_id`**: 11-bit standard arbitration ID determining ECU message priority.
* **`dlc`**: Data Length Code (standardized at 8 bytes).

### 2.2 Time-Windowed Aggregation Features (`model_test_results.csv`)
Used in the time-bucketed ($1.0\text{ s}$) Isolation Forest model:
1. **`message_count`**: Total frame count received per $(\text{window}, \text{can\_id})$.
2. **`avg_interval_ms`**: Mean inter-arrival time between successive frames in milliseconds.
3. **`unique_payloads`**: Cardinality of distinct 8-byte payload strings observed within the window.
4. **`payload_entropy`**: Base-2 Shannon entropy of the payload distribution across the window.

---

## 3. Feature Distribution Comparison: Normal vs. High-Rate Traffic

### 3.1 Streaming Evaluation Distributions (`ml_evaluation.csv`, $N=200$)

| Feature Metric | Normal Traffic ($N=131$) | Attack Traffic ($N=69$) | Separation / Shift |
| :--- | :--- | :--- | :--- |
| **`msg_frequency_hz` (Mean $\pm$ Std)** | $66.92 \pm 33.92\text{ Hz}$ | $1,215.02 \pm 206.96\text{ Hz}$ | **18.2x frequency increase** in attack traffic |
| **`msg_frequency_hz` Range** | $11.02\text{ Hz} - 119.88\text{ Hz}$ | $826.78\text{ Hz} - 1,488.76\text{ Hz}$ | Clear frequency gap between nominal and flood traffic |
| **`payload_entropy` (Mean $\pm$ Std)** | $0.714 \pm 0.128\text{ bits}$ | $0.254 \pm 0.086\text{ bits}$ | **2.8x entropy drop** in attack traffic (repetitive payload) |
| **`payload_entropy` Range** | $0.501 - 0.950\text{ bits}$ | $0.110 - 0.393\text{ bits}$ | Strong separation reflecting attack payload uniformity |

### 3.2 Time-Windowed Feature Comparison (`normal_traffic.csv` vs. `high_rate_traffic.csv`, 1.0s slices)

| Feature | Raw Normal Baseline ($10\text{ s}, 500\text{ msgs}$) | Raw High-Rate Traffic ($10\text{ s}, 5,000\text{ msgs}$) |
| :--- | :--- | :--- |
| **Total Bus Rate** | $50.0\text{ msgs/s}$ ($\sim 12.5\text{ msgs/s}$ per ID) | $500.0\text{ msgs/s}$ ($\sim 125.0\text{ msgs/s}$ per ID) |
| **`message_count`** | Mean: $12.50 \pm 3.01$ (Range: $8 - 19$) | Mean: $125.00 \pm 9.23$ (Range: $102 - 144$) |
| **`avg_interval_ms`** | Mean: $79.48 \pm 21.43\text{ ms}$ (Range: $47.8 - 134.3\text{ ms}$) | Mean: $7.99 \pm 0.58\text{ ms}$ (Range: $6.95 - 9.54\text{ ms}$) |
| **`payload_entropy`** | Mean: $3.60 \pm 0.35$ (Range: $3.00 - 4.25$) | Mean: $6.96 \pm 0.11$ (Range: $6.67 - 7.17$) |

*Rate Shift Warning:* Note that Zeeshan's raw normal traffic runs at $50\text{ msg/s}$ ($12.5\text{ msgs/window/ID}$), whereas earlier calibration in `model_test_results.csv` assumed $25\text{ msg/s}$ ($6.25\text{ msgs/window/ID}$). Uncalibrated models evaluated against the newer normal baseline experience rate drift that artificially elevates false alarms.

---

## 4. Empirical Model Performance & Confusion Matrix

From the labeled benchmark dataset (`ml_evaluation.csv`, 200 samples):

### 4.1 Confusion Matrix

```
                        Actual Class (Ground Truth)
                       ┌─────────────────┬─────────────────┐
                       │   Attack (P)    │   Normal (N)    │
     ┌─────────────────┼─────────────────┼─────────────────┤
     │ Predicted       │  True Positive  │ False Positive  │
     │ Attack (Pos)    │     TP = 64     │     FP = 14     │
Pred ├─────────────────┼─────────────────┼─────────────────┤
     │ Predicted       │ False Negative  │  True Negative  │
     │ Normal (Neg)    │     FN = 5      │    TN = 117     │
     └─────────────────┴─────────────────┴─────────────────┘
```

### 4.2 Core Evaluation Metrics

| Metric | Target / Benchmark | Observed Value | Status |
| :--- | :--- | :--- | :--- |
| **Detection Rate (Recall / TPR)** | $\ge 99.0\%$ | **92.75%** (64 / 69) | **FAIL** (5 missed attacks) |
| **False Positive Rate (FPR)** | $\le 2.0\%$ | **10.69%** (14 / 131) | **FAIL** (Unacceptable for automotive IDS) |
| **Precision** | $\ge 95.0\%$ | **82.05%** (64 / 78) | **FAIL** (18% of alerts are false alarms) |
| **F1-Score** | $\ge 0.970$ | **0.8707** | **FAIL** |
| **Overall Accuracy** | $\ge 95.0\%$ | **90.50%** (181 / 200) | **FAIL** |

### 4.3 Per-CAN ID Performance Breakdown

| CAN ID | Traffic Class | Total | TP | FP | TN | FN | Recall | FPR | Precision |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `0x000` | Attack (DoS) | 36 | 33 | 0 | 0 | 3 | **91.67%** | 0.00% | 100.0% |
| `0x7DF` | Attack (Diag Fuzz) | 33 | 31 | 0 | 0 | 2 | **93.94%** | 0.00% | 100.0% |
| `0x0C1` | Normal | 24 | 0 | 2 | 22 | 0 | N/A | **8.33%** | 0.00% |
| `0x1A0` | Normal | 32 | 0 | 1 | 31 | 0 | N/A | **3.13%** | 0.00% |
| `0x2B0` | Normal | 23 | 0 | 4 | 19 | 0 | N/A | **17.39%** | 0.00% |
| `0x316` | Normal | 27 | 0 | 5 | 22 | 0 | N/A | **18.52%** | 0.00% |
| `0x43F` | Normal | 25 | 0 | 2 | 23 | 0 | N/A | **8.00%** | 0.00% |
| **Total** | **Combined** | **200** | **64** | **14** | **117** | **5** | **92.75%** | **10.69%** | **82.05%** |

---

## 5. Error Analysis: False Positives & False Negatives

### 5.1 False Negatives (Type II Errors — Critical Security Failures)
Five attack instances were predicted as `normal`, failing to trigger IDS intervention:

| Sample ID | CAN ID | Message Frequency (`Hz`) | Payload Entropy | Ground Truth | Prediction | Vulnerability Impact |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **#6** | `0x000` | $1,310.81\text{ Hz}$ | $0.261$ | `attack` | `normal` | High-priority bus denial-of-service bypassed IDS |
| **#14** | `0x7DF` | $1,080.82\text{ Hz}$ | $0.120$ | `attack` | `normal` | Diagnostic broadcast injection bypassed IDS |
| **#65** | `0x7DF` | $1,481.69\text{ Hz}$ | $0.325$ | `attack` | `normal` | Ultra-high rate flooding packet missed |
| **#109** | `0x000` | $1,131.49\text{ Hz}$ | $0.134$ | `attack` | `normal` | Low-entropy priority injection missed |
| **#199** | `0x000` | $1,130.03\text{ Hz}$ | $0.286$ | `attack` | `normal` | Periodic flood burst missed |

*Root Cause:* Despite clear extreme frequency ($>1,000\text{ Hz}$) and low entropy ($<0.33$), the decision boundaries of the classifier suffer from decision space fragmentation or inadequate feature scaling, causing certain localized hyperplanes to classify severe injection frames as normal.

### 5.2 False Positives (Type I Errors — Operational Usability Failures)
Fourteen normal frames were flagged as `attack`, producing an alarming **$10.69\%$ FPR**:
* **Highest False Alarm IDs:** `0x316` (5 FPs, 18.52% error rate) and `0x2B0` (4 FPs, 17.39% error rate).
* **Sample Analysis:**
  * Sample #4 (`0x316`): Freq = $47.43\text{ Hz}$, Entropy = $0.570$ $\rightarrow$ Flagged as attack.
  * Sample #45 (`0x316`): Freq = $27.03\text{ Hz}$, Entropy = $0.634$ $\rightarrow$ Flagged as attack.
  * Sample #107 (`0x2B0`): Freq = $34.66\text{ Hz}$, Entropy = $0.531$ $\rightarrow$ Flagged as attack.
* *Root Cause:* Legitimate sensor signals with lower entropy (e.g. static sensor values such as constant temperature or gear selector) or natural burst transmissions are misclassified by overly sensitive decision thresholds.

---

## 6. Model Limitations & Engineering Recommendations

1. **Uncalibrated Global Thresholding:**
   * The model currently evaluates all CAN IDs using uniform decision criteria. However, different vehicle ECUs have fundamentally different transmission dynamics (e.g., powertrain at 10 ms, chassis at 50 ms, body at 200 ms).
   * *Remediation:* Implement **per-CAN ID baseline profiling** or normalized delta features ($\Delta t / T_{\text{nominal}}$).
2. **Frequency-Entropy Feature Insufficiency:**
   * Relying solely on message rate and entropy leaves the model vulnerable to stealthy, low-rate attacks (e.g., masquerade attacks injected at legitimate 50 Hz frequencies).
   * *Remediation:* Incorporate inter-arrival jitter, sequential payload Hamming distances, and counter/checksum cycle verification.
3. **Contamination and Overlap Tuning:**
   * In the Isolation Forest pipeline, the contamination factor ($0.05$) forces a fixed $5\%$ anomaly fraction even during completely clean baseline operations.
   * *Remediation:* Train on rigorously verified clean baseline traffic using One-Class SVM or tuned Isolation Forests with adaptive threshold calibration based on extreme value theory (EVT).
4. **Validation Next Steps:**
   * Re-evaluate against multi-vector attack datasets (Fuzzing, Spoofing, Replay, and Bus-Off) on independent holdout sets before deployment clearance.
