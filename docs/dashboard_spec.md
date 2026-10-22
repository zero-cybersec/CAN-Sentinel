# CAN-Sentinel Dashboard Specification & Compatibility Checklist

## 1. Purpose

The CAN-Sentinel dashboard provides a graphical interface for reviewing Controller Area Network (CAN) traffic statistics and displaying traffic classification results.

The dashboard is designed to support comparison between normal traffic and simulated high-rate traffic. It will display traffic metrics and machine-learning predictions when verified integration results become available.

This document describes:

- Dashboard layout and metrics.
- Expected CSV input format.
- Required prediction and traffic-source fields.
- Compatibility checks against integration output.
- CSV validation and error handling.
- Steps required to display verified model results.
- Current implementation status and pending work.

**Important:** Demonstration data is used for interface development and testing. It must not be presented as actual CAN observations or verified machine-learning predictions.

---

## 2. Current Implementation Status

### 2.1 Implemented Features

The current dashboard implementation includes:

- PyQt5-based graphical user interface.
- Dark-themed dashboard layout.
- Summary cards for traffic statistics.
- CAN traffic overview table.
- Display of CAN identifiers and message counts.
- Normal and simulated high-rate traffic presentation.
- Message-count and messages-per-second fields in the dashboard design.
- Detection-status field for displaying classification results.
- CSV-loading interface.
- Sample-data refresh functionality.
- Last-updated information.
- Demonstration-data labelling.

The actual behavior of CSV loading and validation must be tested against the current `dashboard.py` implementation.

### 2.2 Pending Work

The following items require further verification or integration:

- Compare the dashboard's expected CSV schema with the actual integration output.
- Identify missing or mismatched columns.
- Confirm the model's prediction-label format.
- Determine whether the model produces an anomaly score.
- Confirm how the traffic source is identified.
- Validate traffic rates against reliable measurements.
- Connect verified model results to the dashboard.
- Test the dashboard using the actual integration CSV.
- Capture a screenshot showing verified results after successful integration.

---

## 3. Dashboard Layout

The dashboard contains summary cards, a traffic-results table, and data-source information.

### 3.1 Proposed Wireframe

```text
+-----------------------------------------------------------------------+
| CAN-SENTINEL                         [Load CSV] [Refresh Sample Data] |
| Automotive ECU Intrusion Detection Dashboard                          |
+-----------------------------------------------------------------------+
| Total Messages | Normal Messages | Anomalies | Traffic Rate           |
+-----------------------------------------------------------------------+
|                                                                       |
|                    CAN Traffic and Detection Results                  |
|                                                                       |
| Traffic Source | CAN ID | Message Count | Messages/sec | Prediction   |
|----------------|--------|---------------|--------------|--------------|
| Normal         | 0x123  | Example value | Example value | Normal       |
| Normal         | 0x456  | Example value | Example value | Normal       |
| High-Rate      | 0x123  | Example value | Example value | Sample label |
| High-Rate      | 0x456  | Example value | Example value | Sample label |
+-----------------------------------------------------------------------+
| Anomaly Score | Detection Status | Data Source | Last Updated         |
+-----------------------------------------------------------------------+
```

This wireframe is a logical specification. It does not guarantee that every field is already implemented in the current dashboard.

All example rows and values are illustrative.

### 3.2 Dashboard Components

| Component | Purpose |
|---|---|
| Total Messages | Summarizes the number of messages represented by the loaded data |
| Normal Messages | Displays message totals classified as normal |
| Anomalies | Displays anomalous records or messages according to the documented metric |
| Traffic Rate | Displays messages per second |
| Traffic Results Table | Displays traffic details and classification results |
| Load CSV | Selects a CSV file for dashboard display |
| Refresh Sample Data | Refreshes demonstration data, if supported by the current implementation |
| Data Source | Identifies the dataset used for the displayed results |
| Last Updated | Indicates when the dashboard data was last updated |

---

## 4. Dashboard Metrics

### 4.1 Total Messages

