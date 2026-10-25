# CAN-Sentinel: ML Model Evaluation Report

**File:** `docs/ml_evaluation.md`  
**Date:** 2026-10-25  
**System:** CAN-Sentinel Automotive Intrusion Detection System (IDS)  
**Evaluator:** ML Engineering & Evaluation Lead  
**Artifacts Reviewed:**
* `src/train_model.py` (Training pipeline script)
* `src/test_model.py` (Inference & testing script)
* `ml_evaluation.csv` (Integration test evaluation dataset, 200 samples)
* `model_test_results.csv` (Historical windowed model test benchmark, 80 samples)
* `normal_traffic.csv` & `high_rate_traffic.csv` (Raw synthetic CAN traffic streams)

---

## 1. Executive Summary & Verdict

### 1.1 Suitability Verdict: NOT CURRENTLY PRODUCTION-SUITABLE
The existing machine learning model in CAN-Sentinel is **not yet suitable for reliable attack detection in production automotive environments**. 

While the model achieves high nominal recall on synthetic high-rate bursts ($92.75\%$ on `ml_evaluation.csv` and $100\%$ on clean historical window sets), empirical evaluation reveals two critical vulnerabilities:
1. **Critical False Negatives ($7.25\%$ Missed Attacks, $5/69$):** Severe high-frequency denial-of-service ($0\text{x}000$ at $>1,300\text{ Hz}$) and diagnostic fuzzing ($0\text{x}7DF$ at $>1,480\text{ Hz}$) injections were classified as `NORMAL`. In an automotive CAN bus, missing arbitration ID $0\text{x}000$ (highest priority dominant frame) allows bus-off DoS attacks to paralyze the vehicle without triggering IDS alerts.
2. **Excessive False Positive Rate ($10.69\%$ FPR, $14/131$ Normal Frames):** More than 1 out of every 10 legitimate frames is falsely flagged as an attack (peaking at $18.52\%$ false alarm rate on ID $0\text{x}316$). In an in-vehicle network, this rate would cause severe alert fatigue, spurious diagnostic trouble codes (DTCs), or unwarranted fail-safe/limp-home mode triggers.
3. **Core Evaluation Ground Rule:** Successful predictions on normal traffic or synthetic high-rate bursts alone do **not** constitute proof of robust attack detection capability.

---

## 2. Review of Existing Workflow (`src/train_model.py` & `src/test_model.py`)

### 2.1 Workflow Architecture Analysis
* **`src/train_model.py` Workflow:**
  1. Hardcodes input path `DATA_FILE = "can_features.csv"` and output `MODEL_FILE = "can_model.joblib"`.
  2. Extracts 4 continuous features: `["message_count", "avg_interval_ms", "unique_payloads", "payload_entropy"]`.
  3. Checks minimum sample constraint (`len(df) >= 10`).
  4. Fits an unsupervised `IsolationForest(n_estimators=100, contamination=0.05, random_state=42)`.
  5. Serializes the trained model to disk via `joblib.dump()`.
* **`src/test_model.py` Workflow:**
  1. Hardcodes the identical input path `FEATURE_FILE = "can_features.csv"`.
  2. Deserializes `can_model.joblib`.
  3. Evaluates `model.predict(X)` and `model.decision_function(X)`.
  4. Maps binary outputs: `1` $\rightarrow$ `"NORMAL"`, `-1` $\rightarrow$ `"ANOMALY"`.
  5. Outputs summary table to console and saves raw predictions to `model_test_results.csv`.

### 2.2 Critical Flaws & Compatibility Issues in the Scripts
1. **Circular Testing & Data Leakage:** Both scripts share the hardcoded filename `can_features.csv`. If a developer runs `train_model.py` followed immediately by `test_model.py`, the model is evaluated directly on its own training data without a train/test split.
2. **Missing Feature Scaling:** No normalization or scaling (`StandardScaler` / `RobustScaler`) is applied. The features span wildly different scales (`message_count`: 2–150 vs. `avg_interval_ms`: 7–520 ms vs. `payload_entropy`: 0–7 bits). Because Isolation Forest selects split points uniformly between feature min and max, high-variance timing features disproportionately dictate tree partitioning over entropy.
3. **Absence of Ground Truth Evaluation:** `src/test_model.py` has no label ingestion, no confusion matrix generation, and no precision/recall calculation. It blindly outputs predictions without verifying detection accuracy against ground truth.
4. **Hardcoded Contamination Blindspot:** Setting `contamination=0.05` assumes that exactly $5\%$ of the input data is anomalous. When evaluating a test set where $50\%$ of the data is attack traffic, this parameter distorts the decision boundary.

