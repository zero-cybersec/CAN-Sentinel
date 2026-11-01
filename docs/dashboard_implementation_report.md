# CAN-Sentinel
# Dashboard Development and Documentation Report
## Day-wise Progress: Day 1 to Day 14

**Project:** Automotive ECU Intrusion Detection System  
**Module:** Dashboard Development and Documentation  
**Responsible Member:** Rena  
**Technologies:** Python, PyQt5, HTML, CSS, CSV, Git and GitHub

---

# 1. Project Overview

CAN-Sentinel is an automotive cybersecurity project focused on monitoring Controller Area Network (CAN) traffic and identifying potentially suspicious communication patterns.

Modern vehicles use CAN communication to exchange information between Electronic Control Units (ECUs). Monitoring this communication helps identify unusual traffic patterns, including unexpectedly high message rates.

The dashboard module provides a graphical interface to visualize CAN traffic, compare normal and simulated high-rate traffic, and review available detector results.

The dashboard development includes:

- CAN traffic visualization.
- Normal and high-rate traffic comparison.
- Message count and messages-per-second display.
- ML detection status presentation.
- CSV data loading and processing.
- ML, Rate-based, and Hybrid detector summaries.
- Confusion matrix and evaluation metrics.
- Edge-case validation results.
- HTML report generation.
- Dashboard testing and documentation.

# 2. Day-wise Development Activities

## Day 1 — Dashboard Review and Initial Traffic Visualization

**Objective:**

Review the existing CAN-Sentinel dashboard, identify implemented components, and prepare the dashboard requirements for displaying normal and high-rate traffic statistics.

**Work Performed:**

1. Reviewed the existing dashboard and identified its available components.
2. Examined the dashboard layout for displaying normal and simulated high-rate traffic.
3. Reviewed the required traffic statistics.
4. Identified the important dashboard fields:
   - Message Count.
   - Messages per Second.
   - ML Detection Status.
5. Reviewed the use of placeholder and sample data.
6. Identified the need to distinguish simulated observations from actual ML predictions.
7. Reviewed the existing project documentation and identified pending integration requirements.
8. Supported the initial CAN environment setup using the virtual CAN interface (`vcan0`), mock ECU, and CAN traffic logger.
9. Saved available traffic data in CSV format.
10. Captured initial dashboard progress screenshots.

**Dashboard Requirements:**

| Field | Description |
|---|---|
| Traffic Type | Normal or simulated high-rate traffic |
| Message Count | Number of CAN messages |
| Messages per Second | CAN message transmission rate |
| ML Detection Status | Available ML classification result |

**Data Presentation Requirements:**

- Normal and high-rate traffic should be displayed separately.
- Placeholder values should be clearly labelled.
- Simulated traffic should not be presented as actual ML predictions.
- Detection status should come from verified detector output.
- Existing completed dashboard components should be preserved.

**Outcome:**

The existing dashboard functionality was reviewed, and the required traffic statistics and integration improvements were identified.

**Deliverables:**
- Initial dashboard progress.
- CAN traffic CSV data.
- Dashboard requirements.
- Initial screenshots.

## Day 2 — CAN Setup Verification and Dashboard Progress

**Objective:**

Verify the CAN traffic collection setup and check the availability of traffic data for dashboard development.

**Work Performed:**

1. Verified the virtual CAN interface.
2. Checked the mock ECU communication.
3. Executed the CAN traffic logger.
4. Generated fresh CAN traffic CSV data.
5. Reviewed the collected traffic records.
6. Continued dashboard development.
7. Updated the available project files in the assigned repository branch.

**Outcome:**

The CAN traffic collection environment was checked, and CSV data was available for further dashboard integration.

**Deliverables:**
- CAN setup verification.
- Fresh traffic CSV file.
- Dashboard development progress.

## Day 3 — Dashboard Documentation and Feature Description

**Objective:**

Document the dashboard functionality and prepare the initial project usage information.

**Work Performed:**

