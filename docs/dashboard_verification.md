# CAN-Sentinel Dashboard Verification — Day 12

## 1. Overview
The dashboard displays ML, Rate-Based, and Hybrid detector prediction summaries, along with normal and high-rate traffic results.

## 2. Data Sources
- `results/integration_results.csv` — detector prediction summaries and traffic dataset results.
- `results/detector_evaluation_metrics.csv` — detector evaluation metrics, including TP, FP, TN, FN, precision, recall, F1-score, and accuracy.
- `reports/detector_dashboard.html` — generated dashboard report.

## 3. Test Results
Test file: `tests/test_dashboard.py`

Command executed:
`python -m unittest discover -s tests -p "test_dashboard.py" -v`

Tests executed: 4  
Final result: OK

- Detector summaries display test: Passed.
- Empty input handling test: Passed.
- Metrics CSV columns verification: Passed.
- Missing input file handling test: Passed.

## 4. Error Handling
The tests verified that empty and missing input CSV files are handled without generating an invalid dashboard output. The script prints readable error messages for these conditions.

## 5. Known Limitations
- Dashboard values depend on the available CSV data.
- Evaluation metrics must be checked against the underlying evaluation output before interpreting them as final model performance.
- Tests cover the dashboard's current functions and do not constitute full end-to-end pipeline validation.