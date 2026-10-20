# CAN-Sentinel Dashboard Specification

## 1. Purpose

The CAN-Sentinel dashboard provides a visual interface for
reviewing Controller Area Network (CAN) traffic statistics
and displaying intrusion-detection results.

The dashboard is designed to compare normal traffic with
simulated high-rate traffic and, when available, display
results produced by the machine-learning model.

The current dashboard uses demonstration data for layout
and testing. Actual detection performance has not yet been
verified through the integrated model pipeline.

## 2. Current Implementation Status

### Implemented Features

- PyQt5-based graphical dashboard.
- Dark-themed user interface.
- Summary cards for total messages and unique CAN IDs.
- Summary cards for normal and suspicious records.
- Traffic table for normal and simulated high-rate traffic.
- Message count and messages-per-second columns.
- CSV file selection and loading interface.
- CSV input validation and error messages.
- Sample-data refresh functionality.
- Visual distinction between normal and suspicious statuses.

### Pending Work

- Validate the dashboard against the team's verified
  traffic simulation datasets.
- Confirm compatibility with the integration script's
  model output format.
- Connect actual model predictions to the dashboard.
- Verify summary statistics against the loaded dataset.
- Test CSV loading with malformed and incomplete files.
- Clearly distinguish actual model predictions from
  demonstration labels.

## 3. Dashboard Metrics

### 3.1 Total Messages

Description:
The sum of message counts across the currently displayed
traffic records.

Calculation:
Total Messages = Sum of message_count.

Note:
If each CSV row represents a separate CAN ID or traffic
group, this calculation represents the total reported
message count across those records.

### 3.2 Normal Messages

Description:
The total number of messages associated with records
classified as normal.

Calculation:
Normal Messages = Sum of message_count for records
whose verified classification is Normal.

The dashboard must use an explicitly defined classification
source. Sample labels must not be treated as verified results.

### 3.3 Anomalies

Description:
The number of records or messages classified as anomalous
by the connected detection system.

The dashboard must specify whether the displayed value
counts anomalous records or anomalous messages.

Until actual model predictions are integrated, this metric
must be labelled as sample or demonstration data.

### 3.4 Traffic Rate

Description:
The traffic rate indicates how many CAN messages are
observed per second.

Unit:
Messages per second (messages/sec).

The rate should come from verified dataset metadata or
the traffic logger's measurements.

If the CSV provides a message count and simulation duration,
the rate can be calculated as:

Messages per second = Message count / Duration in seconds.

The dashboard must not assume that message_count is a
per-second rate.

### 3.5 Unique CAN IDs

Description:
The number of distinct CAN identifiers in the loaded data.

Calculation:
Count the distinct values in the can_id column.

### 3.6 Detection Status

Possible display values:

- Normal
- Suspicious
- Anomaly
- Unknown

The actual status labels must match the output of the
integrated model or the project's verified classification
logic.

A high traffic rate alone must not be described as a
confirmed attack unless the project's detection logic
supports that conclusion.

## 4. Dashboard Wireframe

The proposed layout is:

+-----------------------------------------------------------+
| CAN-SENTINEL                     [Load CSV] [Refresh Demo]|
| Automotive ECU Intrusion Detection Dashboard              |
+-----------------------------------------------------------+
| Total Messages | Normal Messages | Anomalies | Traffic Rate|
+-----------------------------------------------------------+
|                                                           |
| CAN Traffic and Detection Results                         |
|                                                           |
| Traffic Type | CAN ID | Message Count | Messages/sec |     |
|              |        |               |              |Status|
|-----------------------------------------------------------|
| Normal       | 0x123  | Sample value  | Sample value | ... |
| Normal       | 0x456  | Sample value  | Sample value | ... |
| High-Rate    | 0x123  | Sample value  | Sample value | ... |
| High-Rate    | 0x456  | Sample value  | Sample value | ... |
+-----------------------------------------------------------+
| Data Source | Last Updated | Demo / Model Results         |
+-----------------------------------------------------------+

The wireframe is a logical layout specification.
The existing PyQt5 dashboard already implements much of
this layout.

