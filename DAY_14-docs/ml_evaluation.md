# ML Feature Analysis and Evaluation Report

**Project:** CAN-Sentinel — Automotive CAN Bus Intrusion Detection System  
**Document Path:** `docs/ml_evaluation.md`  
**Target Audience:** Nikhil, Avinash, and the CAN-Sentinel Development Team  
**Evaluation Scope:** Traffic feature profiling, IsolationForest anomaly detection, confusion matrix and metric analysis, synthetic dataset limitations, and deployment recommendations.

---

## 1. Executive Summary & Team Note for Avinash

**Hi Avinash,**

This document presents the complete feature analysis and quantitative evaluation of the CAN-Sentinel ML anomaly detection pipeline. We extracted features from the `normal_traffic_new_1.csv` (clean baseline) and `high_rate_traffic_new_1.csv` (DoS/flooding attack) traffic captures on a time-window basis and thoroughly evaluated model behavior and metrics. The key findings are:

1. **Feature Separation:** Across all four key features (`message_count`, `avg_interval_ms`, `unique_payloads`, `payload_entropy`), there is distinct statistical separation between normal and high-rate traffic. High-rate flooding increases bus load by 10x (interval drops from 40 ms to 4 ms, and message count per window rises from 6.25 to 62.5).
2. **Model Performance at Contamination = 0.05:** The model achieved 100% attack recall (40/40 high-rate windows flagged), with **Precision = 95.24%**, **Recall = 100.00%**, and **F1-Score = 97.56%** (2 false positives out of 40 normal windows).
3. **Threshold Sensitivity (`contamination` parameter):** The contamination setting directly shifts the decision threshold (`offset_`). At `0.01`, the threshold collapses (0% attack detection), while at `0.10`, false alarms rise to 4 without any additional detection gain.
4. **Key Caution:** The dataset is purely synthetic (10 seconds / 40 windows per class). Before deploying on a real vehicle CAN bus, testing under dynamic vehicle state transitions and subtle attacks (masquerade/spoofing) is essential.

---

## 2. Normal vs. High-Rate Traffic Comparison

Both datasets are captures of 10.0-second duration. The ML feature extraction pipeline aggregates these frames into **0.25-second (250 ms) non-overlapping time windows**, producing **40 windows per class** (80 evaluation windows in total).

### High-Level Capture Summary

| Parameter | Normal Traffic (`normal_traffic_new_1.csv`) | High-Rate Traffic (`high_rate_traffic_new_1.csv`) | Ratio / Shift |
|:---|:---:|:---:|:---:|
| **Total Frames** | 250 frames | 2,500 frames | **10.0x increase** |
| **Duration** | 10.0 s (0.00s to 9.96s) | 10.0 s (0.000s to 9.996s) | Equal (10s) |
| **Average Frame Rate** | 25.0 frames/sec (Hz) | 250.0 frames/sec (Hz) | **10.0x bus load** |
| **Mean Inter-Frame Gap** | 40.0 ms | 4.0 ms | **10.0x compression** |
| **CAN IDs Present** | 0x100, 0x120, 0x200, 0x300 | 0x100, 0x120, 0x200, 0x300 | Identical ID set |
| **Evaluation Windows (0.25s)** | 40 windows | 40 windows | Total = 80 windows |

---

## 3. Deep-Dive Feature Analysis

For each 250 ms window, the pipeline extracts four statistical/information-theoretic features:

1. `message_count`: The total number of CAN frames received within the window.
2. `avg_interval_ms`: The average time difference (in milliseconds) between consecutive frames within the window.
3. `unique_payloads`: The count of distinct data byte sequences within the window.
4. `payload_entropy`: The Shannon entropy (in bits) of the payload byte sequences within the window.

### Statistical Comparison Table (40 Normal Windows vs. 40 High-Rate Windows)

| Feature | Traffic Class | Mean | Std Dev | Min | Median (50%) | Max | Interpretation |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **`message_count`** | Normal | **6.25** | 0.44 | 6.00 | 6.00 | 7.00 | Regular, low-rate bus transmission (25 fps baseline) |
| | High-Rate | **62.50** | 0.51 | 62.00 | 62.50 | 63.00 | **10x surge**: DoS bus flooding injection |
| **`avg_interval_ms`** | Normal | **40.00** | 0.00 | 40.00 | 40.00 | 40.00 | Fixed 40 ms periodic ECU cycle time |
| | High-Rate | **4.00** | 0.00 | 4.00 | 4.00 | 4.00 | **Drastic drop**: Aggressive micro-interval packet blast |
| **`unique_payloads`** | Normal | **6.25** | 0.44 | 6.00 | 6.00 | 7.00 | Each packet carries a unique random/counter value within a small batch |
| | High-Rate | **62.50** | 0.51 | 62.00 | 62.50 | 63.00 | **High variety**: Dense stream of distinct random payloads |
| **`payload_entropy`** | Normal | **2.64** bits | 0.10 | 2.58 | 2.58 | 2.81 | Low entropy; limited unique states in a small window |
| | High-Rate | **5.97** bits | 0.01 | 5.95 | 5.97 | 5.98 | **High entropy**: Uniformly randomized synthetic payloads |

