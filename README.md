# CAN-Sentinel
### Automotive ECU Intrusion Detection System

CAN-Sentinel is an automotive cybersecurity project focused on visualizing Controller Area Network (CAN) traffic and supporting the identification of potentially suspicious communication patterns using traffic analysis and machine-learning techniques.

The project aims to compare normal CAN traffic with simulated high-rate traffic and provide dashboards for reviewing traffic statistics and detection results.

> **Current Status:** CAN-Sentinel includes a PyQt5 dashboard for sample-data visualization and CSV loading, along with an HTML report dashboard for reviewing detector summaries, evaluation metrics, and edge-case validation results. The HTML dashboard displays available dataset metadata and clearly identifies limitations of synthetic or previously generated data.

---

## Table of Contents

1. Project Overview
2. Project Objectives
3. Dashboard Features
4. Dashboard Metrics
5. Technologies Used
6. Project Structure
7. Installation
8. Running the Dashboard
9. Generating the HTML Report Dashboard
10. Loading Traffic Data from CSV
11. Sample CSV Format
12. Week-wise Progress
13. Pending Integration Work
14. Limitations
15. Team Responsibilities

---

## 1. Project Overview

Modern vehicles use the Controller Area Network (CAN) protocol to enable communication between Electronic Control Units (ECUs).

Monitoring CAN traffic can help identify unusual communication patterns, including unexpectedly high message rates.

CAN-Sentinel is being developed to support this process through:

- CAN traffic simulation and analysis.
- Feature extraction for machine-learning models.
- Model evaluation and prediction testing.
- Graphical dashboards for displaying traffic statistics.
- Comparison of normal and simulated high-rate traffic.
- Documentation of integration and testing requirements.

The dashboards provide visual interfaces for reviewing available traffic data and detector results.

## 2. Project Objectives

The main objectives are:

- Visualize CAN traffic statistics through graphical interfaces.
- Compare normal and simulated high-rate traffic.
- Display message counts and traffic rates.
- Present detection statuses from available detector outputs.
- Support loading traffic and result data from CSV files.
- Integrate the dashboard with the project's feature-extraction and machine-learning pipeline.
- Document implementation progress, testing requirements, and remaining integration work.

---

## 3. Dashboard Features

The project includes a PyQt5 desktop dashboard and an HTML report dashboard.

### 3.1 PyQt5 Dashboard

The desktop dashboard is developed using Python and PyQt5.

The interface supports:

- CAN-Sentinel project heading.
- Summary cards for traffic statistics.
- CAN traffic overview table.
- CSV-loading control.
- Sample-data refresh control.
- Data-source and last-updated information.

### 3.2 HTML Report Dashboard

The HTML report dashboard is generated using:

`src/generate_dashboard_report.py`

The generated report is available at:

`reports/detector_dashboard.html`

Its features include:

- Overall ML Detector summary.
- Rate-Based Detector summary.
- Hybrid Detector summary.
- Normal and high-rate traffic comparison.
- Detector evaluation metrics.
- Edge-case validation results.
- Input dataset information.
- Model file information.
- Rate-based threshold information.
- Report generation timestamp.
- Sample count.
- Synthetic-data limitation notice.

### 3.3 Traffic Comparison

The dashboard supports displaying normal and simulated high-rate traffic.

| Field | Description |
|---|---|
| Traffic Type | Normal or simulated high-rate traffic |
| CAN ID | Identifier associated with the traffic record |
| Message Count | Number of messages represented by the record |
| Messages/sec | Observed or calculated message rate |
| Detection Status | Classification or status associated with the record |

### 3.4 Detector Summaries

The HTML dashboard displays summaries for three detectors:

- **ML Detector:** Displays available machine-learning prediction counts.
- **Rate-Based Detector:** Displays predictions based on traffic-rate analysis.
- **Hybrid Detector:** Displays available hybrid detector predictions.

The displayed values depend on the available CSV result files.

### 3.5 CSV Loading

The PyQt5 dashboard includes a CSV-loading interface for selecting a local data file and displaying its contents.

The CSV format must match the columns expected by the dashboard. Files with missing columns or invalid values should produce a clear error message.

### 3.6 Demonstration Data

Sample data can be used to test the layout and demonstrate how normal and high-rate traffic may appear.