**Purpose:** Display the total number of messages represented by the loaded records.

When each record contains a message count:

`Total Messages = Sum of message_count`

The calculation must match the actual dataset's structure. If each row represents an individual CAN message rather than an aggregated count, the total must be calculated accordingly.

### 4.2 Normal Messages

**Purpose:** Display the number of messages classified as normal.

The calculation must use a verified classification source, such as actual model predictions or documented ground-truth labels.

Demonstration labels must not be counted as verified model results.

### 4.3 Anomalies

**Purpose:** Display the number of anomalous records or messages.

The dashboard must document whether this metric counts individual records or the number of messages represented by those records.

An anomaly must be identified using the project's verified detection logic or model output.

A high message rate alone does not prove that an attack has been detected.

### 4.4 Traffic Rate

**Purpose:** Display the number of CAN messages observed or generated per second.

Unit: `messages per second`

When a reliable message count and measurement duration are available:

`Messages per second = Message Count / Duration in Seconds`

The dashboard must use a measured rate or calculate it from a reliable count and duration.

A total message count must not be treated as a messages-per-second value without knowing the measurement interval.

### 4.5 Unique CAN IDs

**Purpose:** Display the number of distinct CAN identifiers.

Calculation:

`Unique CAN IDs = Number of distinct can_id values`

This metric is available only when the dataset contains CAN identifiers.

### 4.6 Prediction Label

**Purpose:** Display the class predicted by the existing machine-learning model.

The prediction label must come from the actual model or integration output.

The dashboard must not create prediction labels randomly or infer them solely from the traffic rate.

### 4.7 Anomaly Score

**Purpose:** Display a model-generated anomaly score if the existing model or integration pipeline provides one.

Before displaying this field, confirm:

- Whether the model actually produces a score.
- What the score represents.
- Its valid range, if applicable.
- Whether a higher or lower score indicates greater abnormality.
- Whether a threshold has been defined and validated.

If the model produces only class labels, the dashboard must not invent an anomaly score.

### 4.8 Traffic Source

**Purpose:** Identify the dataset or traffic category associated with a record.

Examples of possible source labels include:

- Normal
- Simulated High-Rate

These labels must reflect actual dataset metadata or documented source information.

They must not be assigned arbitrarily when loading integration results.

### 4.9 Detection Status

**Purpose:** Present the classification in a human-readable form.

Possible values include:

- Normal
- Suspicious
- Anomaly
- Unknown

The actual labels must match the documented model output and classification logic.

A prediction label and a detection status may represent related information, but their meanings must be defined clearly.

---

## 5. Expected Dashboard CSV Format

The normalized dashboard CSV schema is defined below.

| Column | Required | Description | Expected Data |
|---|---|---|---|
| `traffic_source` | Required for source identification | Identifies the source dataset or traffic category | Text |
| `can_id` | Required when displaying per-ID records | CAN identifier | Text |
| `message_count` | Required for aggregated message statistics | Number of messages represented by the record | Non-negative integer |
| `messages_per_second` | Required when traffic-rate information is available | Observed or reliably calculated rate | Non-negative numeric value |
| `prediction_label` | Required for verified model-prediction display | Model-predicted class | Text or documented model label |
| `anomaly_score` | Conditional | Model-generated anomaly score, if available | Numeric value with documented meaning |
| `detection_status` | Required for a human-readable detection display | Verified or mapped classification | Text |

The actual integration output may use different column names.

The integration CSV must be inspected before implementing mappings or declaring columns missing.

### 5.1 Prediction Label and Detection Status

`prediction_label` should preserve the class produced by the model.

`detection_status` should provide the corresponding human-readable status when a documented mapping is available.

For example, a numeric model label may require mapping to a meaningful class name. The mapping must come from the model's training labels, configuration, or integration implementation.

Do not assume that a particular numeric value means Normal or Anomaly without verifying the mapping.

### 5.2 Anomaly Score

The `anomaly_score` field is conditional on the actual model output.

