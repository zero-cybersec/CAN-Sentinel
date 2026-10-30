# CAN-Sentinel - Final Detection Report

## Detector Performance

detector | evaluated_windows | TP | FP | TN | FN | precision | recall | f1_score | accuracy
--- | --- | --- | --- | --- | --- | --- | --- | --- | ---
ML | 52 | 48 | 0 | 4 | 0 | 1.0 | 1.0 | 1.0 | 1.0
Rate-based | 52 | 48 | 0 | 4 | 0 | 1.0 | 1.0 | 1.0 | 1.0
Hybrid | 52 | 48 | 0 | 4 | 0 | 1.0 | 1.0 | 1.0 | 1.0

## Integration Results

Total integration records: 52

### Prediction Distribution
- HIGH_RATE_SUSPECTED: 48
- NORMAL: 4

## Confusion Matrix Summary

- True Positives: 48
- False Positives: 0
- True Negatives: 4
- False Negatives: 0

## Conclusion

All three detectors achieved 100% accuracy on the evaluated synthetic traffic dataset. Real-world accuracy has not been established.