**Important:** Demonstration values and sample detection statuses are illustrative only. They must not be presented as actual CAN observations, verified attack detections, or machine-learning predictions.

---

## 4. Dashboard Metrics

### 4.1 Traffic Metrics

**Total Messages**

The sum of message counts represented by the loaded records.

**Unique CAN IDs**

The number of distinct CAN identifiers in the loaded dataset.

**Normal Messages**

The total message count associated with records classified as normal by the selected classification source.

**Anomalies**

The number of records or messages classified as anomalous. The dashboard must specify whether this metric counts records or individual messages.

**Messages per Second**

The rate at which CAN messages are observed or generated.

When a reliable message count and simulation duration are available:

`Messages per second = Message count / Duration in seconds`

A message count must not be treated as a messages-per-second value without confirming the measurement interval.

### 4.2 Detection Status

Possible statuses include:

- Normal
- Suspicious
- Anomaly
- Unknown

Actual statuses must come from the project's documented classification logic or verified model output.

A high message rate alone does not prove that an attack has been detected.

### 4.3 Detector Evaluation Metrics

The HTML report displays the following evaluation metrics:

| Metric | Description |
|---|---|
| TP | True Positive — attack correctly identified |
| FP | False Positive — normal traffic incorrectly identified as an attack |
| TN | True Negative — normal traffic correctly identified |
| FN | False Negative — attack incorrectly identified as normal |
| Precision | Correct positive predictions out of all positive predictions |
| Recall | Correctly identified positive cases out of all actual positive cases |
| F1-score | Harmonic mean of precision and recall |
| Accuracy | Overall percentage of correct predictions |

These metrics are displayed for ML, Rate-based, and Hybrid detectors when evaluation data is available.

### 4.4 Edge-Case Validation

The dashboard displays available edge-case validation scenarios, including:

- Burst Traffic
- Replay Pattern
- Normal-to-High-Rate Transition

The validation report distinguishes baseline results from production detector execution. A `NOT RUN` value means the production detector was not executed for that scenario.

---

## 5. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| PyQt5 | Graphical desktop dashboard |
| HTML | Report dashboard structure |
| CSS | Dashboard styling |
| CSV | Traffic-data and result exchange format |
| Machine Learning | Traffic classification and evaluation |
| Git | Version control |
| GitHub | Source-code collaboration and project hosting |

The precise model, feature-extraction methods, and CAN logging implementation are maintained in their respective project modules.

---

## 6. Project Structure

The current project structure includes:

```text
CAN-Sentinel/
│
├── dashboard.py
├── README.md
├── requirements.txt
├── sample_traffic.csv
│
├── src/
│   └── generate_dashboard_report.py
│
├── reports/
│   └── detector_dashboard.html
│
├── results/
│   ├── detector_evaluation_metrics.csv
│   ├── edge_case_validation.csv
│   ├── high_rate_traffic.csv
│   ├── integration_results.csv
│   ├── normal_traffic.csv
│   └── rule_baseline_results.csv
│
├── tests/
│   ├── test_dashboard.py
│   └── test_dashboard_metadata.py
│
├── docs/
│   ├── dashboard_spec.md
│   └── dashboard_verification.md
│
└── screenshots/
    ├── dashboard_day1.png.png
    ├── dashboard_progress.png
    └── day5_dashboard_progress.png
```

---

## 7. Installation

### Requirements

- Python 3.x
- Visual Studio Code
- Git
- Required Python packages listed in `requirements.txt`

### Installation Steps

1. Clone the project repository.

```bash
git clone https://github.com/zero-cybersec/CAN-Sentinel.git
```

2. Open the project folder in Visual Studio Code.

3. Open the terminal.

4. Install the required packages.

```bash
pip install -r requirements.txt
```

---

## 8. Running the Dashboard

### 8.1 Run the PyQt5 Dashboard

Run the following command from the project root:

```bash
python dashboard.py
```

The desktop dashboard opens and displays the available sample or loaded traffic data.

### 8.2 Load CSV Data

1. Open the PyQt5 dashboard.
2. Select the CSV-loading option.
3. Choose the required CSV file.
4. The dashboard displays the available records.

The selected CSV must follow the expected data format.

---

## 9. Generating the HTML Report Dashboard

The HTML report dashboard is generated using the existing Python script.

