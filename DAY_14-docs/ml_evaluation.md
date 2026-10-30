# ML Feature Analysis and Evaluation Report

**Project:** CAN-Sentinel — Automotive CAN Bus Intrusion Detection System  
**Document Path:** `docs/ml_evaluation.md`  
**Target Audience:** Nikhil, Avinash, and CAN-Sentinel Development Team  
**Evaluation Scope:** Traffic Feature Profiling, IsolationForest Anomaly Detection, Confusion Matrix & Metric Analysis, Synthetic Dataset Limitations, and Deployment Recommendations.

---

## 1. Executive Summary & Team Note for Avinash

**Hi Avinash,**

Yahan CAN-Sentinel ML anomaly detection pipeline ka complete feature analysis aur quantitative evaluation document kiya gaya hai. Humne `normal_traffic_new_1.csv` (clean baseline) aur `high_rate_traffic_new_1.csv` (DoS/flooding attack) traffic captures ke features ko time-window basis par extract karke model behavior aur metrics ko thoroughly evaluate kiya hai:

1. **Feature Separation:** Normal aur High-Rate traffic ke darmiyan charon key features (`message_count`, `avg_interval_ms`, `unique_payloads`, `payload_entropy`) mein distinct statistical separation hai. High-rate flooding bus load ko 10x increase karta hai (40 ms -> 4 ms interval, 6.25 -> 62.5 messages/window).
2. **Model Performance at Contamination = 0.05:** Model ne 100% attack recall achieve kiya (40/40 high-rate windows flagged), with **Precision = 95.24%**, **Recall = 100.00%**, aur **F1-Score = 97.56%** (2 False Positives out of 40 normal windows).
3. **Threshold Sensitivity (`contamination` parameter):** Contamination setting threshold (`offset_`) ko directly shift karti hai. `0.01` par threshold collapse ho jata hai (0% attack detection), jabki `0.10` par false alarms badh kar 4 ho jate hain bina kisi additional detection gain ke.
4. **Key Caution:** Dataset purely synthetic hai (10 seconds / 40 windows per class). Real-vehicle CAN bus par deploy karne se pehle dynamic vehicle state transitions aur subtle attacks (masquerade/spoofing) par testing zaroori hai.

---

## 2. Normal vs. High-Rate Traffic Comparison

Dono datasets 10.0 seconds duration ke captures hain. ML feature extraction pipeline in frames ko **0.25-second (250 ms) non-overlapping time windows** mein aggregate karta hai, jisse har class ke **40 windows** (total 80 evaluation windows) form hote hain.

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

Pipeline har 250 ms window ke liye 4 statistical/information-theoretic features extract karta hai:

1. `message_count`: Window ke andar total received CAN frames.
2. `avg_interval_ms`: Window ke andar consecutive frames ka average time difference (milliseconds).
3. `unique_payloads`: Window ke andar distinct data byte sequences ki count.
4. `payload_entropy`: Window ke andar payload byte sequences ki Shannon entropy (bits).

### Statistical Comparison Table (40 Normal Windows vs. 40 High-Rate Windows)

| Feature | Traffic Class | Mean | Std Dev | Min | Median (50%) | Max | Interpretation |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **`message_count`** | Normal | **6.25** | 0.44 | 6.00 | 6.00 | 7.00 | Regular, low-rate bus transmission (25 fps baseline) |
| | High-Rate | **62.50** | 0.51 | 62.00 | 62.50 | 63.00 | **10x surge**: DoS bus flooding injection |
| **`avg_interval_ms`** | Normal | **40.00** | 0.00 | 40.00 | 40.00 | 40.00 | Fixed 40 ms periodic ECU cycle time |
| | High-Rate | **4.00** | 0.00 | 4.00 | 4.00 | 4.00 | **Drastic drop**: Aggressive micro-interval packet blast |
| **`unique_payloads`** | Normal | **6.25** | 0.44 | 6.00 | 6.00 | 7.00 | Har packet ka unique random/counter data within small batch |
| | High-Rate | **62.50** | 0.51 | 62.00 | 62.50 | 63.00 | **High variety**: Dense stream of distinct random payloads |
| **`payload_entropy`** | Normal | **2.64** bits | 0.10 | 2.58 | 2.58 | 2.81 | Low entropy; limited unique states in small window |
| | High-Rate | **5.97** bits | 0.01 | 5.95 | 5.97 | 5.98 | **High entropy**: Uniformly randomized synthetic payloads |

