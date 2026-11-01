# CAN-Sentinel: Machine Learning Model Attack-Validation & Evaluation Report

**Project:** CAN-Sentinel — Automotive CAN Bus Intrusion Detection System (IDS)  
**Author:** Nikhil (CAN-Sentinel Core Team)  
**Collaborator / Recipient:** Avinash & CAN-Sentinel Development Team  
**Evaluation Scope:** Testing the updated Isolation Forest model against attack-validation datasets, analyzing Normal and Anomaly predictions, preparing confusion matrices across contamination thresholds, computing quantitative classification metrics (Accuracy, Precision, Recall, F1-Score), investigating misclassified samples, and providing deployment recommendations.  
**Date:** November 2026  

---

## 1. Executive Summary & Memo for Avinash

**Hi Avinash,**

This comprehensive evaluation report documents the testing and quantitative validation of our updated Machine Learning anomaly detection pipeline for CAN-Sentinel.

We evaluated the reference model (`contamination = 0.05`), the updated/experimental configuration (`contamination = 0.01`), and an over-sensitive variant (`contamination = 0.10`) on **80 validation time-windows** (40 clean Normal baseline windows + 40 High-Rate DoS Attack windows).

### Key Takeaways:
1. **Best Operational Baseline (`contamination = 0.05`):**
   - **Attack Recall: 100.00%** (40 out of 40 high-rate attack windows caught).
   - **Precision: 95.24%** (40 true attack detections out of 42 total alarms, with only 2 false positives).
   - **F1-Score: 97.56%**, **Overall Accuracy: 97.50%**.
   
2. **Updated Model Failure (`contamination = 0.01`):**
   - Attempting to suppress false alarms by lowering contamination to 0.01 caused complete **Threshold Collapse**.
   - **Recall dropped to 0.00%** (0 out of 40 attacks detected; all 40 attack windows were misclassified as False Negatives).
   - **Root Cause:** The Isolation Forest decision threshold (`offset_ = -0.740462`) dropped below the attack score cluster (+0.039), leading the model to classify high-volume attack traffic as 'NORMAL'.

3. **Recommendation for the Team:**
   - Retain **`contamination = 0.05`** as our active deployment configuration.
   - Discontinue threshold suppression attempts. Instead, focus future development on multi-feature engineering (per-ID delta variance, CAN ID entropy, and cyclic rolling counters).

---

## 2. Validation Dataset & Feature Pipeline

The validation dataset was evaluated on a non-overlapping time-window basis:
- **Window Sizing:** 0.25 seconds (250 ms) per window.
- **Normal Traffic Baseline (`normal_traffic_new_1.csv`):** 250 frames (25 frames/sec baseline), 10.0 seconds total capture duration, yielding **40 evaluation windows**. Mean interval is 40.0 ms, mean message count is 6.25 frames/window, and Shannon entropy is ~2.64 bits.
- **Attack Validation Capture (`high_rate_traffic_new_1.csv`):** 2,500 frames (250 frames/sec), 10.0 seconds total capture duration, yielding **40 evaluation windows**. Average interval drops to 4.0 ms (a 10x bus flooding surge), mean message count rises to 62.5 frames/window, and Shannon entropy increases to ~5.97 bits.

### Extracted Feature Dimensions:
1. `message_count`: Total CAN frames arriving within the 250 ms window.
2. `avg_interval_ms`: Average inter-arrival time (in ms) between consecutive frames.
3. `unique_payloads`: Number of unique 8-byte payload sequences in the window.
4. `payload_entropy`: Shannon entropy (in bits) computed over payload distributions.

---

## 3. Predictions Breakdown: Normal vs. ANOMALY

Evaluating all 80 validation windows (40 ground-truth Normal, 40 ground-truth High-Rate Attack) across three contamination configurations yielded:

| Model Configuration | Total Windows | Predicted NORMAL | Predicted ANOMALY | High-Rate Detected (Attack Recall) | Normal Windows Flagged (False Alarms) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Updated/Experimental (`c = 0.01`, n = 200)** | 80 | 79 | 1 | **0 / 40 (0.00%)** | **1 / 40 (2.50%)** |
| **Reference Model (`c = 0.05`, n = 100/200)** | 80 | 38 | 42 | **40 / 40 (100.00%)** | **2 / 40 (5.00%)** |
| **High Contamination (`c = 0.10`, n = 200)** | 80 | 36 | 44 | **40 / 40 (100.00%)** | **4 / 40 (10.00%)** |

---

## 4. Confusion Matrices

### Matrix 1: Recommended Reference Model (`contamination = 0.05`)
```
                          PREDICTED
                    Predicted NORMAL    Predicted ANOMALY    Total
ACTUAL Normal            38 (TN)              2 (FP)          40
ACTUAL High-Rate Attack   0 (FN)             40 (TP)          40
Total                    38                  42               80
```
- **True Positives (TP):** 40 (All high-rate attack windows correctly identified)
- **False Positives (FP):** 2 (Normal boundary windows falsely alerted)
- **True Negatives (TN):** 38 (Normal baseline windows correctly identified)
- **False Negatives (FN):** 0 (Zero attacks missed)