### Step 1: Open the Project Terminal

Make sure the terminal is in the CAN-Sentinel project root directory.

### Step 2: Generate the Report

Run:

```bash
python src/generate_dashboard_report.py --force
```

The `--force` option allows the existing HTML report to be updated.

### Step 3: Open the HTML Report

Open the generated file:

```text
reports/detector_dashboard.html
```

The report displays:

- Detector prediction summaries.
- Normal and high-rate traffic results.
- Evaluation metrics.
- Edge-case validation results.
- Dataset and report metadata.
- Synthetic-data limitation notice.

The report is generated from the available CSV files. It does not independently execute the machine-learning model.

---

## 10. Loading Traffic Data from CSV

The project uses CSV files to store and exchange traffic and evaluation results.

Important input and result files include:

| File | Purpose |
|---|---|
| `integration_results.csv` | Integration and detector prediction results |
| `detector_evaluation_metrics.csv` | Detector evaluation metrics |
| `edge_case_validation.csv` | Edge-case validation results |
| `normal_traffic.csv` | Normal traffic data |
| `high_rate_traffic.csv` | High-rate traffic data |
| `rule_baseline_results.csv` | Rule-based baseline results |

The HTML report reads the available CSV files and displays their contents.

Missing or empty input files should be handled with clear error messages.

---

## 11. Sample CSV Format

An example of the traffic data format is:

```csv
timestamp,can_id,message_count,traffic_type
1.0,0x100,5,normal
1.2,0x200,8,normal
1.4,0x300,50,high_rate
```

The actual CSV columns depend on the data-generation and integration scripts.

The dashboard must use the correct column names and data types expected by the corresponding script.

---

## 12. Week-wise Progress

### Week 1 — Dashboard Development

- Initial dashboard setup.
- PyQt5 interface development.
- CSV loading support.
- Traffic statistics display.
- Dashboard layout improvements.
- Dashboard documentation.

### Week 2 — Detector Integration and Evaluation

- Investigation of normal and high-rate traffic features.
- Isolation Forest model investigation.
- Hybrid detector review.
- Comparison of ML and rule-based predictions.
- Detector evaluation metrics support.
- Dashboard specification updates.

### Week 3 — Integration and Validation

- Dashboard integration with available CSV results.
- ML, Rate-based, and Hybrid detector summaries.
- Evaluation metrics display.
- Edge-case validation result display.
- Dashboard test development.
- Metadata display and verification.
- Synthetic-data limitation notice.

---

## 13. Pending Integration Work

The following activities require further verification or implementation:

- Integration with verified machine-learning predictions.
- Testing with actual CAN traffic datasets.
- Verification of the model file and its execution.
- Verification and documentation of the rate-based threshold.
- Production detector testing for edge-case scenarios.
- End-to-end validation of the complete detection pipeline.
- Verification using real vehicle CAN traffic where available.

These activities must be marked complete only after actual implementation and testing.

---

## 14. Limitations

- Dashboard values depend on the available CSV data.
- Sample data is used for demonstration and interface testing.
- The HTML report generator displays existing results; it does not independently execute the ML model.
- Model file and rate-based threshold values are shown as unavailable when they cannot be verified from the current report inputs.
- Edge-case baseline validation does not prove that the production detector has executed successfully.
- Evaluation metrics must be checked against the underlying evaluation output before interpreting them as final model performance.
- Synthetic or previously generated data must not be treated as proof of real-world production performance.
- Full end-to-end integration and real-world validation remain necessary.

---

## 15. Team Responsibilities

The project is developed collaboratively by a team of four members.

| Team Member | Responsibility |
|---|---|
| Avinash | Team Lead and CAN Setup |
| Nikhil | Machine Learning |
| Zeeshan | Attack Simulation |
| Rena | Dashboard and Documentation |

Each member contributes to the development, testing, integration, and documentation of the CAN-Sentinel project.

---

## Conclusion

CAN-Sentinel provides a foundation for automotive CAN-network traffic analysis and intrusion detection.

The project includes a PyQt5 desktop dashboard and an HTML report dashboard for reviewing available traffic statistics, detector predictions, evaluation metrics, and edge-case validation results.

Further integration and testing are required to verify the complete detection pipeline and its performance using actual CAN traffic data.