1. Worked on the project README.
2. Prepared software requirements information.
3. Documented the dashboard features.
4. Described CAN ID display.
5. Documented message count information.
6. Described NORMAL and ANOMALY detection statuses.
7. Prepared dashboard usage instructions.
8. Reviewed the dashboard layout and available features.

**Outcome:**

The initial dashboard features and software requirements were documented.

**Deliverables:**
- README documentation.
- Software requirements information.
- Dashboard feature descriptions.
- Dashboard screenshots.

## Day 4 — CSV Integration and Result Verification

**Objective:**

Review the available traffic and detector output files to support dashboard integration.

**Work Performed:**

1. Reviewed the integration test script.
2. Checked available detector result CSV files.
3. Compared expected CSV columns with available results.
4. Reviewed attack simulation output files.
5. Worked on displaying available results in the dashboard.
6. Reviewed model prediction output associated with `can_model.joblib`.
7. Checked the integration result structure.

**Outcome:**

The required CSV inputs and integration output structure were reviewed for dashboard reporting.

**Deliverables:**
- CSV structure verification.
- Integration result review.
- Dashboard integration support.

## Day 5 — Dashboard Layout and Traffic Statistics

**Objective:**

Improve the dashboard presentation of normal and high-rate traffic.

**Work Performed:**

1. Reviewed the existing dashboard layout.
2. Improved the presentation of CAN traffic information.
3. Worked on displaying message count.
4. Reviewed messages-per-second information.
5. Checked normal traffic presentation.
6. Checked simulated high-rate traffic presentation.
7. Reviewed the detection status display.
8. Worked on improving dashboard readability.

**Outcome:**

The dashboard layout was reviewed and improved to support traffic monitoring and comparison.

**Deliverables:**
- Updated dashboard layout.
- Traffic statistics display support.
- Dashboard progress screenshots.

## Day 6 — Intermediate Development Period

**Objective:**

Continue the dashboard development and integration activities.

**Progress Record:**

A separate detailed Day 6 task record is not available in the current project history.

No additional implementation or testing results are claimed for this day.

**Documentation Status:** Individual activities require verification from the corresponding project records.

## Day 7 — Intermediate Development Period

**Objective:**

Continue the project development activities.

**Progress Record:**

A separate detailed Day 7 dashboard activity record is not available in the current project history.

No unverified dashboard features or testing results are included in this report.

**Documentation Status:** Individual activities require verification from the corresponding project records.

## Day 8 — Dashboard Development Progress

**Objective:**

Continue preparing the dashboard for detector integration and result visualization.

**Progress Record:**

A separate detailed Day 8 activity record is not available in the current project history.

The subsequent development activities included detector investigation, evaluation support, and dashboard integration.

**Documentation Status:** Individual activities require verification from the corresponding project records.

## Day 9 — Isolation Forest Model Investigation

**Objective:**

Investigate differences between normal and high-rate CAN traffic features for detector analysis.

**Work Performed:**

1. Reviewed the Isolation Forest model-related work.
2. Investigated available normal traffic features.
3. Reviewed high-rate traffic features.
4. Compared the available traffic characteristics.
5. Examined the relevance of traffic features for anomaly detection.
6. Reviewed the information required for displaying detector results in the dashboard.

**Outcome:**

Normal and high-rate traffic feature differences were investigated to support detector integration and evaluation.

**Deliverables:**
- Model investigation findings.
- Traffic feature comparison support.

## Day 10 — Hybrid Detector Review

**Objective:**

Review the hybrid detection approach and compare available detector outputs.

**Work Performed:**

1. Reviewed machine-learning detector output.
2. Reviewed rate-based or rule-based detector output.
3. Compared available ML and rule-based predictions.
4. Examined hybrid detector results.
5. Reviewed dashboard requirements for displaying multiple detector outputs.
6. Updated dashboard specification information.

**Outcome:**

Detector comparison requirements were reviewed, and dashboard specifications were updated to support ML, Rate-based, and Hybrid detector reporting.

**Deliverables:**
- Hybrid detector review.
- Detector comparison support.
- Updated dashboard specification.

## Day 11 — Detector Evaluation Metrics Support

**Objective:**

Support detector evaluation and prepare the required performance metrics for dashboard reporting.