### Feature-by-Feature Detailed Insights

1. **`message_count`:**
   - **Mechanism:** Bus load directly reflect karta hai. Normal operational traffic 6 ya 7 messages per window produce karta hai. High-rate traffic continuous flooding karta hai, resulting in exactly ~62–63 frames per window.
   - **Separation Power:** Yeh feature clear linearly separable boundary provide karta hai (max normal = 7 vs min high-rate = 62). DoS attack detection ke liye single strongest volume metric hai.

2. **`avg_interval_ms`:**
   - **Mechanism:** Normal traffic mein ECUs periodic schedule par broadcast karte hain (40 ms mean gap). Attack condition mein attacker CAN bus par arbitration capture karne ke liye minimum delay (4 ms) par frames transmit karta hai.
   - **Separation Power:** 10x difference (40 ms vs 4 ms) timing anomaly detection ko ultra-sharp banata hai.

3. **`unique_payloads`:**
   - **Mechanism:** Synthetic generator mein har frame random payload generate karta hai, isliye unique payload count directly `message_count` ke saath scale hoti hai.
   - **Caveat:** Real vehicle CAN bus par signal values (e.g. coolant temperature, gear position) repetitive ya slowly changing hoti hain, jabki synthetic attack stream random bytes push karti hai.

4. **`payload_entropy`:**
   - **Mechanism:** Shannon entropy $H(X) = -\sum p(x) \log_2 p(x)$ measure karti hai. Normal traffic mein 6 frames hone ki wajah se maximum theoretical entropy $\log_2(6) \approx 2.58$ bits hoti hai. High-rate traffic mein 62–63 unique frames hone par entropy $\log_2(62) \approx 5.95$ bits tak pahunch jati hai.
   - **Utility:** Fuzzing aur randomized payload injection ko regular telemetry se distinguish karne ke liye highly effective hai.

---

## 4. ML Model Training vs. Testing Feature Comparison

### Training Protocol (Unsupervised Anomaly Detection)
- **Model:** Scikit-Learn `IsolationForest(n_estimators=200, random_state=42)`
- **Training Subset:** Clean normal traffic only (`label` contains "normal", 40 windows). Attack samples training ke time model ko provide nahi kiye jate (One-Class semi-supervised formulation).
- **Core Hypothesis:** Isolation Forest clean baseline traffic ka feature subspace learn karta hai. Jo samples clean distribution se isolated hain (kam tree depth par partition ho jate hain), unhe anomaly flag kiya jata hai.

### Feature Space Distribution Shift

| Dimension | Training Set (Clean Normal) | Testing Set (All 80 Windows) | Isolation Forest Partitioning Impact |
|:---|:---:|:---:|:---|
| **Sample Distribution** | 40 rows (100% Normal) | 80 rows (50% Normal, 50% High-Rate) | Bimodal distribution with extreme gap |
| **`message_count` Range** | $[6.0, 7.0]$ | $[6.0, 63.0]$ | High-rate samples root split par hi isolate ho jate hain |
| **`avg_interval_ms` Range** | $[40.0, 40.0]$ | $[4.0, 40.0]$ | Zero-variance baseline vs 4.0 ms extreme outlier |
| **`payload_entropy` Range** | $[2.58, 2.81]$ | $[2.58, 5.98]$ | +3.33 bits shift test set mein |
| **Tree Average Path Length** | High path length ($h(x) \approx \text{deep}$) | Normal = Deep, High-Rate = Very Short ($h(x) \approx 1-2$) | Anomaly score for high-rate is drastically lower (more negative) |

---

## 5. Performance Evaluation: Confusion Matrix & Metrics

Sensitivity experiment mein `contamination` parameter ko sweep kiya gaya across **{0.01, 0.05, 0.10}**.

