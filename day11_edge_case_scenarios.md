
# Day 11: Edge-Case Attack Traffic

## Purpose
This document describes additional CAN traffic scenarios for experimental validation of CAN-Sentinel.

## Scenarios

| Scenario | Description | Expected label |
|---|---|---|
| burst_traffic | Short burst of high-rate messages | attack |
| replay_pattern | Repeated CAN ID and identical payload | attack |
| normal_to_high_rate | Normal traffic followed by high-rate traffic | normal, then attack |

## Dataset Details
- Generator: `src/generate_day11_edge_cases.py`
- Output: `results/day11_edge_case_traffic.csv`
- Random seed: 11
- Expected data rows: 400

## CSV Schema
- `timestamp`: Simulated timestamp in seconds
- `can_id`: CAN identifier in hexadecimal
- `dlc`: Data length code
- `data`: Payload bytes in hexadecimal
- `scenario`: Scenario name
- `label`: Expected traffic label

## Validation
Verify CSV headers, row count, scenario names, labels, and reproducibility before using the dataset for model evaluation.

## Safety
Do not overwrite or delete existing datasets. Keep all work on the assigned branch. Experimental results must be measured before claiming model improvement.
