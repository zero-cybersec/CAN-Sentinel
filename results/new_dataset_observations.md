# New Synthetic CAN Traffic Dataset Observations

## Generation method
Generated using `results/new_test_dataset.py`.
The script uses Python's csv, random, and pathlib modules.
Random seed: 2026.
Duration: 10 seconds per dataset.
CAN IDs used: 0x100, 0x120, 0x200, 0x300.

## Datasets and verification
- normal_traffic_new.csv: 250 messages at 25 messages/second.
- high_rate_traffic_new.csv: 2500 messages at 250 messages/second.
- Both datasets contain 4 unique CAN IDs.
- Timestamps are ordered.
- Normal first/last timestamps: 0.0 and 9.96 seconds.
- High-rate first/last timestamps: 0.0 and 9.996 seconds.
- Each message contains 8 data bytes.
- High-rate traffic is 10 times faster than normal traffic.

## Scope
These are synthetic simulation datasets, not real vehicle measurements.
The rate comparison alone does not prove a real-world attack.
Existing datasets were preserved; new filenames were used.