### Classification Metrics Formulation
- **Positive Class:** Anomaly / Attack (High-Rate Traffic)
- **Negative Class:** Normal / Benign Traffic
- **True Positive (TP):** High-rate window correctly flagged as ANOMALY.
- **False Positive (FP):** Normal window incorrectly flagged as ANOMALY.
- **True Negative (TN):** Normal window correctly classified as NORMAL.
- **False Negative (FN):** High-rate window missed and classified as NORMAL.

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
- **Analysis:** Contamination ko 0.01 set karne se decision boundary normal cluster ke itne extreme tail par shift ho gayi ki high-rate score cluster threshold ke upar chala gaya. Result: Zero attack detection (Complete Recall Collapse).

#### 3. Contamination = 0.10 (Over-Sensitive / Elevated False Alarms)
```
                  Predicted Normal     Predicted Anomaly
Actual Normal            36 (TN)              4 (FP)
Actual High-Rate          0 (FN)             40 (TP)
```
- **Analysis:** Cutoff loose hone se normal traffic ke 4 benign low-frequency windows anomaly ban gaye. Attack detection 40/40 par constant raha, isliye precision drop ho kar 90.91% ho gayi.

---

## 6. Synthetic Dataset Limitations

Realistic automotive IDS validation ke point of view se is dataset ki following technical limitations hain:

1. **Simulated Perfect Periodicity (No Real Jitter or Arbitration):**
   - Synthetic generator strict intervals par messages queue karta hai (e.g. exactly 40 ms ya 4 ms).
   - Real CAN networks par physical bus arbitration, transmission retries, clock drift, aur bit-stuffing ki wajah se jitter naturally occur hota hai.
2. **Minimal Training Sample Size (40 Windows / 10 Seconds):**
   - 40 windows threshold setting ke liye statistically small sample size hai. Aise chote dataset par `contamination` setting 1 ya 2 outlier samples se disproportionately distort ho sakti hai.
3. **Absence of ECU State Transitions:**
   - Real vehicle operations mein ignition-on, idle, high-speed cruise, emergency braking, aur diagnostic mode ke dauran message frequencies legitimate tarike se change hoti hain. Synthetic data mein yeh dynamics missing hain.
4. **Single Extreme Attack Type Evaluated (DoS Flooding Only):**
   - High-rate flooding detection sabse asaan attack vector hai kyunki yeh bus volume ko 10x explode karta hai.
   - Yeh evaluation subtle attacks (jaise low-frequency payload spoofing, stealthy sensor replay, ya selective ECU masquerading) par model ki detection capability prove nahi karta.
5. **Lack of Independent Hold-Out Test Set:**
   - Same continuous capture block se evaluation windows extract kiye gaye hain. True out-of-distribution generalization test nahi hui hai.

---

## 7. Actionable Recommendations for Avinash & Next Steps

Avinash, model ko production/experimental prototype standard par lane ke liye yeh recommendations implement karni chahiye:

1. **Move Away from Hardcoded Contamination:**
   - `contamination` setting par rely karne ke bajaye, clean validation data ke decision scores par **Percentile Thresholding (e.g. 99th percentile of normal scores)** ya **Extreme Value Theory (EVT)** use karein.
2. **Feature Engineering Expansion:**
   - Sirf total `message_count` par depend na karein. Feature set mein yeh add karein:
     - **Per-CAN-ID Delta Time Variance:** Individual critical IDs (e.g. `0x0C0` RPM, `0x0D0` Speed) ka interval variance.
     - **CAN ID Entropy:** Bus par active IDs ki diversity (DoS flooding aksar single ID par concentrated hoti hai).
     - **Cyclic Redundancy / Rolling Counter Check:** Automotive safety frames mein payload counter sequencing verify karna.
3. **Multi-Attack Capture Suite:**
   - `machine_learning.py` mein available DoS, Fuzzing, Replay, aur Spoofing attack generators ke separate captures run karke comprehensive multi-class evaluation benchmark create karein.
4. **Benchmarking with Hardware / SocketCAN:**
   - CAN Buddy application aur Linux `vcan0` (SocketCAN) par live injection run karke latency aur memory footprint evaluate karein taaki embedded ECU constraints par real-time inference validate ho sake.

---

*Report generated and validated for CAN-Sentinel ML Evaluation Milestone.*