---

## 3. Feature Comparison: Training vs. Integration Test Environment

A fundamental structural and semantic gap exists between what `src/train_model.py` expects and what the integration test environment produces:

| Comparison Dimension | Model Training Features (`train_model.py`) | Integration Test Features (`ml_evaluation.csv`) | Compatibility Gap & Impact |
| :--- | :--- | :--- | :--- |
| **Observation Level** | Windowed statistical aggregate (1 row = 1 CAN ID per $1.0\text{ s}$) | Per-frame stream event (1 row = 1 CAN packet) | **Granularity mismatch:** Stream events cannot be scored by the windowed model without temporal buffering. |
| **Primary Rate Metric** | `message_count` (int, count per window) & `avg_interval_ms` (mean $\Delta t$ in ms) | `msg_frequency_hz` (instantaneous frequency in Hertz) | **Semantic mismatch:** The trained model has no concept of `msg_frequency_hz`; passing integration test columns directly causes missing column errors. |
| **Payload Metric** | `unique_payloads` (count) & `payload_entropy` (Shannon bits) | `payload_entropy` (instantaneous entropy) & `dlc` (8) | `unique_payloads` is completely absent from streaming data. |
| **Arbitration Context** | Partitions by `can_id` across temporal windows | Evaluates mixed bus stream with `can_id` as a metadata column | Inter-arrival timing must be calculated per `can_id`, not across the whole bus. |
| **Detection Latency** | Inherently bounded by window length ($\ge 1,000\text{ ms}$) | Continuous real-time ($0.01 - 0.02\text{ s}$ per frame) | Windowing introduces up to 1-second lag, delaying critical DoS intervention. |

---

## 4. Feature Value Distribution Analysis: Normal vs. High-Rate Traffic

### 4.1 Integration Test Feature Values (`ml_evaluation.csv`, $N=200$)

| Feature Metric | Normal Traffic ($N=131$) | High-Rate Attack ($N=69$) | Factor / Difference |
| :--- | :--- | :--- | :--- |
| **`msg_frequency_hz` (Mean $\pm$ Std)** | $66.92 \pm 33.92\text{ Hz}$ | $1,215.02 \pm 206.96\text{ Hz}$ | **18.2x surge** in attack frequency |
| **`msg_frequency_hz` Range** | $11.02\text{ Hz} - 119.88\text{ Hz}$ | $826.78\text{ Hz} - 1,488.76\text{ Hz}$ | Clear mathematical separation margin ($>700\text{ Hz}$) |
| **`payload_entropy` (Mean $\pm$ Std)** | $0.714 \pm 0.128\text{ bits}$ | $0.254 \pm 0.086\text{ bits}$ | **2.8x drop** in attack entropy |
| **`payload_entropy` Range** | $0.501 - 0.950\text{ bits}$ | $0.110 - 0.393\text{ bits}$ | Distinct boundary gap between attack padding and normal signals |

### 4.2 Raw Traffic Windowed Distributions (`normal_traffic.csv` vs. `high_rate_traffic.csv`, 1.0s slices)

| Feature (per CAN ID, 1.0s window) | Normal Traffic Baseline ($50\text{ msg/s}$) | High-Rate Traffic ($500\text{ msg/s}$) | Difference Rationale |
| :--- | :--- | :--- | :--- |
| **`message_count`** | Mean: $12.50 \pm 3.01$ (Range: $8 - 19$) | Mean: $125.00 \pm 9.23$ (Range: $102 - 144$) | **10.0x higher** due to injection rate |
| **`avg_interval_ms`** | Mean: $79.48 \pm 21.43\text{ ms}$ (Range: $47.8 - 134.3$) | Mean: $7.99 \pm 0.58\text{ ms}$ (Range: $6.95 - 9.54$) | **10.0x compressed** inter-arrival interval |
| **`payload_entropy`** | Mean: $3.60 \pm 0.35$ (Range: $3.00 - 4.25$) | Mean: $6.96 \pm 0.11$ (Range: $6.67 - 7.17$) | Synthetic random payloads inflate window entropy |

