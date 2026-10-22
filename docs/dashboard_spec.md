# CAN-Sentinel Dashboard Specification & Compatibility Checklist

**Project:** CAN-Sentinel  
**Module:** Dashboard & Documentation  
**Last Updated:** 22 October 2026  
**Status:** CSV schema reviewed; complete dashboard integration verification pending.

---

## 1. Purpose

This document defines the CAN-Sentinel dashboard requirements, expected CSV input formats, model-output mapping, validation rules, testing requirements, and integration status.

The dashboard is intended to display CAN traffic statistics and detection results produced by the CAN-Sentinel traffic analysis pipeline.

The dashboard must distinguish between:

- Normal traffic.
- Traffic flagged by rule-based detection.
- Traffic classified by the machine learning model.
- Simulated high-rate traffic used for testing.

Sample or simulated traffic must not be presented as verified real-world attack detection.

This document also records compatibility findings from the available baseline and integration CSV files.

---

## 2. Current Implementation Status

The repository contains the following dashboard-related files:

- `dashboard.py`
- `sample_traffic.csv`
- `docs/dashboard_spec.md`

The team integration branch also contains:

- `results/rule_baseline_results.csv`
- `results/integration_results.csv`
- `results/normal_traffic.csv`
- `results/high_rate_traffic.csv`

The two result CSV schemas have been reviewed through their GitHub previews.

### Verified observations

1. The baseline CSV contains a `prediction` column with rule-based classifications.
2. The integration CSV contains `ml_prediction`, `anomaly_score`, `rate_based_prediction`, and `prediction`.
3. The visible high-rate rows show `ml_prediction` as `NORMAL`, while `rate_based_prediction` is `HIGH_RATE_SUSPECTED`.
4. The existing sample dashboard CSV has a different schema from the integration output.

### Remaining work

- Confirm the complete result-file contents and dataset-level metrics.
- Verify the model's anomaly-score interpretation.
- Confirm how the integration pipeline creates the final `prediction` column.
- Test the dashboard with actual integration output.
- Confirm that displayed values are mapped to the correct source fields.

**The existence of integration result files does not, by itself, prove that the dashboard is fully integrated or that the model successfully detects high-rate traffic.**

---

## 3. Dashboard Layout

The dashboard should present traffic statistics and detection information in a readable format.

### Proposed layout

```text
+--------------------------------------------------------------+
|                    CAN-Sentinel Dashboard                   |
+--------------------------------------------------------------+
| Total Messages | Unique CAN IDs | Normal | Suspicious        |
+--------------------------------------------------------------+
| Traffic Source | CAN ID | Message Count | Message Rate       |
+--------------------------------------------------------------+
| ML Prediction | Anomaly Score | Baseline Prediction          |
+--------------------------------------------------------------+
|                    Traffic Results Table                     |
+--------------------------------------------------------------+
| Data Source / Validation Status / Integration Status         |
+--------------------------------------------------------------+
```

### Display requirements

- Display available traffic statistics.
- Display the traffic source or source filename.
- Display CAN IDs and message counts.
- Display the ML prediction separately from the rule-based prediction.
- Display the anomaly score only when a valid score is available.
- Identify whether the displayed data is sample data or integration output.
- Show appropriate validation messages when required columns are missing.

The layout is a specification. Actual implementation behavior must be verified by running and testing the dashboard.

---

## 4. Dashboard Metrics

### 4.1 Total Messages

The total number of messages represented by the currently loaded dataset.

The calculation must use the actual meaning of the input data. If each row represents an aggregate window rather than an individual CAN message, the dashboard must not simply count rows as messages.

### 4.2 Unique CAN IDs

The number of distinct CAN identifiers in the loaded data.

Candidate field:

`can_id`

### 4.3 Normal and Suspicious Results

The dashboard may display counts of normal and suspicious classifications.

These counts must be derived from the correct prediction field and its documented label mapping.

Do not combine ML predictions and baseline predictions into one metric without explicitly defining the calculation.

