# Experimental ML — Findings

Date: 2026-10-27

## 1. What was built

`experimental_model.py` (project root) — an experimental variant of
`train_model.py` / `test_model.py`:

- **Same feature contract** as the reference workflow: reads
  `can_features.csv` with columns `message_count`, `avg_interval_ms`,
  `unique_payloads`, `payload_entropy` (same list as `train_model.py`).
- **Same output format** as `test_model.py`: `prediction`
  (NORMAL/ANOMALY) and `anomaly_score` (IsolationForest
  `decision_function`; negative = more anomalous).
- **Same training protocol** as the reference workflow: fitted on
  clean/normal windows only (rows whose `label` contains "normal"),
  scored on all windows.
- **Separate outputs** — the reference pipeline is never written to:

| File | Experimental | Reference (untouched) |
|------|--------------|------------------------|
| Model artifact | `experimental_can_model.joblib` | `can_model.joblib` |
| Results | `results/experimental_ml_predictions.csv` | `model_test_results.csv` |

The results CSV carries both models' outputs: `prediction` /
`anomaly_score` (experimental) and `reference_prediction` /
`reference_anomaly_score` (added for comparison, when
`can_model.joblib` is present).

## 2. Model configuration

| Parameter | Experimental | Reference | Why changed |
|-----------|--------------|-----------|-------------|
| `contamination` | **0.01** | 0.05 | Hypothesis: the reference's 2 false positives on normal windows come from the 0.05 cutoff sitting too close to low-count normal windows; 0.01 should drop the cutoff below them. |
| `n_estimators` | **200** | 100 | Halves split-randomness noise in scores. |
| `max_samples` | "auto" | "auto" | Unchanged. |
| `random_state` | 42 | 42 | Reproducibility. |

## 3. Verification (all passing — `tests/test_experimental_ml.py`)

15 tests cover the completion criteria:

- **Prediction count** — output has exactly 80 rows, matching the 80
  feature rows (40 normal + 40 high-rate windows).
- **Feature-row alignment** — output rows are in the same
  `source`/`window`/`can_id` order as `can_features.csv`, for both the
  generated run and the committed results file. Predictions are always
  NORMAL/ANOMALY, and ANOMALY is asserted exactly when the score < 0.
- **Invalid-input handling** — `load_features` raises a clear
  `ValueError` for missing feature columns, non-numeric values, NaNs,
  empty files, and missing files; training errors out if no normal-
  labeled rows exist.
- **Reference artifacts unchanged** — SHA-256 of `can_model.joblib`,
  `model_test_results.csv`, `can_features.csv` verified identical before
  and after every run, and the committed reference results still parse.
- **Reproducibility** — two independent runs (retrained each time) give
  byte-identical predictions and scores (`random_state=42`).

Reproduce:

```
python experimental_model.py                       # regenerate deliverable
python -m pytest tests/test_experimental_ml.py -v  # run the tests
```

## 4. Test results

Reference run (`model_test_results.csv`) vs. experimental run
(`results/experimental_ml_predictions.csv`), same 80 feature windows:

| Traffic (simulated) | Windows | Reference ANOMALY | Experimental ANOMALY |
|---------------------|---------|-------------------|----------------------|
| normal_traffic_new  | 40 | 2 | **1** |
| high_rate_traffic   | 40 | **40** | **0** |

Agreement between the two models on the same rows: 39/80 (48.75%).

**The experimental hypothesis was rejected.** Lowering
`contamination` 0.05 → 0.01 removed one normal false positive but
collapsed attack detection entirely (0/40 high-rate windows flagged).

## 5. Why (score evidence)

- All 40 high-rate windows form a single tight score cluster
  (experimental `decision_function` = +0.039 for every one of them).
- The two extreme low-count normal windows (2 and 11 messages per
  window) score *below* the entire high-rate cluster
  (−0.046 vs. +0.039).
- With `contamination=0.01`, the anomaly threshold is placed below that
  entire cluster — so the "attack" windows all read NORMAL.
- **No threshold value separates these windows perfectly**: any cutoff
  that catches all 40 high-rate windows also flags the 2 extreme normal
  windows. The reference configuration (contamination=0.05: 40/40
  detected, 2/40 false positives) is already the best achievable with
  this 4-feature model on this data.

Conclusion: the reference model's 2 false positives are a structural
limitation of the current features, not a tuning mistake — and the
contamination threshold is fragile near the gap between the two clusters.

## 6. Limitations

1. **Simulated traffic only.** Both captures are simulated
   high-rate/normal sets; nothing here measures detection accuracy on a
   real vehicle (per the project note, no accuracy claims are made).
2. **Window-level detection only.** The features summarize a whole
   1-second window; targeted ID injection that keeps the window average
   normal is invisible to this model family. Measuring that sensitivity
   is Phase D of the evaluation plan and has not been done.
3. **Tiny training set.** 40 normal windows from a single capture; the
   model has seen no variation in CAN IDs, vehicles, or benign bursts.
4. **Threshold fragility.** As the rejected hypothesis shows, the
   contamination cutoff sits inside a narrow score gap; small changes to
   the normal-traffic profile can flip the outcome.
5. **Reference-vs-experimental comparison is apples-to-apples only for
   these 80 windows**; no cross-validation or held-out capture was used.
6. **Zeeshan's own model file** has not been shared yet (Phase B of the
   evaluation plan); all reference numbers describe the local reference
   model, not his.

## 7. Recommendation

Keep the reference configuration (`contamination=0.05`) as the active
model. Do not lower `contamination`. Future improvement should target
features, not the threshold: per-window min/max interval, per-CAN-ID
rates, and ID-frequency deviation would let the model separate the
extreme-but-benign low-count windows from true floods. Phase C (labeled
metrics) and Phase D (robustness sweep) of `EVALUATION_PLAN.md` remain
the gates before any detection-accuracy statement.
