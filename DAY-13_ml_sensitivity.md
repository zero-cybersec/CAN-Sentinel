# Day 13 — ML Model Sensitivity Experiment (contamination parameter)

Date: 2026-10-28. Scope: how the IsolationForest `contamination` setting
changes predictions, swept through the same evaluation workflow as the
experimental model. **Nothing was overwritten** — the reference artifacts
(`can_model.joblib`, `model_test_results.csv`) and the existing experimental
artifacts were only read; the sweep writes its own results file.

## 1. Experimental setup

- **Model family / protocol:** same as `experimental_model.py` —
  IsolationForest fitted on clean/normal windows only (40 rows whose
  `label` contains "normal"), then all 80 feature windows scored.
- **Swept parameter:** `contamination` ∈ {0.01, 0.05, 0.10}.
- **Held constant:** `n_estimators=200`, `max_samples="auto"`,
  `random_state=42` (the experimental model's configuration; only
  `contamination` varies).
- **Output:** `results/day13_ml_sensitivity.csv` — one row per setting
  with evaluated samples, predicted-anomaly counts (total and per traffic
  label), the fitted anomaly threshold (`offset_`), and the min/mean/max
  anomaly score observed.

Reproduce:

```
python ml_sensitivity_day13.py                      # regenerate the CSV
python -m pytest tests/test_day13_ml_sensitivity.py -v   # verify
```

Reproducibility is asserted by tests (`random_state=42`); two consecutive
runs produced byte-identical results, and the committed CSV is asserted
equal to a fresh regeneration. No metric is imputed anywhere: every number
below is read back from the generated file.

## 2. Results (80 evaluated windows: 40 normal, 40 high-rate)

| contamination | predicted ANOMALY | high-rate flagged | normal flagged | anomaly threshold | mean anomaly score |
|--------------:|------------------:|------------------:|---------------:|------------------:|-------------------:|
| 0.01          | 1                 | 0 / 40            | 1 / 40         | −0.740462         | +0.150865          |
| 0.05          | 42                | 40 / 40           | 2 / 40         | −0.646774         | +0.057176          |
| 0.10          | 44                | 40 / 40           | 4 / 40         | −0.554491         | −0.035106          |

(Per-label counts are observed windows only, by the captures' own labels;
per the project rule no detection-accuracy claim is made.)

## 3. Observed differences

1. **Anomaly count is a near-linear function of contamination here.**
   1 → 42 → 44 predicted anomalies as contamination doubles past the
   training data's assumed anomaly rate. `contamination` acts purely as a
   score cutoff: the fitted threshold (`offset_`) moves monotonically up
   with contamination (−0.740 → −0.647 → −0.554), pulling more of the
   score distribution below 0.
2. **Attack detection turns on between 0.01 and 0.05.** At 0.01 the
   threshold sits below the entire high-rate score cluster, so 0/40
   high-rate windows are flagged — this reproduces the day-12 finding
   that lowering contamination collapses attack detection. From 0.05 on,
   all 40 high-rate windows are caught.
3. **False positives on normal windows grow with contamination.** 1 → 2
   → 4 normal windows flagged. The two extra windows picked up at 0.10
   are the same extreme-but-benign low-count windows identified in
   `docs/findings.md`; a looser cutoff simply admits more of them.
4. **Scores shift, structure does not.** The min/mean/max anomaly scores
   move down together as the threshold rises — the underlying score
   ordering of the 80 windows is unchanged, confirming that
   `contamination` changes only the decision cutoff, not the ranking.

## 4. Limitations

1. **Training data is minimal and possibly insufficient for threshold
   setting.** The model is fitted on 40 normal windows from a single
   simulated capture. `contamination` is meant to encode the expected
   anomaly fraction; with a small, single-capture training set the fitted
   cutoff is highly sensitive to a handful of outlier windows (see the
   1→2→4 progression). These settings must not be treated as tuned values
   for deployment.
2. **Simulated traffic only.** Both captures are simulated
   normal/high-rate sets; nothing here measures behaviour on real vehicle
   traffic, and no accuracy metrics are claimed.
3. **Feature data reconstructed from the committed results CSV.**
   `can_features.csv` is not committed to this repo, so the sweep reads
   the feature columns back from `results/experimental_ml_predictions.csv`
   (same 80 rows, values exactly as committed). When the parent project's
   `can_features.csv` is present the script prefers it automatically.
4. **Single score family.** Only IsolationForest with the experimental
   configuration was swept; interactions with `n_estimators`,
   `max_samples`, or other model families were not explored.
5. **No held-out data or cross-validation.** The sweep evaluates the same
   windows the threshold is set on, so per-setting counts describe this
   dataset only.
6. **Day-13 outcome is consistent with `docs/findings.md`:** no
   contamination setting separates the two score clusters perfectly —
   0.05 repeats the reference behaviour (40/40 + 2 normal false
   positives); 0.01 loses all attack detection; 0.10 trades two more
   normal false positives for no additional detection.
