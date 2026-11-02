# Holdout Dataset Generation Report

## Objective
Generate an independent holdout dataset for CAN-Sentinel.

## Dataset
- File: results/holdout_traffic.csv
- Total frames: 6500
- Total simulated duration: 40 seconds
- Format: CSV

## Scenario Summary
| Scenario | Interval | Duration | Frames | Label |
|---|---|---|---|---|
| Normal | 20 ms | 10 s | 500 | normal |
| Burst | 2 ms | 10 s | 5000 | attack |
| Replay | 20 ms | 10 s | 500 | attack |
| Recovery | 20 ms | 10 s | 500 | normal |

## Validation
- All scenarios have independent timestamps starting at 0.
- Scenario labels are preserved.
- Replay traffic contains repeated frame sequences.
- The dataset was generated independently without reusing
  the existing training dataset.
- Frame counts and timestamp ranges were verified.

## Status
Holdout dataset generation and validation completed.