**Work Performed:**

1. Reviewed detector evaluation requirements.
2. Worked with confusion matrix values.
3. Reviewed True Positive (TP).
4. Reviewed False Positive (FP).
5. Reviewed True Negative (TN).
6. Reviewed False Negative (FN).
7. Worked with precision, recall, F1-score, and accuracy.
8. Reviewed evaluation output requirements.

**Outcome:**

The dashboard evaluation requirements were prepared to display and compare detector performance using standard evaluation metrics.

**Deliverables:**
- Detector evaluation support.
- Confusion matrix reporting requirements.
- Evaluation metric display requirements.

## Day 12 — HTML Dashboard Development and Integration

**Objective:**

Update the existing HTML dashboard to display detector results and evaluation metrics.

**Work Performed:**

The existing HTML dashboard generation script was updated to generate a consolidated report using available CSV result files.

**Main Implementation File:**

`src/generate_dashboard_report.py`

**Generated Dashboard:**

`reports/detector_dashboard.html`

**Dashboard Features:**

1. ML Detector summary.
2. Rate-based Detector summary.
3. Hybrid Detector summary.
4. Normal traffic results.
5. High-rate traffic results.
6. Detector evaluation metrics.
7. Edge-case validation results.

**Evaluation Metrics Displayed:**

- TP — True Positive.
- FP — False Positive.
- TN — True Negative.
- FN — False Negative.
- Precision.
- Recall.
- F1-score.
- Accuracy.

**Data Sources:**

- `results/integration_results.csv`
- `results/detector_evaluation_metrics.csv`
- `results/edge_case_validation.csv`

**Testing:**

Test file: `tests/test_dashboard.py`

Command:

`python -m unittest discover -s tests -p "test_dashboard.py" -v`

**Result:** 4 tests passed.

The tests covered:
- Detector summary display.
- Empty input handling.
- Metrics CSV column verification.
- Missing input file handling.

**Outcome:**

The HTML dashboard was generated successfully and displayed the available detector summaries, evaluation metrics, and edge-case results.

**Deliverables:**
- Updated dashboard generator.
- Generated HTML dashboard.
- Dashboard test file.
- Dashboard verification.

## Day 13 — Dashboard Metadata and Validation

**Objective:**

Improve the existing HTML dashboard by adding dataset and execution metadata.

**Work Performed:**

The existing dashboard was updated to display additional information about the input data and report generation.

**Metadata Added:**

1. Input dataset name.
2. Model filename.
3. Rate-based threshold.
4. Run timestamp.
5. Sample count.
6. Synthetic-data limitation notice.

**Displayed Metadata:**

| Metadata | Displayed Value |
|---|---|
| Input dataset | `results/integration_results.csv` |
| Model filename | Not available |
| Rate-based threshold | Not available |
| Run timestamp | Automatically generated |
| Sample count | 60 |

Unavailable model and threshold information was displayed as `Not available` rather than using unverified values.

**Missing and Empty Input Handling:**

Additional tests were created to verify:

- Metadata display.
- Missing metadata handling.
- Empty input handling.
- Missing input CSV file handling.

**Test File:**

`tests/test_dashboard_metadata.py`

**Command:**

`python -m unittest discover -s tests -p "test_dashboard_metadata.py" -v`

**Result:** 4 tests passed.

The existing Day 12 dashboard tests were also executed again.

**Dashboard Generation:**

`python src/generate_dashboard_report.py --force`

**Generation Results:**

- Integration records: 60.
- Metrics records: 3.
- Edge-case scenarios: 3.
- Dashboard generation: Successful.

**Visual Verification:**

The generated HTML dashboard was opened in a browser and checked for:

- Dataset information.
- Model filename and threshold fields.
- Run timestamp and sample count.
- Detector summaries.
- Evaluation metrics.
- Edge-case validation results.
- Synthetic-data limitation notice.

**Outcome:**

The existing HTML dashboard was successfully updated with metadata display and input validation support.

**Deliverables:**
- Updated `src/generate_dashboard_report.py`.
- Updated `reports/detector_dashboard.html`.
- `tests/test_dashboard_metadata.py`.
- Updated README information.