### 4.4 Messages Per Second

The current sample CSV contains a `messages_per_second` column.

However, neither the visible baseline CSV schema nor the visible integration CSV schema contains a direct `messages_per_second` column.

The integration output contains:

- `message_count`
- `avg_interval_ms`

A message-rate value must be calculated only after the aggregation window and interval definitions have been verified.

Do not assume that the average interval alone is sufficient to calculate the correct rate for every aggregation window.

### 4.5 ML Prediction

Candidate field:

`ml_prediction`

Expected values observed in the integration output include:

- `NORMAL`
- `ANOMALY`

These values should be displayed as model predictions, not automatically treated as confirmed real-world attack labels.

### 4.6 Anomaly Score

Candidate field:

`anomaly_score`

The integration output contains numeric values in this column.

The score's meaning, direction, range, and any threshold for classification must be verified against the model implementation before the dashboard interprets it.

Do not assume that a higher score always means a higher anomaly risk.

### 4.7 Rule-Based Prediction

Candidate integration field:

`rate_based_prediction`

The baseline CSV uses:

`prediction`

Examples visible in the baseline output include:

- `NORMAL_BY_BASELINE`
- `HIGH_RATE_SUSPECTED`

These labels represent rule-based results, not the Isolation Forest model's predictions.

---

## 5. Expected CSV Input Format

The repository currently contains multiple CSV schemas. They serve different purposes and must not be treated as interchangeable without mapping.

### 5.1 Existing Dashboard Sample CSV

File:

`sample_traffic.csv`

Observed header:

```csv
traffic_type,can_id,message_count,messages_per_second,detection_status
```

Observed sample rows:

```csv
Normal,0x123,250,25,Normal
Normal,0x456,180,18,Normal
Simulated High-Rate,0x123,1200,120,Suspicious
Simulated High-Rate,0x456,950,95,Suspicious
```

This file provides sample traffic statistics and sample detection statuses.

Its `detection_status` values must not be represented as verified ML predictions unless the file is explicitly populated by the actual detection pipeline and that provenance is verified.

### 5.2 Rule-Based Baseline Output

File:

`results/rule_baseline_results.csv`

The visible header is:

```csv
source_file,dataset,can_id,window_start_message,message_count,avg_interval_ms,min_interval_ms,threshold_ms,prediction
```

Field descriptions:

| Column | Meaning |
|---|---|
| `source_file` | Source dataset filename |
| `dataset` | Dataset identifier |
| `can_id` | CAN identifier |
| `window_start_message` | Starting message index for the evaluated window |
| `message_count` | Number of messages in the window |
| `avg_interval_ms` | Average message interval in milliseconds |
| `min_interval_ms` | Minimum message interval in milliseconds |
| `threshold_ms` | Interval threshold used by the baseline |
| `prediction` | Rule-based classification |

The visible examples include `NORMAL_BY_BASELINE` and `HIGH_RATE_SUSPECTED`.

There is no dedicated `anomaly_score` column in this schema.

There is also no direct `messages_per_second` or `traffic_source` column. The `source_file` field identifies a filename, not a separate traffic-source category.

### 5.3 ML Integration Output

File:

`results/integration_results.csv`

The visible header is:

```csv
source_file,can_id,message_count,avg_interval_ms,unique_payloads,payload_entropy,ml_prediction,anomaly_score,rate_based_prediction,prediction
```

Field descriptions:

| Column | Meaning |
|---|---|
| `source_file` | Source dataset filename |
| `can_id` | CAN identifier |
| `message_count` | Number of messages represented by the result row |
| `avg_interval_ms` | Average message interval in milliseconds |
| `unique_payloads` | Number of unique payloads represented |
| `payload_entropy` | Payload entropy feature or statistic |
| `ml_prediction` | Machine learning prediction |
| `anomaly_score` | Numeric score produced by the integration pipeline |
| `rate_based_prediction` | Rule-based or rate-based prediction |
| `prediction` | Combined or final prediction; exact generation logic must be verified |