If the integration pipeline does not produce a score, document the field as unavailable rather than filling it with an invented value.

### 5.3 Traffic Source

The `traffic_source` field should identify the origin or category of each record.

If source information exists only in the dataset filename or metadata, it may be added during preprocessing when the source is known and documented.

---

## 6. Dashboard CSV Compatibility Checklist

### 6.1 Objective

The objective is to compare the expected dashboard CSV format with the actual output generated by the CAN-Sentinel integration pipeline.

The expected integration output path is:

`results/integration_results.csv`

The actual file must be available and inspected before the comparison can be completed.

If the file is unavailable, the review must remain pending.

### 6.2 Compatibility Table

Complete the following table after inspecting the actual integration CSV.

| Expected Dashboard Field | Actual Column Name | Status | Required Action |
|---|---|---|---|
| `traffic_source` | Pending inspection | Pending | Identify source metadata or a documented mapping |
| `can_id` | Pending inspection | Pending | Confirm the CAN identifier field exists |
| `message_count` | Pending inspection | Pending | Confirm message-count availability and meaning |
| `messages_per_second` | Pending inspection | Pending | Verify measured or calculated traffic rate |
| `prediction_label` | Pending inspection | Pending | Identify the model prediction column |
| `anomaly_score` | Pending inspection | Pending | Confirm whether the model produces a score |
| `detection_status` | Pending inspection | Pending | Confirm the classification field or mapping |

### 6.3 Compatibility Status Definitions

Use the following statuses:

- **Match:** The expected field exists and has the correct meaning.
- **Rename Required:** An equivalent field exists under a different column name.
- **Transformation Required:** The field must be derived or mapped using documented logic.
- **Unavailable:** The required information is not provided by the actual output.
- **Pending:** The actual output has not yet been inspected.

Do not mark a column as missing merely because it is absent from the expected format of another file.

Inspect the actual integration output and relevant source code before determining compatibility.

### 6.4 Missing or Mismatched Fields

The following fields require specific verification:

1. **Prediction Label:** Confirm that the integration output contains the model's actual predicted class and establish its meaning.
2. **Anomaly Score:** Confirm whether the model produces a score and document its interpretation.
3. **Traffic Source:** Confirm how the source dataset or traffic category is identified.
4. **Message Count:** Confirm whether counts are available per CAN ID, per dataset, or per record.
5. **Messages per Second:** Confirm whether the rate is supplied directly or can be calculated from reliable duration information.
6. **Detection Status:** Confirm whether the output provides a status or requires a documented mapping from the prediction label.

These are verification requirements, not claims that the columns are definitely missing.

### 6.5 Compatibility Review Procedure

1. Obtain the actual `results/integration_results.csv` file.
2. Inspect the CSV headers and representative data rows.
3. Review the integration script to identify how its output columns are generated.
4. Review the existing model's output format and class-label mapping.
5. Compare each actual column with the expected dashboard fields.
6. Record matching, renamed, transformed, unavailable, and pending fields.
7. Identify any missing or mismatched columns supported by the actual inspection.
8. Define necessary transformations without changing the meaning of the original data.
9. Verify the normalized CSV using a small test file.
10. Load the normalized results into the dashboard.
11. Check the table and summary metrics against the source data.
12. Record test outcomes and unresolved issues.

---

## 7. CSV Validation and Error Handling

The dashboard should validate CSV files before replacing the currently displayed data.

### 7.1 Validation Requirements

The dashboard should check:

- Whether the file can be opened.
- Whether required columns exist.
- Whether column names can be mapped unambiguously.
- Whether numeric fields contain valid values.
- Whether message counts and traffic rates are non-negative.
- Whether the file contains usable records.
- Whether prediction labels follow the documented output format.
- Whether any anomaly score has a documented interpretation.

### 7.2 Error Cases

The dashboard should show a clear error message when:

- The selected file cannot be opened.
- Required columns are missing.
- Numeric values are invalid.
- Negative values appear where they are not valid.
- The CSV file contains no usable records.
- The input schema cannot be mapped to the expected dashboard format.