## Day 14 — Dashboard Status and Documentation

**Objective:**

Prepare dashboard status documentation and organize the development progress.

**Work Performed:**

1. Inspected the existing PyQt5 and HTML dashboards.
2. Reviewed ML Detector results.
3. Reviewed Rate-based Detector results.
4. Reviewed Hybrid Detector results.
5. Documented confusion matrix values.
6. Explained TP, FP, TN, and FN.
7. Documented precision, recall, F1-score, and accuracy.
8. Organized dashboard output and screenshot references.
9. Updated README with installation and dashboard execution instructions.
10. Prepared the dashboard status report.
11. Organized the day-wise dashboard development activities.

**README Updates:**

The README was updated with:

- Project overview.
- Dashboard features.
- Detector summaries.
- Evaluation metrics.
- Technologies used.
- Project structure.
- Installation instructions.
- PyQt5 dashboard execution.
- HTML report generation instructions.
- CSV input information.
- Limitations and future work.

**Dashboard Status Documentation:**

`docs/dashboard_status.md`

The document includes:

- Day-wise dashboard development progress.
- Detector evaluation results.
- Confusion matrix explanation.
- Edge-case validation details.
- Dashboard input and output references.
- Testing summary.
- Current limitations.
- Future work.

**Outcome:**

The dashboard development activities and available verification results were organized into a single day-wise project report.

**Deliverables:**
- Updated `README.md`.
- `docs/dashboard_status.md`.
- Day-wise dashboard progress documentation.

---

# 3. Detector Evaluation Results

The available detector evaluation dataset contains 60 evaluated windows for each detector.

| Metric | ML | Rate-based | Hybrid |
|---|---:|---:|---:|
| TP | 0 | 52 | 52 |
| FP | 2 | 0 | 2 |
| TN | 6 | 8 | 6 |
| FN | 52 | 0 | 0 |
| Precision | 0.0000 | 1.0000 | 0.9631 |
| Recall | 0.0000 | 1.0000 | 1.0000 |
| F1-score | 0.0000 | 1.0000 | 0.9811 |
| Accuracy | 0.1000 | 1.0000 | 0.9667 |

These values represent the available evaluation dataset. They should not be interpreted as verified real-world vehicle performance.

## 3.1 ML Detector

- TP: 0
- FP: 2
- TN: 6
- FN: 52
- Precision: 0.0000
- Recall: 0.0000
- F1-score: 0.0000
- Accuracy: 0.1000

## 3.2 Rate-based Detector

- TP: 52
- FP: 0
- TN: 8
- FN: 0
- Precision: 1.0000
- Recall: 1.0000
- F1-score: 1.0000
- Accuracy: 1.0000

## 3.3 Hybrid Detector

- TP: 52
- FP: 2
- TN: 6
- FN: 0
- Precision: 0.9631
- Recall: 1.0000
- F1-score: 0.9811
- Accuracy: 0.9667

---

# 4. Confusion Matrix and Evaluation Metrics

A confusion matrix is used to evaluate how correctly a detector classifies normal and attack traffic.

| Term | Explanation |
|---|---|
| TP — True Positive | Attack traffic correctly identified as an attack |
| FP — False Positive | Normal traffic incorrectly identified as an attack |
| TN — True Negative | Normal traffic correctly identified as normal |
| FN — False Negative | Attack traffic incorrectly identified as normal |

### 4.1 Precision

Measures how many predicted attack cases were actually attacks.

`Precision = TP / (TP + FP)`

### 4.2 Recall

Measures how many actual attack cases were correctly identified.

`Recall = TP / (TP + FN)`

### 4.3 F1-score

Harmonic mean of precision and recall.

`F1-score = 2 × Precision × Recall / (Precision + Recall)`

### 4.4 Accuracy

Measures the overall percentage of correct predictions.

`Accuracy = (TP + TN) / (TP + TN + FP + FN)`

---

# 5. Edge-Case Validation

The available dashboard displays three edge-case scenarios:

1. Burst Traffic.
2. Replay Pattern.
3. Normal-to-High-Rate Transition.

The validation data is available in:

`results/edge_case_validation.csv`

**Important limitation:** The available edge-case validation results indicate that the production detector was marked `NOT RUN`. Therefore, baseline validation results must not be presented as successful production detector execution.

---

# 6. Dashboard Files and Output References

| File | Description |
|---|---|
| `dashboard.py` | PyQt5 dashboard |
| `src/generate_dashboard_report.py` | HTML dashboard generation script |
| `reports/detector_dashboard.html` | Generated HTML dashboard |
| `tests/test_dashboard.py` | Existing dashboard tests |
| `tests/test_dashboard_metadata.py` | Metadata and input handling tests |
| `README.md` | Project documentation |
| `docs/dashboard_status.md` | Day-wise dashboard status report |

## 6.1 Input Data Files

| File | Purpose |
|---|---|
| `results/integration_results.csv` | Integration results |
| `results/detector_evaluation_metrics.csv` | Detector evaluation metrics |
| `results/edge_case_validation.csv` | Edge-case validation results |

## 6.2 Screenshot References

Existing screenshot references:

- `screenshots/dashboard_day1.png.png`
- `screenshots/dashboard_progress.png`
- `screenshots/day5_dashboard_progress.png`

Generated HTML report:

`reports/detector_dashboard.html`

---

# 7. Testing Summary

| Test File | Tests Passed |
|---|---:|
| `tests/test_dashboard.py` | 4 |
| `tests/test_dashboard_metadata.py` | 4 |
| **Total** | **8** |

Dashboard generation was also completed successfully.

**Generation command:**

`python src/generate_dashboard_report.py --force`

**Generation output:**

- Integration records: 60.
- Metrics records: 3.
- Edge-case scenarios: 3.

---

# 8. Current Implementation Status

| Feature | Status |
|---|---|
| Initial PyQt5 dashboard | Implemented |
| CAN traffic visualization | Available |
| CSV data loading | Available |
| Normal and high-rate traffic comparison | Available |
| Message count display | Available |
| Messages-per-second information | Available in the dashboard data flow; source interval must be verified |
| ML detector summary | Available in evaluation report |
| Rate-based detector summary | Available in evaluation report |
| Hybrid detector summary | Available in evaluation report |
| Confusion matrix metrics | Implemented |
| HTML report dashboard | Implemented |
| Dataset metadata display | Implemented |
| Run timestamp | Implemented |
| Sample count | Implemented |
| Synthetic-data limitation notice | Implemented |
| Missing input file handling test | Passed |
| Metadata tests | 4 passed |
| Existing dashboard tests | 4 passed |
| Production edge-case detector execution | Not confirmed |
| Actual vehicle CAN validation | Pending |

---

# 9. Current Limitations

- Model filename is not available from the verified configuration.
- Rate-based threshold is not available.
- Production detector execution for edge cases is not confirmed.
- Results depend on the available CSV files.
- Synthetic-data results do not establish real-world vehicle performance.
- A high message rate alone does not prove that an attack has been detected.
- Full end-to-end validation using actual CAN traffic remains necessary.

---

# 10. Future Work

1. Verify the model filename and configuration.
2. Verify the rate-based threshold.
3. Validate messages-per-second calculations against the actual measurement interval.
4. Perform production detector testing.
5. Validate the complete detection pipeline.
6. Test using actual CAN traffic datasets.
7. Continue improving dashboard visualization and documentation.

---

# 11. Conclusion

From Day 1 to Day 14, the CAN-Sentinel dashboard development progressed from the initial PyQt5 interface and CAN traffic visualization to CSV integration, detector evaluation reporting, HTML dashboard generation, metadata display, testing, and documentation.

The dashboard currently provides a way to review available CAN traffic records, normal and simulated high-rate traffic, ML, Rate-based, and Hybrid detector summaries, evaluation metrics, and edge-case validation information.

The development work establishes the dashboard reporting functionality required by the project. Further production testing and validation using actual CAN traffic are necessary before treating the available evaluation results as final vehicle intrusion detection performance.