### Feature-by-Feature Detailed Insights

1. **`message_count`:**
   - **Mechanism:** This feature directly reflects bus load. Normal operational traffic produces 6 or 7 messages per window. High-rate traffic floods the bus continuously, resulting in exactly ~62–63 frames per window.
   - **Separation Power:** This feature provides a clear linearly separable boundary (max normal = 7 vs. min high-rate = 62). It is the single strongest volume metric for DoS attack detection.

2. **`avg_interval_ms`:**
   - **Mechanism:** In normal traffic, ECUs broadcast on a periodic schedule (40 ms mean gap). Under attack conditions, the attacker transmits frames at minimum delay (4 ms) to capture arbitration on the CAN bus.
   - **Separation Power:** The 10x difference (40 ms vs. 4 ms) makes timing anomaly detection extremely sharp.

3. **`unique_payloads`:**
   - **Mechanism:** In the synthetic generator, each frame produces a random payload, so the unique payload count scales directly with `message_count`.
   - **Caveat:** On a real vehicle CAN bus, signal values (e.g., coolant temperature, gear position) are repetitive or slowly changing, whereas the synthetic attack stream pushes random bytes.

4. **`payload_entropy`:**
   - **Mechanism:** This measures Shannon entropy, $H(X) = -\sum p(x) \log_2 p(x)$. In normal traffic, with 6 frames per window, the maximum theoretical entropy is $\log_2(6) \approx 2.58$ bits. In high-rate traffic, with 62–63 unique frames, entropy reaches up to $\log_2(62) \approx 5.95$ bits.
   - **Utility:** This is highly effective for distinguishing fuzzing and randomized payload injection from regular telemetry.

---

## 4. ML Model Training vs. Testing Feature Comparison

### Training Protocol (Unsupervised Anomaly Detection)
- **Model:** Scikit-Learn `IsolationForest(n_estimators=200, random_state=42)`
- **Training Subset:** Clean normal traffic only (`label` contains "normal", 40 windows). Attack samples are not provided to the model during training (one-class semi-supervised formulation).
- **Core Hypothesis:** The Isolation Forest learns the feature subspace of clean baseline traffic. Samples that are isolated from the clean distribution (i.e., partitioned at a shallow tree depth) are flagged as anomalies.

### Feature Space Distribution Shift

| Dimension | Training Set (Clean Normal) | Testing Set (All 80 Windows) | Isolation Forest Partitioning Impact |
|:---|:---:|:---:|:---|
| **Sample Distribution** | 40 rows (100% Normal) | 80 rows (50% Normal, 50% High-Rate) | Bimodal distribution with an extreme gap |
| **`message_count` Range** | $[6.0, 7.0]$ | $[6.0, 63.0]$ | High-rate samples are isolated at the root split itself |
| **`avg_interval_ms` Range** | $[40.0, 40.0]$ | $[4.0, 40.0]$ | Zero-variance baseline vs. 4.0 ms extreme outlier |
| **`payload_entropy` Range** | $[2.58, 2.81]$ | $[2.58, 5.98]$ | A +3.33-bit shift in the test set |
| **Tree Average Path Length** | High path length ($h(x) \approx \text{deep}$) | Normal = Deep, High-Rate = Very Short ($h(x) \approx 1-2$) | The anomaly score for high-rate traffic is drastically lower (more negative) |

---

## 5. Performance Evaluation: Confusion Matrix & Metrics

In the sensitivity experiment, the `contamination` parameter was swept across **{0.01, 0.05, 0.10}**.

### Classification Metrics Formulation
- **Positive Class:** Anomaly / Attack (High-Rate Traffic)
- **Negative Class:** Normal / Benign Traffic
- **True Positive (TP):** A high-rate window correctly flagged as ANOMALY.
- **False Positive (FP):** A normal window incorrectly flagged as ANOMALY.
- **True Negative (TN):** A normal window correctly classified as NORMAL.
- **False Negative (FN):** A high-rate window missed and classified as NORMAL.

### Detailed Comparison Across Contamination Settings

