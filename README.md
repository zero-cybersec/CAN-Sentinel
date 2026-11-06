CAN-Sentinel
Automotive ECU Intrusion Detection System
CAN-Sentinel is an automotive cybersecurity project focused on monitoring Controller Area Network (CAN) traffic and identifying potentially suspicious communication patterns. It combines traffic analysis, feature extraction, machine-learning predictions, rate-based detection, sequence-based detection, and hybrid decision logic.
The project provides a PyQt5 desktop dashboard and an HTML report dashboard for reviewing traffic statistics, detector outputs, evaluation metrics, and validation evidence.
> **Project status:** The project includes an integrated detector-results workflow and a PyQt5 dashboard that loads `results/integration_results.csv`. The dashboards display the results available in the generated CSV files. Synthetic and previously generated traffic results must not be treated as proof of real-world vehicle performance.
---
Table of Contents
Project Overview
Project Objectives
System Workflow
Detection Methods
Dashboard Features
Dashboard Metrics
Technologies Used
Project Structure
Installation
Running the Project
Input and Result CSV Files
Testing and Validation
Team Responsibilities
Known Limitations
Final Project Status
---
1. Project Overview
Modern vehicles use the Controller Area Network (CAN) protocol to enable communication between Electronic Control Units (ECUs). Monitoring CAN traffic can help identify unusual communication patterns, such as unexpectedly high message rates or repeated message sequences.
CAN-Sentinel supports this process through:
CAN traffic logging and simulation.
Feature extraction from traffic windows.
Machine-learning prediction.
Rate-based traffic analysis.
Sequence-based replay detection.
Hybrid detector output.
Evaluation and validation of detector results.
Dashboards for reviewing traffic statistics and predictions.
The project is intended as a development and evaluation prototype. Further testing with real vehicle CAN traffic is required before making production-performance claims.
2. Project Objectives
Visualize CAN traffic statistics through graphical dashboards.
Compare normal and simulated attack traffic.
Extract useful traffic features for detection.
Review ML, rate-based, sequence-based, and hybrid predictions.
Display detector outputs and available evaluation metrics.
Support CSV-based traffic and result exchange.
Record testing evidence, known limitations, and implementation progress.
3. System Workflow
The main processing workflow is:
```text
CAN Traffic Input
       |
       v
Traffic Logging
       |
       v
Feature Extraction
       |
       +--------------------+
       |                    |
       v                    v
 ML Prediction       Rate-based Detection
       |                    |
       |              Sequence-based Detection
       |                    |
       +----------+---------+
                  |
                  v
          Hybrid Prediction
                  |
                  v
       Integration Results CSV
                  |
          +-------+-------+
          |               |
          v               v
   PyQt5 Dashboard   HTML Report Dashboard
```
The integration output records the available feature values and detector predictions for each processed traffic window. The dashboards read these generated results for display; they do not independently execute the detection models.
4. Detection Methods
4.1 Machine-Learning Detection
The ML component uses the existing trained model to classify extracted traffic features. Its predictions and available anomaly scores are recorded in the integration results.
The trained model and preprocessing pipeline should remain consistent. Model parameters and thresholds should not be changed without a confirmed issue and supporting evidence.
4.2 Rate-Based Detection
The rate-based detector reviews traffic timing and message-rate-related features to identify unusually frequent messages. Its output is recorded separately from the ML prediction.
A high message rate is a suspicious indicator; by itself, it is not proof of a malicious attack.
4.3 Sequence-Based Detection
The sequence detector reviews message-sequence patterns and provides a sequence-related prediction. It supports identifying replay-like patterns in the available simulated traffic.
4.4 Hybrid Detection
The hybrid detector combines the available rate-based, sequence-based, and ML outputs according to the implemented decision logic. The final hybrid prediction is recorded in the integration results.
The exact output depends on the input data and the detector logic used for that run.
5. Dashboard Features
5.1 PyQt5 Desktop Dashboard
Run using `python dashboard.py`.
The desktop dashboard supports:
CAN-Sentinel project heading and dashboard interface.
Summary cards for total windows, total messages, normal hybrid results, and detection alerts.
Detector prediction table.
Loading an integration CSV file.
Reloading the default integration results.
Displaying the source file and last-updated information.
The prediction table includes the available fields:
Source / Scenario
Messages
Average Interval (ms)
Unique CAN IDs
ML Prediction
Anomaly Score
Rate Prediction
Sequence Prediction
Hybrid Prediction
The dashboard reads predictions from the integration CSV. If a CSV was generated before sequence prediction fields were added, those fields may display as unavailable.
5.2 HTML Report Dashboard
The HTML report is generated by:
`src/generate_dashboard_report.py`
Generated report:
`reports/detector_dashboard.html`
The report can display available:
ML, rate-based, and hybrid detector summaries.
Normal and high-rate traffic comparisons.
Detector evaluation metrics.
Edge-case validation results.
Input dataset and model metadata.
Report generation information.
Synthetic-data limitation notices.
Generate or refresh the report from the project root:
```bash
python src/generate_dashboard_report.py --force
```
Open `reports/detector_dashboard.html` in a browser.
> The HTML report displays existing result files. It does not independently run the ML model or detector pipeline.
6. Dashboard Metrics
Metric	Description
Total Windows	Number of processed traffic windows represented in the loaded results
Total Messages	Message count represented by the loaded records
Normal Hybrid	Number of records with a `NORMAL` hybrid prediction
Detection Alerts	Number of records with a non-normal hybrid prediction
Average Interval	Average interval between messages, in milliseconds
Anomaly Score	Score supplied by the ML model, when available
Detector Evaluation Metrics
Metric	Meaning
TP	Attack correctly identified
FP	Normal traffic incorrectly identified as an attack
TN	Normal traffic correctly identified
FN	Attack incorrectly identified as normal
Precision	Correct positive predictions out of all positive predictions
Recall	Correctly identified positive cases out of all actual positive cases
F1-score	Harmonic mean of precision and recall
Accuracy	Overall proportion of correct predictions
Evaluation metrics must be interpreted with their corresponding dataset, labels, and evaluation procedure. Do not assume that dashboard prediction counts are equivalent to evaluation metrics.
7. Technologies Used
Technology	Purpose
Python	Core programming language
PyQt5	Desktop dashboard
HTML and CSS	HTML report dashboard
CSV	Traffic and result data exchange
Machine Learning	Traffic classification
Git	Version control
GitHub	Source-code collaboration and hosting
pytest	Automated testing
8. Project Structure
Important project files and folders include:
```text
CAN-Sentinel/
|
|-- dashboard.py
|-- README.md
|-- requirements.txt
|-- sample_traffic.csv
|-- can_model.joblib
|
|-- src/
|   |-- integration_test.py
|   |-- sequence_detector.py
|   |-- generate_dashboard_report.py
|   |-- train_model.py
|   |-- test_model.py
|   |-- evaluate_detectors.py
|   |-- evaluate_holdout.py
|   |-- extract_features.py
|   |-- can_logger.py
|
|-- results/
|   |-- integration_results.csv
|   |-- detector_evaluation_metrics.csv
|   |-- normal_traffic.csv
|   |-- high_rate_traffic.csv
|   |-- edge_case_validation.csv
|   |-- experimental_ml_predictions.csv
|   |-- holdout_evaluation_metrics.csv
|   |-- holdout_traffic.csv
|   |-- holdout_window_predictions.csv
|   |-- day17_mixed_traffic.csv
|
|-- reports/
|   |-- detector_dashboard.html
|
|-- docs/
|   |-- dashboard_spec.md
|   |-- dashboard_verification.md
|   |-- dashboard_implementation_report.md
|   |-- integration_audit.md
|   |-- integration_findings.md
|   |-- detector_evaluation_report.md
|   |-- final_detection_report.md
|
|-- tests/
|   |-- test_dashboard.py
|   |-- test_dashboard_metadata.py
|   |-- test_end_to_end.py
|   |-- test_evaluate_detectors.py
|
|-- evidence/
    |-- day19_dashboard_verification.png
    |-- day19_test_results.txt
    |-- day19_limitations.txt
```
This is a list of important project files, not an exhaustive listing. Some files may be present only on particular team branches or may be added during integration.
9. Installation
Requirements
Python 3.x
Git
Visual Studio Code or another Python editor
Packages listed in `requirements.txt`
Setup
Clone the repository:
```bash
git clone https://github.com/zero-cybersec/CAN-Sentinel.git
cd CAN-Sentinel
```
Install dependencies:
```bash
pip install -r requirements.txt
```
If the project is already cloned, open the existing project folder and run the installation command from its root directory.
10. Running the Project
Run commands from the CAN-Sentinel project root.
10.1 Run the Integration Pipeline
```bash
python -m src.integration_test
```
This runs the integration module and generates or updates:
`results/integration_results.csv`
The input files and required model/module files must be available in the locations expected by the integration script.
10.2 Run the PyQt5 Dashboard
```bash
python dashboard.py
```
The dashboard loads the default integration results when available. Use Load Integration CSV to select another compatible CSV file or Reload Default Results to reload the default results.
10.3 Generate the HTML Report
```bash
python src/generate_dashboard_report.py --force
```
Then open:
`reports/detector_dashboard.html`
10.4 Run Automated Tests
```bash
python -m pytest tests/ -q
```
The Day 19 test run completed with 8 passed. This is the recorded test result for that run; run the command again after later code changes to verify the current checkout.
11. Input and Result CSV Files
Important CSV files include:
File	Purpose
`normal_traffic.csv`	Normal traffic input
`high_rate_traffic.csv`	High-rate traffic input
`day17_mixed_traffic.csv`	Mixed traffic input used in Day 17 integration validation
`integration_results.csv`	Integrated feature and detector prediction results
`detector_evaluation_metrics.csv`	Available detector evaluation metrics
`edge_case_validation.csv`	Edge-case validation results
`holdout_traffic.csv`	Holdout traffic data
`holdout_window_predictions.csv`	Holdout window prediction results
`holdout_evaluation_metrics.csv`	Holdout evaluation metrics
The exact columns depend on the generating script and result version. Use the column names expected by the relevant integration or dashboard module.
Example traffic CSV:
```csv
timestamp,can_id,message_count,traffic_type
1.0,0x100,5,normal
1.2,0x200,8,normal
1.4,0x300,50,high_rate
```
This is an illustrative format only. It is not a substitute for the actual schema expected by each project script.
12. Testing and Validation
Day 17 Integration Evidence
The recorded integration results contained 120 windows:
Source file	Windows
`day17_mixed_traffic.csv`	80
`normal_traffic.csv`	20
`high_rate_traffic.csv`	20
Total	120
The recorded hybrid prediction distribution was:
Hybrid prediction	Count
`NORMAL`	60
`HIGH_RATE_SUSPECTED`	40
`REPLAY_SUSPECTED`	20
Total	120
These are counts from the recorded integration-results CSV. They are not accuracy, precision, recall, or F1-score values, and they do not independently establish real-world detection performance.
Day 19 Dashboard and Test Evidence
The PyQt5 dashboard was opened with the integration results.
The dashboard displayed the available ML, rate-based, sequence-based, and hybrid prediction columns.
A dashboard verification screenshot was saved under `evidence/`.
The automated test run reported 8 passed.
Test output and a limitations note were saved under `evidence/`.
Validation Notes
Verify expected labels against the corresponding ground-truth labels before reporting scenario-level performance.
Keep ML evaluation metrics separate from dashboard prediction counts.
Do not treat synthetic traffic results as real-vehicle validation.
Re-run the tests after any subsequent code changes.
13. Team Responsibilities
Team Member	Responsibility
Avinash	Team Lead and Integration
Nikhil	Machine Learning
Zeeshan	Attack Simulation
Rena	Dashboard and Documentation
Each member contributes to implementation, testing, integration, evidence preparation, and documentation through their assigned work and Git branch.
14. Known Limitations
Dashboard values depend on the CSV files loaded or generated.
The dashboards display stored results; they do not independently execute all detection models.
Demonstration and synthetic traffic data cannot establish real-world vehicle detection performance.
A high message rate alone does not prove an attack.
Replay detection depends on the quality and representativeness of the available sequence data.
Evaluation metrics are meaningful only when the ground-truth labels, windowing protocol, and evaluation procedure are correct and documented.
Results from different datasets or evaluation protocols should not be compared as if they were produced under identical conditions.
Real vehicle CAN traffic validation and production-environment testing remain necessary.
The system is a prototype and should not be treated as a certified automotive safety or security product.
15. Final Project Status
CAN-Sentinel brings together traffic inputs, feature extraction, ML prediction, rate-based detection, sequence-based detection, hybrid prediction, CSV result generation, and dashboard-based result review.
The PyQt5 dashboard and HTML report provide interfaces for inspecting the available outputs. The recorded Day 17 integration run produced 120 result windows, and the Day 19 automated test run reported 8 passing tests.
The project documentation and evidence describe the tested workflow and its limitations. Final team-wide integration status, ML evaluation conclusions, and attack-simulation validation should be based on the corresponding final reports and commits from the responsible team members.
Important: No claim of real-world vehicle performance, production readiness, or complete attack coverage is made without validation using representative real CAN traffic and a documented evaluation protocol.