The exact meaning of the final `prediction` column must be confirmed by inspecting the integration code.

Do not assume that it always represents the ML model's output.

### 5.4 Schema Compatibility Summary

| Dashboard requirement | Sample CSV | Baseline CSV | Integration CSV |
|---|---|---|---|
| Traffic type | `traffic_type` | `dataset` | No direct equivalent shown |
| Traffic source | No dedicated field | `source_file` | `source_file` |
| CAN ID | `can_id` | `can_id` | `can_id` |
| Message count | `message_count` | `message_count` | `message_count` |
| Messages per second | `messages_per_second` | Not present | Not present |
| ML prediction | Not present | Not present | `ml_prediction` |
| Anomaly score | Not present | Not present | `anomaly_score` |
| Rule-based prediction | `detection_status` is sample status | `prediction` | `rate_based_prediction` |
| Final prediction | Not present as a verified model output | No separate field | `prediction` |

---

## 6. Dashboard CSV Compatibility Checklist

This checklist compares the documented dashboard requirements with the visible result-file schemas.

### 6.1 Required Columns

| Requirement | Expected or candidate field | Finding | Status |
|---|---|---|---|
| CAN ID | `can_id` | Available in all three schemas | Compatible field |
| Message count | `message_count` | Available in all three schemas | Compatible field |
| Traffic source | `traffic_source` or mapped source field | Integration files use `source_file` | Mapping required |
| Prediction label | `prediction_label` or mapped prediction field | Integration output has `ml_prediction` and `prediction` | Mapping required |
| Anomaly score | `anomaly_score` | Present in integration output only | Available in integration schema |
| Message rate | `messages_per_second` | Present in sample CSV, absent from visible result schemas | Derivation or pipeline change required |
| Baseline prediction | Baseline `prediction` or integration `rate_based_prediction` | Available | Keep separate from ML output |

### 6.2 Prediction Label Mapping

The integration output contains two relevant fields:

- `ml_prediction`
- `prediction`

The baseline output contains:

- `prediction`

Recommended mapping:

- Display `ml_prediction` in the dashboard's **ML Prediction** field.
- Display `rate_based_prediction` in the dashboard's **Rule-Based Prediction** field.
- Display integration `prediction` as **Final Prediction** only after confirming its generation logic.

Do not rename the baseline's `prediction` field to `ml_prediction`. They represent different outputs.

### 6.3 Anomaly Score Mapping

Map the integration output's `anomaly_score` to the dashboard's **Anomaly Score** field.

Before using the value to classify traffic:

1. Inspect the model implementation.
2. Confirm the score's semantics and direction.
3. Confirm any threshold or decision rule.
4. Verify that the dashboard preserves the original score correctly.

The baseline output has no dedicated anomaly-score field. Do not invent a score for it.

### 6.4 Traffic Source Mapping

The integration output contains `source_file`, which can identify the source dataset filename.

A dashboard may display this field as **Source File**.

If the dashboard specifically requires a traffic-source category, such as normal or high-rate traffic, the mapping must be defined and validated. A filename should not silently be treated as a verified attack label.

### 6.5 Observed ML-versus-Baseline Disagreement

In the visible high-rate rows of `integration_results.csv`:

- `ml_prediction` is `NORMAL`.
- `rate_based_prediction` is `HIGH_RATE_SUSPECTED`.
- The final `prediction` field is shown as `HIGH_RATE_SUSPECTED`.

This indicates disagreement between the ML output and the rate-based baseline in the displayed rows.

It does not establish the complete model detection rate, false-positive rate, or overall accuracy. Those require analysis of the complete dataset and verified labels.

### 6.6 Compatibility Conclusion

The integration CSV contains candidate fields for ML prediction and anomaly-score display.

However, the dashboard's documented field names do not exactly match all actual CSV field names. Explicit mapping is required.

Full compatibility must not be declared until the dashboard has been tested with the actual integration output.

---

## 7. CSV Validation and Error Handling

The dashboard should validate a CSV before attempting to display its contents.