---

## 5. Root-Cause Analysis: Why the Model Classifies High-Rate Traffic as NORMAL

When developers observe high-rate traffic being classified as `NORMAL`, the failure stems from five concrete technical causes:

### 5.1 Cause 1: Training Data Contamination (Unsupervised Inversion)
Isolation Forest is strictly an **unsupervised anomaly detection algorithm**; it does not read a `label` column. It defines "normal" as whatever data occupies the densest clusters in its training matrix:
* If `src/train_model.py` is executed on a `can_features.csv` file generated from mixed traffic or high-rate captures, the high-rate traffic (which generates 10x more frames: 5,000 frames vs 500 normal frames) dominates the dataset.
* The model builds isolation trees around the high-rate cluster. Consequently, **high-rate traffic is scored as nominal inliers (`NORMAL`, score $> 0$)**, and low-frequency normal traffic is isolated as outliers (`ANOMALY`)!

### 5.2 Cause 2: Sklearn Contamination Threshold Distortion
In `src/train_model.py`, the hyperparameter `contamination=0.05` explicitly fixes the anomaly threshold such that only the top $5\%$ most extreme points are assigned label `-1` (`ANOMALY`):
* If a test dataset contains $50\%$ high-rate attack traffic, scikit-learn's default `predict()` threshold is mathematically constrained to classify **at least $95\%$ of all input samples as `NORMAL`**.
* This forces the vast majority of high-rate attack samples to receive the `NORMAL` label.

### 5.3 Cause 3: Direct Streaming Ingestion Without Window Aggregation
If raw CAN frames from Zeeshan's generator are fed directly into `test_model.py` without Avinash's window feature extraction:
* An un-aggregated frame has `message_count = 1` and `avg_interval_ms = 1000.0 ms`.
* Because each frame appears isolated, the high-rate flood is invisible to the model. The model observes what looks like severe bus starvation or idle traffic, often defaulting to `NORMAL`.

