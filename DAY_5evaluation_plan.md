# CAN-Sentinel — ML Evaluation Plan & Feature Format

Prepared from Zeeshan's uploads: `train_model.py`, `test_model.py`,
`normal_traffic_new.csv`, `high_rate_traffic_new.csv` (2026-10-24).

## 1. Script review

- **`train_model.py`** — trains `IsolationForest(n_estimators=100,
  contamination=0.05, random_state=42)` on a numeric feature matrix read
  from `can_features.csv`, requires >= 10 rows, saves `can_model.joblib`.
  Unsupervised (anomaly detection), no labels used.
- **`test_model.py`** — loads `can_model.joblib`, scores `can_features.csv`,
  writes `prediction` (NORMAL/ANOMALY), `anomaly_score`
  (decision_function; negative = more anomalous) and
  `model_test_results.csv`.
- **Gap found:** both scripts expect a pre-computed `can_features.csv`,
  but Zeeshan's CSVs are raw CAN frame logs
  (`timestamp_s, mode, can_id, data`). `extract_features.py` (included)
  bridges that gap.

## 2. Required feature format — `can_features.csv`

One row per (capture window, CAN ID). Required numeric columns, in this
exact spelling (scripts index by name):

| Column             | Definition                                          |
|--------------------|-----------------------------------------------------|
| `message_count`    | frames from that CAN ID in the window               |
| `avg_interval_ms`  | mean gap between consecutive frames, ms             |
| `unique_payloads`  | distinct `data` payloads in the window              |
| `payload_entropy`  | Shannon entropy (bits) over the window's payloads   |

Optional provenance columns (safe to include; scripts ignore them):
`source`, `window`, `can_id`, `label`.

Windowing: **1.0 s** per capture window (`extract_features.py`,
`WINDOW_S = 1.0`). Windowing is required — per-capture aggregation gives
only ~4 rows, below the 10-row training minimum. 10 s captures yield 40
windows each. Any raw CSV with columns `timestamp_s, mode, can_id, data`
is accepted:

```
python3 extract_features.py <raw1.csv> <raw2.csv> ...   # -> can_features.csv
python3 train_model.py                                   # on clean traffic only
python3 test_model.py                                    # on any capture
```

Observed feature separation (per-window means):

| Traffic      | message_count | avg_interval_ms | payload_entropy |
|--------------|---------------|-----------------|-----------------|
| normal       | 6.25          | 157.57          | 2.57            |
| high_rate    | 62.50         | 15.95           | 5.96            |

## 3. Evaluation plan

**Phase A — Reference pipeline validation (done, see §4).**
Verify extraction, training and scoring run end-to-end on Zeeshan's CSVs.

**Phase B — Zeeshan's model file.** Zeeshan's `can_model.joblib` (and his
training `can_features.csv`, if different from ours) has not been shared
yet. When it arrives, re-run `test_model.py` against it and record
predictions unchanged — no retraining.

**Phase C — Detection metrics.** Score windows from each capture and
compute per-capture: flag rate (share of windows marked ANOMALY), and on
labeled sets: true-positive rate (ANOMALY on attack traffic), false
positive rate (ANOMALY on normal traffic), plus confusion matrix and
anomaly_score distributions (normal vs. attack) with the score threshold
at 0.

**Phase D — Robustness sweep.** Only after Phases B–C pass:
1. Sliding windows (50% overlap) to check stability of flag rate.
2. Window sizes 0.5 s / 1 s / 2 s — does detection hold?
3. Injection attacks (targeted IDs flooded, others kept normal) — a
   model trained on whole-window features can only flag when the window
   skews; targeted-attack sensitivity must be measured, not assumed.
4. Unseen CAN IDs and benign bursty traffic (e.g. diagnostics) to
   measure false positives on realistic normal variation.
5. Threshold/contamination sensitivity: vary `contamination` 0.01–0.1
   and re-check FP/TP trade-off.

**Decision rule:** report accuracy only from Phase C onward, per
project note — no detection-accuracy claims until the model is tested
with real attack traffic. Simulated high-rate results are labeled as
simulated in every report.

## 4. Reference run (provisional — reference model, not Zeeshan's)

Trained exactly per `train_model.py` on the 40 normal windows, then
scored on all 80 windows:

| Capture             | Windows | Flagged ANOMALY | Note                    |
|---------------------|---------|-----------------|-------------------------|
| normal_traffic_new  | 40      | 2               | FPs at extreme windows  |
| high_rate_traffic   | 40      | 40              | all flagged             |

The 2 normal false positives are low-count windows (2 and 11 messages)
and the 40 high-rate windows share one score cluster, so the separation
is wide — but **these numbers describe the reference model only** and
are not the system's detection accuracy.

Artifacts: `can_features.csv` (80 rows), `model_test_results.csv`
(80 scored rows), `extract_features.py`, `train_model.py`,
`test_model.py` (unmodified).