When loading fails, the previously loaded valid data should remain visible where possible.

The application must not silently substitute fabricated values for missing information.

---

## 8. Integration Steps for Verified Model Results

The dashboard should display actual detection results only after the existing pipeline has generated and validated them.

### Step 1: Obtain Verified Datasets

Obtain the team's verified normal and high-rate traffic CSV files.

Expected paths may include:

- `results/normal_traffic.csv`
- `results/high_rate_traffic.csv`

Confirm the actual paths and file formats with the simulation team.

### Step 2: Inspect the Integration Output

Obtain:

`results/integration_results.csv`

Inspect its column names, data types, and representative rows.

If the output has not been generated, document this dependency and do not fabricate results.

### Step 3: Verify Feature Extraction

Review the existing feature-extraction implementation and identify the exact input features required by the trained model.

Do not assume that the dashboard CSV columns are the same as the model's feature columns.

### Step 4: Verify Model Predictions

Use the existing trained model through the project's established prediction pipeline.

Confirm the meaning of its prediction labels.

If anomaly scores are available, inspect how they are generated and interpreted.

Do not retrain the model or create substitute predictions unless the team determines that doing so is necessary.

### Step 5: Normalize the Results

Map the actual integration output to the dashboard schema.

Preserve the original prediction values and use documented mappings for display labels.

Add traffic-source information only when it can be established from verified dataset metadata or the known source file.

Calculate traffic rates only when reliable message counts and measurement durations are available.

### Step 6: Validate the Normalized CSV

Confirm that the normalized output contains the required fields for the selected dashboard features.

Check numeric values, labels, and record counts.

Document any fields that remain unavailable.

### Step 7: Load Results into the Dashboard

Use the dashboard's CSV-loading interface to load the normalized output.

Verify that:

- Traffic records appear correctly.
- Message counts match the input.
- Traffic rates match the verified data.
- Prediction labels correspond to the model output.
- Detection statuses follow the documented mapping.
- Summary cards agree with the underlying records.

### Step 8: Capture Evidence

After successful validation, capture a screenshot of the dashboard showing the verified results.

Clearly label screenshots containing demonstration data.

### Step 9: Document Test Results

Record:

- The input dataset used.
- The output file tested.
- The validation checks performed.
- Any compatibility issues found.
- Any unresolved limitations.

Successful CSV loading alone does not prove that the model detects attacks correctly.

---

## 9. Testing Requirements

The following tests should be completed.

| Test | Expected Outcome | Status |
|---|---|---|
| Load a valid CSV file | Records display correctly | Pending |
| Load normal traffic results | Counts and rates match verified input | Pending |
| Load high-rate traffic results | Counts and rates match verified input | Pending |
| Verify prediction labels | Labels match actual model output | Pending |
| Verify anomaly score | Score is shown only if actually provided | Pending |
| Verify traffic source | Source corresponds to documented dataset metadata | Pending |
| Load a file with missing columns | Clear error message appears | Pending |
| Load a file with invalid numeric values | Invalid input is rejected | Pending |
| Load an empty CSV | Clear error message appears | Pending |
| Verify summary metrics | Displayed values match underlying records | Pending |
| Verify failed-load behavior | Previous valid data is preserved where possible | Pending |
| Verify sample-data labelling | Demonstration data is clearly distinguished from verified results | Pending |

Update each test status only after the test has actually been performed.

---

## 10. Current Limitations

- Demonstration data does not represent verified live CAN traffic.
- Demonstration statuses are not actual machine-learning predictions.
- The availability of an anomaly score has not been established by this specification.
- Actual integration-output column names must be inspected before compatibility can be confirmed.
- Traffic rates require reliable measurement data.
- Model performance cannot be inferred from the dashboard layout or sample predictions.
- Reliable false-positive and false-negative calculations require suitable expected labels.
- End-to-end detection performance must be assessed through integration testing.

---

## 11. Dependencies