### 7.1 File Validation

Check that:

- The file exists and can be opened.
- The file is a valid CSV.
- The header row is present.
- The file contains at least one usable data row.
- Required values are available and correctly typed.

### 7.2 Column Validation

The dashboard must identify the expected input format and use the corresponding field mapping.

For the sample format, validate the documented sample columns.

For integration results, validate the relevant fields, including:

- `source_file`
- `can_id`
- `message_count`
- `ml_prediction`
- `anomaly_score`
- `rate_based_prediction`
- `prediction`

If a required field is absent, report the missing column clearly.

Optional fields may be displayed as unavailable when they are not present. The dashboard must not silently create fake predictions or anomaly scores.

### 7.3 Value Validation

Check that:

- `can_id` is represented consistently.
- Message counts are numeric and valid.
- Interval values are numeric where present.
- Anomaly scores are numeric where present.
- Prediction fields contain recognized labels.
- Empty or invalid values are handled without crashing the dashboard.

### 7.4 Error Messages

Useful messages include:

- "Unable to open CSV file."
- "CSV file is empty."
- "Required column is missing."
- "Invalid numeric value found."
- "Anomaly score is not available in this dataset."
- "Actual ML integration has not been verified."

---

## 8. Integration Steps for Verified Model Results

The following steps describe the required workflow. They do not imply that all steps have already been completed.

### Step 1: Identify the output file

Use the actual integration output generated by the team's model and integration workflow:

`results/integration_results.csv`

Do not substitute the sample CSV for model output.

### Step 2: Inspect the schema

Verify the header and available fields.

Confirm that the output contains the expected prediction, score, source, CAN ID, and message-count fields.

### Step 3: Review prediction generation

Inspect the integration code to establish how these fields are produced:

- `ml_prediction`
- `rate_based_prediction`
- `prediction`
- `anomaly_score`

Confirm whether `prediction` represents an ML result, a baseline result, or a combined decision.

### Step 4: Define the field mapping

Map the actual CSV fields to the dashboard fields.

Keep the ML and rule-based results separate so that disagreements remain visible.

### Step 5: Validate score semantics

Determine how the model's score is calculated and interpreted.

Do not invent a classification threshold or assume the score's direction without code-level evidence.

### Step 6: Load actual results

Update or configure the dashboard to read the verified integration output using the documented mapping.

Ensure that the displayed data source is clearly identified.

### Step 7: Test both datasets

Evaluate the normal and high-rate datasets separately.

Verify the number of rows processed, available predictions, score values, and displayed classifications.

Compare ML predictions against the rule-based baseline.

### Step 8: Record test results

Document the tested file, schema, mapping, observations, and any failures.

Report full-dataset metrics only after they have been calculated from the complete result data.

### Step 9: Update the status

Mark integration as verified only after successful testing.

Until then, identify the feature as pending verification.

---

## 9. Testing Requirements

The following tests should be performed before declaring the dashboard compatible with the integration output.

### 9.1 Schema Tests

- Verify the expected columns in the sample CSV.
- Verify the expected columns in the baseline CSV.
- Verify the expected columns in the integration CSV.
- Confirm that the correct mapping is selected for each input format.
- Confirm that missing required fields are reported.

### 9.2 Prediction Display Tests

- Verify that `ml_prediction` is displayed as the ML result.
- Verify that `rate_based_prediction` is displayed separately.
- Verify the meaning of the final `prediction` field.
- Confirm that the dashboard does not label sample statuses as verified ML predictions.

### 9.3 Anomaly Score Tests

- Verify that the score is read as a numeric value.
- Verify that the displayed value corresponds to the source CSV.
- Confirm the score's interpretation against the model code.
- Confirm that a missing score is handled without fabricating a value.

### 9.4 Dataset Tests

- Test with the normal traffic dataset.
- Test with the high-rate traffic dataset.
- Compare the traffic intervals and message counts using the verified dataset definitions.
- Record cases where the ML output disagrees with the baseline.

### 9.5 Full-Dataset Evaluation