## 5. Expected CSV Input Format

The dashboard's normalized input format is:

traffic_type,can_id,message_count,messages_per_second,detection_status

Example demonstration data:

traffic_type,can_id,message_count,messages_per_second,detection_status
Normal,0x123,250,25.0,Normal
Normal,0x456,180,18.0,Normal
Simulated High-Rate,0x123,1200,120.0,Suspicious
Simulated High-Rate,0x456,950,95.0,Suspicious

IMPORTANT:
The example values above are illustrative only.
They are not verified simulation results or actual ML predictions.

### Required Columns

| Column | Meaning | Expected Type |
|---|---|---|
| traffic_type | Traffic category | Text |
| can_id | CAN identifier | Text |
| message_count | Number of messages | Non-negative integer |
| messages_per_second | Traffic rate | Non-negative number |
| detection_status | Classification or status | Text |

The dashboard should reject files that are missing required
columns or contain invalid numeric values.

## 6. Model Output Integration

The model integration layer must define how raw traffic
features are converted into model input and how model
outputs are represented in the dashboard.

The model's required feature columns must be obtained from
the existing model pipeline. They must not be guessed from
the dashboard CSV schema.

Recommended normalized dashboard output:

- traffic_type
- can_id
- message_count
- messages_per_second
- detection_status

If the model produces numeric labels, the integration
code must map them to meaningful status labels using the
model's documented label mapping.

The dashboard must not invent predictions when model
results are unavailable.

## 7. Integration Workflow

1. Obtain verified normal and high-rate traffic CSV files
   from the attack-simulation team.
2. Review the existing feature-extraction implementation.
3. Confirm the model's required input feature columns.
4. Run both datasets through the existing feature pipeline.
5. Load the existing trained model and generate predictions.
6. Compare predictions with reliable expected labels,
   when those labels are available.
7. Save the integration results in the agreed output format.
8. Normalize the verified results into the dashboard CSV schema.
9. Load the normalized results in the dashboard.
10. Verify the displayed counts, rates, and detection statuses.
11. Capture a screenshot of the dashboard displaying the results.

If the datasets or model outputs are unavailable, document
the missing dependency instead of fabricating results.

## 8. Error Handling

The dashboard should show a clear error message when:

- The CSV file cannot be opened.
- Required columns are missing.
- Numeric values are invalid.
- Message counts or traffic rates are negative.
- The file contains no usable data rows.

If loading fails, the dashboard should preserve the previously
loaded valid data.

## 9. Testing Requirements

The following tests are required:

- Load a valid sample CSV.
- Load a verified normal-traffic dataset after its schema
  has been confirmed.
- Load a verified high-rate dataset after its schema
  has been confirmed.
- Test a CSV file with missing columns.
- Test invalid numeric values.
- Confirm that summary metrics match the loaded records.
- Confirm that model statuses match actual model outputs.
- Verify that demonstration data is clearly labelled.
- Verify that failed CSV loading does not replace valid data.

Testing results must be documented separately from the
design specification.

## 10. Dependencies and Pending Integration

The dashboard depends on outputs from the other project modules:

- Attack simulation: verified normal and high-rate traffic.
- Feature extraction: correctly prepared model input features.
- Machine learning: trained model and documented output labels.
- Integration: prediction results and test evidence.

The dashboard can be developed and tested with sample data
while these dependencies are being completed.

Actual detection performance must only be reported after
the integrated pipeline has been tested with verified data.

## 11. Current Limitations

- The dashboard's demonstration data is not live CAN traffic.
- Demonstration detection statuses are not actual ML predictions.
- Traffic-rate values must be verified against simulation duration
  or trusted logger output.
- Model detection accuracy cannot be established from the
  dashboard display alone.
- Integration depends on the verified datasets and model output.

## 12. Deliverable Status

Completed:
- Dashboard layout and demonstration-data visualization.
- Initial CSV loading implementation.
- Dashboard metrics and input-format specification.

Pending:
- Verification with the team's actual CSV datasets.
- Actual ML prediction integration.
- End-to-end integration testing.
- Final screenshot using verified results.