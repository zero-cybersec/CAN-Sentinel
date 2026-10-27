# CAN-Sentinel — Integration Findings

**Contributor:** Avinash
**Role:** Team Lead & Integration
**Phase:** Week 3 — Integration

## 1. Objective

Document the existing CAN-Sentinel detection pipeline, its component interfaces, and the integration findings observed so far.

## 2. Existing Pipeline

The current integration workflow connects these components:

1. CAN traffic input is read from `results/normal_traffic.csv` and `results/high_rate_traffic.csv`.
2. Feature extraction groups messages by CAN ID and processes message windows.
3. Windows with fewer than 10 messages are skipped.
4. The following features are calculated:
   - `message_count`
   - `avg_interval_ms`
   - `unique_payloads`
   - `payload_entropy`
5. The existing model, `can_model.joblib`, produces ML predictions and anomaly scores.
6. The rate-based detector labels windows with an average interval below 30 ms as `HIGH_RATE_SUSPECTED`.
7. The hybrid detector uses the rate-based label for high-rate windows and otherwise retains the ML prediction.
8. Results are written to `results/integration_results.csv`.

## 3. Component Interfaces

| Component | Input | Output |
|---|---|---|
| Traffic input | Synthetic CAN traffic CSV files | Timestamp, CAN ID and data fields |
| Feature extraction | Traffic messages | Per-window feature rows |
| ML detector | Feature columns | ML prediction and anomaly score |
| Rate-based detector | `avg_interval_ms` | Rate-based prediction |
| Hybrid detector | Rate-based result and ML prediction | Combined prediction |
| Integration output | All processed windows | `results/integration_results.csv` |

## 4. Existing Validation Evidence

Previously recorded results showed:

- The rule-baseline test suite passed 4 tests.
- The detector-evaluation test suite passed 5 tests.
- The combined result was 9/9 tests passed.
- The existing synthetic evaluation contained 52 high-rate windows and 8 normal windows.
- The recorded hybrid evaluation detected all 52 high-rate windows and produced 2 false positives among the 8 normal windows.

These are results from the existing synthetic datasets, not independent real-world validation.

## 5. Integration Risks and Limitations

- The workflow requires the expected traffic CSV files and `can_model.joblib` to be available.
- Feature extraction expects the required timestamp, CAN ID and data columns.
- The 30 ms rate threshold was selected using the same synthetic datasets and has not been independently validated.
- The ML model was trained on a very small dataset, so its performance may not generalize to other traffic.
- The integration output is written to a fixed results path; repeated runs can replace the previous output.
- End-to-end behavior with edge-case traffic still requires validation.

## 6. Next Integration Steps

1. Validate the complete pipeline with reproducible test inputs.
2. Confirm that feature rows and detector predictions remain aligned.
3. Test missing inputs and invalid traffic data.
4. Integrate edge-case traffic results when available.
5. Record actual test results, failures and fixes after execution.

## 7. Conclusion

The repository contains an existing pipeline connecting feature extraction, ML inference, rate-based detection, hybrid predictions and CSV output. The next integration stage is to validate the component boundaries and edge cases. The current synthetic results should not be treated as proof of production readiness.