### Matrix 2: Updated Model (`contamination = 0.01` — Threshold Collapse)
```
                          PREDICTED
                    Predicted NORMAL    Predicted ANOMALY    Total
ACTUAL Normal            39 (TN)              1 (FP)          40
ACTUAL High-Rate Attack  40 (FN)              0 (TP)          40
Total                    79                   1               80
```
- **Outcome:** Severe threshold collapse. 40 attack windows completely missed because the decision threshold was moved excessively deep into the tail of the clean training distribution.

### Matrix 3: Over-Sensitive Model (`contamination = 0.10`)
```
                          PREDICTED
                    Predicted NORMAL    Predicted ANOMALY    Total
ACTUAL Normal            36 (TN)              4 (FP)          40
ACTUAL High-Rate Attack   0 (FN)             40 (TP)          40
Total                    36                  44               80
```
- **Outcome:** Elevated false alarms. False positives doubled from 2 to 4 without providing any gain in attack detection (Recall remained identical at 40/40).

---

## 5. Quantitative Evaluation Metrics

Formulations using Ground-Truth Validation Labels:
- $\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$
- $\text{Precision} = \frac{TP}{TP + FP}$
- $\text{Recall (Sensitivity)} = \frac{TP}{TP + FN}$
- $\text{Specificity (TNR)} = \frac{TN}{TN + FP}$
- $\text{F1-Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$

### Metric Summary Table

| Metric | Updated Model (`c = 0.01`) | Reference Model (`c = 0.05`) [OPTIMAL] | High Contamination (`c = 0.10`) |
|:---|:---:|:---:|:---:|
| **Accuracy** | 48.75% (39/80) | **97.50% (78/80)** | 95.00% (76/80) |
| **Precision** | 0.00% (0/1) | **95.24% (40/42)** | 90.91% (40/44) |
| **Recall (Sensitivity)** | 0.00% (0/40) | **100.00% (40/40)** | 100.00% (40/40) |
| **Specificity (TNR)** | 97.50% (39/40) | **95.00% (38/40)** | 90.00% (36/40) |
| **F1-Score** | 0.00% | **97.56%** | 95.24% |
| **Decision Threshold (`offset_`)** | -0.740462 | **-0.646774** | -0.554491 |

---

## 6. Root-Cause Analysis of Misclassified Samples

### A. Reference Model (`c = 0.05`): 2 False Positives (Normal $\rightarrow$ ANOMALY)
- **Misclassified Windows:** 2 normal windows out of 40.
- **Root Cause:** Due to partition edge boundaries and inter-arrival timing jitter in the baseline 10-second capture, these two windows registered message counts differing from the regular 6–7 messages (e.g., 2 or 11 messages per window). With a small training sample size (40 windows), the Isolation Forest flags these peripheral points as outliers.
- **Automotive Safety Assessment:** **Safe Failure Mode (Fail-Safe Alert)**. In vehicular electronic systems, raising an anomalous diagnostic alert while retaining zero false negatives (FN = 0) protects the vehicle against unmitigated attacks.

### B. Updated Model (`c = 0.01`): 40 False Negatives (Attack $\rightarrow$ NORMAL) + 1 FP
- **Misclassified Windows:** All 40 High-Rate DoS attack windows.
- **Root Cause:** Lowering contamination to 0.01 pushed the decision threshold downward to `-0.740462`. The high-rate flooding feature windows clustered at a positive decision function score of `+0.039`. Consequently, all attack windows scored higher than the threshold, causing the model to misclassify the entire attack sequence as NORMAL.
- **Automotive Safety Assessment:** **Catastrophic Silent Failure**. A massive 10x bus flooding attack passes completely undetected through the vehicle's gateway, potentially starving critical brake and throttle ECUs without alerting the intrusion response system.

---

## 7. Actionable Recommendations for Avinash & Next Steps

1. **Standardize on `contamination = 0.05`:**
   - Keep the reference configuration (`contamination = 0.05`, `n_estimators = 100` or `200`) as the active production baseline. Do not reduce contamination.
2. **Implement Dynamic Thresholding (Extreme Value Theory / Percentile):**
   - Replace arbitrary contamination tuning with statistical tail estimation, such as the 99th percentile of clean baseline decision scores or Extreme Value Theory (EVT) modeling.
3. **Multi-Attack Validation (`machine_learning.py`):**
   - Extend validation beyond DoS flooding. Generate dedicated validation datasets for the Fuzzing, Replay, and Spoofing attack routines provided in `machine_learning.py` to evaluate the model across stealthy and low-frequency attack profiles.
4. **Feature Engineering Enhancements:**
   - Incorporate per-CAN-ID delta interval variance (e.g., for `0x0C0` Engine RPM and `0x0D0` Vehicle Speed), CAN ID diversity entropy, and rolling payload counter verification to distinguish legitimate load changes from malicious injection.