### 5.4 Cause 4: Decision Boundary Fragmentation in High-Dimensional Space
In `ml_evaluation.csv`, 5 high-rate attack samples (e.g., Sample #65 with $1,481.69\text{ Hz}$ frequency) were classified as `normal`. This occurs because:
* Without feature scaling, decision trees partition along unstandardized features. In isolated regions where entropy ($0.325$) and frequency ($1,481\text{ Hz}$) intersect near tree depth limits, random split hyperplanes group the sample into a deep, nominal leaf node.

---

## 6. Empirical Verification: False Positives & False Negatives

Based on verified empirical evidence from `ml_evaluation.csv` ($N=200$ samples: $131$ Normal, $69$ Attack):

### 6.1 Global Confusion Matrix

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

### 6.2 Quantitative Benchmark Metrics

| Metric | Target Standard | Observed Value | Status |
| :--- | :--- | :--- | :--- |
| **Detection Rate (Recall / TPR)** | $\ge 99.0\%$ | **92.75%** ($64 / 69$) | **FAIL** (5 attacks missed) |
| **False Positive Rate (FPR)** | $\le 2.0\%$ | **10.69%** ($14 / 131$) | **FAIL** (High false alarm rate) |
| **Precision** | $\ge 95.0\%$ | **82.05%** ($64 / 78$) | **FAIL** (17.95% alarms are false) |
| **F1-Score** | $\ge 0.970$ | **0.8707** | **FAIL** |
| **Overall Accuracy** | $\ge 95.0\%$ | **90.50%** ($181 / 200$) | **FAIL** |

### 6.3 Detailed False Negative Analysis (Missed Attacks — Security Critical)
All 5 missed attacks exhibited extreme frequency ($>1,000\text{ Hz}$) and low entropy, yet were classified as `normal`:

| Sample ID | Timestamp | CAN ID | Message Frequency (`Hz`) | Payload Entropy | Prediction | Actual Attack Type | Security Impact |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **#6** | $0.06\text{ s}$ | `0x000` | $1,310.81\text{ Hz}$ | $0.261$ | `normal` | DoS Bus Flooding | Highest priority arbitration flood missed |
| **#14** | $0.14\text{ s}$ | `0x7DF` | $1,080.82\text{ Hz}$ | $0.120$ | `normal` | OBD-II Diagnostic Fuzz | Diagnostic gateway injection missed |
| **#65** | $0.65\text{ s}$ | `0x7DF` | $1,481.69\text{ Hz}$ | $0.325$ | `normal` | High-Rate Diagnostic Flood | Peak frequency injection ($1.48\text{ kHz}$) bypassed |
| **#109** | $1.09\text{ s}$ | `0x000` | $1,131.49\text{ Hz}$ | $0.134$ | `normal` | DoS Bus Flooding | Periodic DoS burst missed |
| **#199** | $1.99\text{ s}$ | `0x000` | $1,130.03\text{ Hz}$ | $0.286$ | `normal` | DoS Bus Flooding | End-of-window flood missed |

### 6.4 Detailed False Positive Analysis (False Alarms — Operational Usability)
Fourteen normal frames triggered false alarms, concentrated heavily on specific CAN IDs:
* **`0x316`**: 5 False Positives out of 27 frames (**$18.52\%$ error rate**). (e.g., Sample #4: $47.43\text{ Hz}$, entropy $0.570$; Sample #45: $27.03\text{ Hz}$, entropy $0.634$).
* **`0x2B0`**: 4 False Positives out of 23 frames (**$17.39\%$ error rate**). (e.g., Sample #77: $82.97\text{ Hz}$, entropy $0.556$; Sample #107: $34.66\text{ Hz}$, entropy $0.531$).
* **`0x0C1`**: 2 False Positives ($8.33\%$ error rate).
* **`0x43F`**: 2 False Positives ($8.00\%$ error rate).
* **`0x1A0`**: 1 False Positive ($3.13\%$ error rate).
* **Root Cause:** Certain legitimate automotive sensors (e.g., gear selector, coolant temperature) produce repetitive or static payload bytes resulting in lower entropy ($0.50 - 0.65$), while transient bus traffic causes minor frequency spikes ($80 - 120\text{ Hz}$). The model's uniform threshold confuses these with attack patterns.

---

## 7. Model Improvement & Remediation Suggestions

To resolve compatibility issues and achieve production-grade detection, implement the following architectural upgrades:

### 7.1 Immediate Pipeline Architecture Fixes (`src/train_model.py` & `src/test_model.py`)
1. **Decouple Training and Testing Inputs:**
   * Modify both scripts to accept explicit CLI arguments (`--input`, `--model`, `--output`, `--ground-truth`) instead of sharing hardcoded `can_features.csv`.
2. **Incorporate Feature Scaling:**
   * Fit a `RobustScaler` or `StandardScaler` inside `train_model.py` and bundle it with the model into a unified Scikit-Learn `Pipeline` artifact:
     ```python code
     from sklearn.pipeline import Pipeline
     from sklearn.preprocessing import RobustScaler
     from sklearn.ensemble import IsolationForest

     pipeline = Pipeline([
         ('scaler', RobustScaler()),
         ('model', IsolationForest(n_estimators=150, contamination=0.01, random_state=42))
     ])
     ```
3. **Verify Pure Clean Baseline for Training:**
   * Ensure that `train_model.py` is trained **strictly on verified 100% nominal traffic**. Set `contamination=0.01` or use thresholding based on Extreme Value Theory (EVT) rather than letting arbitrary contamination distort the decision score.

### 7.2 Per-CAN ID Baseline Profiling (Resolve False Positives)
* A single global model across all CAN IDs is flawed because powertrain IDs transmit at 10 ms while body/chassis IDs transmit at 100–500 ms.
* **Remediation:** Compute normalized interval ratios:
  $$\text{Interval Ratio} = \frac{\Delta t_{\text{observed}}}{T_{\text{nominal}}(can\_id)}$$
  Normalizing by expected per-ID period ensures that a 20 ms burst on a 500 ms sensor is detected accurately without falsely flagging a 10 ms powertrain frame.

### 7.3 Hybrid Feature Vector (Bridge Streaming & Window Mismatch)
* Expand the feature vector to include both instantaneous and rolling context:
  1. `instantaneous_frequency_hz`: Measured via rolling 5-packet FIFO queue.
  2. `delta_t_jitter`: Standard deviation of successive frame intervals.
  3. `payload_hamming_distance`: Byte-level distance between consecutive frames of the same ID (flags replay and static injection).
  4. `rolling_entropy`: Shannon entropy computed over a short rolling window (e.g., 10 packets) rather than a rigid 1.0-second tumbling window.

### 7.4 Model Algorithm Upgrade (Resolve False Negatives)
* Transition from pure unsupervised Isolation Forest to a **Semi-Supervised One-Class SVM with RBF Kernel** or an **Autoencoder Neural Network** trained exclusively on nominal driving cycles.
* For labeled evaluation environments, benchmark against gradient-boosted decision trees (**XGBoost / LightGBM**) to establish the upper bound on classification separability.

---

## 8. Summary Action Item Tracker

| Action Item | Responsible | Target Deliverable | Priority |
| :--- | :--- | :--- | :--- |
| **Pipeline CLI & Decoupling** | Avinash | Update `src/train_model.py` and `src/test_model.py` | High |
| **Scaler & Pipeline Artifact** | Avinash | Bundle `RobustScaler` into `can_model.joblib` | High |
| **Per-ID Period Normalization** | Avinash | Implement $\Delta t / T_{\text{nominal}}$ feature extraction | High |
| **Attack Vector Diversification** | Zeeshan | Generate spoofing, fuzzing, and replay datasets | Medium |
| **Automated Benchmarking** | ML Eval Lead | Integrate confusion matrix & recall tests into CI/CD | High |

---

---

## 9. Executive Debrief & Actionable Handoff for Avinash

### 9.1 Key Takeaways for Avinash
1. **Pipeline & Script Decoupling Needed Immediately:**
   * Both `src/train_model.py` and `src/test_model.py` currently hardcode `can_features.csv`.
   * This causes circular data dependency, risks data leakage, and prevents running test evaluation against independent benchmark sets without overwriting the training source.
   * Add CLI argument parsing (`argparse`) to accept `--input`, `--model`, `--output`, and optional `--ground-truth`.

2. **Feature Scale Disparity Distorts Tree Partitions:**
   * Features like `message_count` (2–150) and `avg_interval_ms` (7–520 ms) operate on vastly larger numeric scales than `payload_entropy` (0–7 bits).
   * Because Isolation Forest selects random cutpoints between min and max per feature, timing features dominate tree depth, while entropy splits are under-utilized.
   * Wrap the feature transformation in a Scikit-Learn `Pipeline` with `RobustScaler` before `IsolationForest`.

3. **Per-CAN ID Normalization is Vital to Fix False Positives (FPR = 10.69%):**
   * Legitimate CAN IDs have completely different native transmission periods (e.g., powertrain at 10 ms vs. body sensors at 100–500 ms).
   * A single global threshold causes lower-frequency IDs like `0x316` (18.52% false alarm rate) and `0x2B0` (17.39% false alarm rate) to be misclassified as anomalies during benign jitter.
   * Baseline the nominal period $T_{\text{nominal}}$ per ID and train on normalized interval ratios $\Delta t / T_{\text{nominal}}$.

4. **Stream vs. Window Mismatch Explains High-Rate Traffic Misclassifications:**
   * `train_model.py` expects window-aggregated statistical features (`message_count`, `avg_interval_ms`, `unique_payloads`, `payload_entropy`).
   * Integration testing (`ml_evaluation.csv`) evaluates per-frame streaming events (`msg_frequency_hz`, `payload_entropy`, `dlc`).
   * When raw frames are streamed without window buffering, single frames appear isolated, causing high-rate injection attacks to bypass detection and be marked `NORMAL`.
   * Conversely, if training data is contaminated with high-rate bursts, the unsupervised model learns high frequency as nominal inliers, inverting detection logic.

5. **Detection Performance Summary (Empirical Benchmark):**
   * Tested on $N=200$ samples: **TP = 64, FP = 14, TN = 117, FN = 5**.
   * Accuracy: **90.50%**, Precision: **82.05%**, Recall: **92.75%**, F1-Score: **0.8707**, False Positive Rate: **10.69%**.
   * The 5 missed attacks (False Negatives) include critical high-rate DoS arbitration floods (`0x000` at $>1,300\text{ Hz}$) and diagnostic fuzzing (`0x7DF` at $>1,480\text{ Hz}$).
   * **Rule of Thumb:** High test accuracy on normal traffic alone is not evidence of reliable IDS protection. Ground-truth evaluation against real adversarial attacks is required.