| Metric | Contamination = 0.01 | Contamination = 0.05 (Reference) | Contamination = 0.10 |
|:---|:---:|:---:|:---:|
| **Fitted Anomaly Threshold (`offset_`)** | **−0.740462** | **−0.646774** | **−0.554491** |
| **Total Predicted Anomalies** | 1 / 80 | 42 / 80 | 44 / 80 |
| **True Positives (TP)** | 0 | **40** | 40 |
| **False Positives (FP)** | 1 | **2** | 4 |
| **True Negatives (TN)** | 39 | **38** | 36 |
| **False Negatives (FN)** | 40 | **0** | 0 |
| **Precision** | **0.00%** (0/1) | **95.24%** (40/42) | **90.91%** (40/44) |
| **Recall (Sensitivity)** | **0.00%** (0/40) | **100.00%** (40/40) | **100.00%** (40/40) |
| **Specificity (True Negative Rate)** | **97.50%** (39/40) | **95.00%** (38/40) | **90.00%** (36/40) |
| **F1-Score** | **0.00%** | **97.56%** | **95.24%** |
| **Overall Accuracy** | 48.75% (39/80) | **97.50%** (78/80) | 95.00% (76/80) |

---

### Confusion Matrices

#### 1. Contamination = 0.05 (Optimal Balance)
```
                  Predicted Normal     Predicted Anomaly
Actual Normal            38 (TN)              2 (FP)
Actual High-Rate          0 (FN)             40 (TP)
```
- **Precision:** $40 / (40 + 2) = 95.24\%$
- **Recall:** $40 / (40 + 0) = 100.00\%$
- **F1-Score:** $2 \times (0.9524 \times 1.0) / (0.9524 + 1.0) = 97.56\%$

#### 2. Contamination = 0.01 (Under-Sensitive / Threshold Collapse)
```
                  Predicted Normal     Predicted Anomaly
Actual Normal            39 (TN)              1 (FP)
Actual High-Rate         40 (FN)              0 (TP)
```
- **Analysis:** Setting contamination to 0.01 shifts the decision boundary so far into the extreme tail of the normal cluster that the high-rate score cluster moves above the threshold. The result is zero attack detection (complete recall collapse).

#### 3. Contamination = 0.10 (Over-Sensitive / Elevated False Alarms)
```
                  Predicted Normal     Predicted Anomaly
Actual Normal            36 (TN)              4 (FP)
Actual High-Rate          0 (FN)             40 (TP)
```
- **Analysis:** With a looser cutoff, 4 benign low-frequency windows from normal traffic are classified as anomalies. Attack detection remains constant at 40/40, so precision drops to 90.91%.

---

## 6. Synthetic Dataset Limitations

From the perspective of realistic automotive IDS validation, this dataset has the following technical limitations:

1. **Simulated Perfect Periodicity (No Real Jitter or Arbitration):**
   - The synthetic generator queues messages at strict intervals (e.g., exactly 40 ms or 4 ms).
   - On real CAN networks, jitter occurs naturally due to physical bus arbitration, transmission retries, clock drift, and bit-stuffing.
2. **Minimal Training Sample Size (40 Windows / 10 Seconds):**
   - 40 windows is a statistically small sample size for threshold setting. On such a small dataset, the `contamination` setting can be disproportionately distorted by just 1 or 2 outlier samples.
3. **Absence of ECU State Transitions:**
   - In real vehicle operation, message frequencies legitimately change during ignition-on, idle, high-speed cruise, emergency braking, and diagnostic mode. These dynamics are missing from the synthetic data.
4. **Single Extreme Attack Type Evaluated (DoS Flooding Only):**
   - High-rate flooding detection is the easiest attack vector, because it explodes bus volume by 10x.
   - This evaluation does not prove the model's detection capability against subtle attacks (such as low-frequency payload spoofing, stealthy sensor replay, or selective ECU masquerading).
5. **Lack of Independent Hold-Out Test Set:**
   - The evaluation windows were extracted from the same continuous capture block. A true out-of-distribution generalization test has not been performed.

---

## 7. Actionable Recommendations for Avinash & Next Steps

Avinash, to bring the model up to a production/experimental prototype standard, the following recommendations should be implemented:

1. **Move Away from Hardcoded Contamination:**
   - Instead of relying on the `contamination` setting, use **percentile thresholding** (e.g., the 99th percentile of scores on clean validation data) or **Extreme Value Theory (EVT)** on the decision scores.
2. **Feature Engineering Expansion:**
   - Do not depend solely on the total `message_count`. Add the following to the feature set:
     - **Per-CAN-ID Delta Time Variance:** Interval variance for individual critical IDs (e.g., `0x0C0` RPM, `0x0D0` Speed).
     - **CAN ID Entropy:** Diversity of active IDs on the bus (DoS flooding is often concentrated on a single ID).
     - **Cyclic Redundancy / Rolling Counter Check:** Verify payload counter sequencing in automotive safety frames.
3. **Multi-Attack Capture Suite:**
   - Run separate captures using the DoS, Fuzzing, Replay, and Spoofing attack generators available in `machine_learning.py`, and create a comprehensive multi-class evaluation benchmark.
4. **Benchmarking with Hardware / SocketCAN:**
   - Run live injection on the CAN Buddy application and Linux `vcan0` (SocketCAN) to evaluate latency and memory footprint, so that real-time inference can be validated against embedded ECU constraints.

---