When the complete labelled dataset is available, calculate and report:

- Total evaluated rows.
- NORMAL and ANOMALY prediction counts.
- False positives.
- False negatives, where ground-truth labels are available.
- Detection rate and other relevant metrics, where the labels and calculation method support them.

Do not derive these metrics from a few visible GitHub preview rows.

---

## 10. Dependencies and Pending Integration

The dashboard's existing sample CSV and the team's integration output use different schemas.

The integration output has the following additional model and feature fields:

- `unique_payloads`
- `payload_entropy`
- `ml_prediction`
- `anomaly_score`
- `rate_based_prediction`

The dashboard mapping must be explicitly defined before these fields can be displayed correctly.

### Pending items

1. Verify the integration code's output-field semantics.
2. Validate the complete baseline and integration CSV files.
3. Confirm how the dashboard calculates or obtains message rate.
4. Test the dashboard with the actual integration output.
5. Verify that displayed labels and scores match the source results.
6. Document the test evidence and final integration status.

The baseline output and ML output must remain distinguishable throughout the dashboard and documentation.

---

## 11. Current Limitations

### 11.1 Sample Data

The dashboard sample file contains illustrative normal and simulated high-rate rows.

These values are not, by themselves, evidence of successful model detection.

### 11.2 Schema Differences

The sample, baseline, and integration CSV files have different column names and purposes.

Explicit field mapping is required.

### 11.3 ML and Baseline Disagreement

The visible high-rate integration rows show `NORMAL` from the ML model while the rate-based baseline flags the traffic as `HIGH_RATE_SUSPECTED`.

This is an observed disagreement that requires investigation.

It must not be presented as proof of successful ML detection.

### 11.4 Anomaly Score Interpretation

The presence of `anomaly_score` does not establish the correct threshold, direction, or meaning of the score.

These details require verification against the model implementation.

### 11.5 Message Rate

The integration CSV does not contain a direct `messages_per_second` field in its visible header.

A validated calculation or an explicit pipeline output field is required if the dashboard needs this metric.

### 11.6 Verification Scope

The current findings are based on visible GitHub CSV headers and sample rows.

Complete dataset statistics, confusion-matrix metrics, and end-to-end dashboard behavior have not been established by those previews alone.

---

## 12. Deliverable Status

**Owner:** Dashboard & Documentation

**Date:** 22 October 2026

| Deliverable | Status | Evidence / Notes |
|---|---|---|
| Review dashboard specification | Completed | Existing specification reviewed |
| Inspect baseline CSV schema | Completed | Visible GitHub header and rows inspected |
| Inspect integration CSV schema | Completed | Visible GitHub header and rows inspected |
| Identify prediction fields | Completed | `ml_prediction`, `rate_based_prediction`, and `prediction` identified |
| Identify anomaly-score field | Completed | `anomaly_score` exists in integration output |
| Identify source mapping | Partially completed | `source_file` is available; source-category mapping requires confirmation |
| Document schema differences | Completed in this specification | Sample, baseline, and integration schemas compared |
| Verify full-dataset metrics | Pending | Complete dataset-level analysis required |
| Verify anomaly-score semantics | Pending | Model implementation must be reviewed |
| Test dashboard with actual integration output | Pending | End-to-end test evidence required |
| Confirm final integration status | Pending | Must follow successful testing |

### Final Conclusion

The team's baseline and integration CSV files contain different schemas. The integration output provides `ml_prediction` and `anomaly_score`, while the baseline output provides a rule-based `prediction` and interval-related fields.

The dashboard can use these fields only after explicit mapping and validation. In the visible high-rate integration rows, the ML prediction is `NORMAL` while the rate-based baseline reports `HIGH_RATE_SUSPECTED`. This discrepancy must remain documented until the complete model evaluation explains the behavior.

**Current status:** CSV schemas reviewed and initial compatibility mapping documented. Full-dataset evaluation, score interpretation, and dashboard integration testing remain pending. No claim of successful high-rate ML detection is made.