The dashboard depends on the following project components:

### Attack Simulation

Provides verified normal and simulated high-rate traffic datasets.

### Feature Extraction

Transforms traffic data into the features expected by the existing model.

### Machine Learning

Provides the trained model, prediction output, and documented class-label meanings.

### Integration

Runs the required pipeline and produces results that can be checked against the dashboard schema.

### Dashboard

Loads the normalized result data, displays traffic statistics, and presents verified prediction information.

The dashboard specification can be prepared before the other modules are complete, but actual compatibility and detection results must remain unverified until the necessary outputs are available.

---

## 12. Deliverable Status

### Completed Documentation

- Dashboard layout and metric definitions documented.
- Expected dashboard CSV schema documented.
- Prediction-label, anomaly-score, and traffic-source requirements documented.
- CSV compatibility-review procedure documented.
- Missing-column verification process documented.
- Integration steps for displaying verified model results documented.
- Validation and testing requirements documented.
### Day 9 — CSV Compatibility Findings

**Date:** 22 October 2026

#### 1. Available Sample CSV

The currently available CSV file is `sample_traffic.csv`. It contains the following columns:

- `traffic_type`
- `can_id`
- `message_count`
- `messages_per_second`
- `detection_status`

The sample contains Normal and Simulated High-Rate traffic entries.

#### 2. Observed Sample Values

| Traffic Type | CAN ID | Message Count | Messages per Second | Detection Status |
|---|---|---:|---:|---|
| Normal | 0x123 | 250 | 25 | Normal |
| Normal | 0x456 | 180 | 18 | Normal |
| Simulated High-Rate | 0x123 | 1200 | 120 | Suspicious |
| Simulated High-Rate | 0x456 | 950 | 95 | Suspicious |

These values are sample data. They demonstrate different traffic rates but do not, by themselves, establish verified ML detection performance.

#### 3. Compatibility Checklist

| Requirement | Current Finding | Status |
|---|---|---|
| Traffic type | Available as `traffic_type` | Available |
| CAN ID | Available as `can_id` | Available |
| Message count | Available as `message_count` | Available |
| Message rate | Available as `messages_per_second` | Available |
| Detection status | Available as `detection_status` | Available; source of status needs verification |
| Prediction label | No `prediction_label` column in the available sample CSV | Missing from sample |
| Anomaly score | No `anomaly_score` column in the available sample CSV | Missing from sample |
| Traffic source | No `traffic_source` column in the available sample CSV | Missing from sample |
| Rule baseline results | `results/rule_baseline_results.csv` was not found in the inspected project files | Pending |
| Integration results | `results/integration_results.csv` was not found in the inspected project files | Pending |

#### 4. Dashboard Mapping Notes

- Map `can_id`, `message_count`, and `messages_per_second` from their existing columns.
- `traffic_type` may be displayed as the traffic category.
- Do not treat `detection_status` as a verified ML prediction unless its origin is confirmed.
- Map `prediction_label` only when the actual model output provides a prediction label.
- Map `anomaly_score` only when the model or integration output provides a real score.
- Do not invent an anomaly score or create fake integration results.
- A `traffic_source` field may be added to the integration contract if the integration needs to identify the source of each record.

#### 5. Integration Status

The available `sample_traffic.csv` supports sample dashboard data display. Actual compatibility with the rule-based baseline and ML integration outputs remains unverified because the corresponding result files were not found in the inspected project structure.

**Current status: Partial compatibility documented; actual ML integration and result-file verification remain pending.**

### Pending Verification

- Inspect the actual `results/integration_results.csv` file.
- Confirm the actual prediction-label column.
- Confirm whether an anomaly-score field is available.
- Confirm how traffic source is represented.
- Record confirmed missing or mismatched columns.
- Validate the normalized output in the dashboard.
- Capture a screenshot of verified integration results.

**Current conclusion:** The dashboard's expected input format and compatibility-review process are documented. Compatibility with the actual integration output has not been confirmed until the output file is inspected and tested.