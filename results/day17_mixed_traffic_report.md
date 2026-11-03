# Day 17 Mixed-Traffic Validation Report

## Objective
Validate chronological integration of Normal, Burst, Replay, and Recovery traffic.

## Test Design
- Source: Existing independent holdout dataset
- Total frames: 6500
- Simulated duration: 40 seconds
- CSV schema: timestamp_s,can_id,data,scenario,label
- Scenario order: Normal -> Burst -> Replay -> Recovery

## Scenario Boundaries
| Scenario | Start | End | Expected Label |
|---|---:|---:|---|
| Normal | 0 s | 10 s | normal |
| Burst | 10 s | 20 s | attack |
| Replay | 20 s | 30 s | attack |
| Recovery | 30 s | 40 s | normal |

## Validation
- Timestamps are chronological.
- Each scenario has a clear boundary.
- Scenario labels are preserved.
- Existing 0.5-second windowing and model parameters remain unchanged.
- Existing holdout data was reused instead of unnecessarily duplicating it.

## Expected Behavior
Normal and Recovery segments are expected to be classified as normal.
Burst and Replay segments are expected to be detected as attacks.
Actual model predictions require separate ML evaluation.

## Status
Mixed-traffic dataset generated and chronological validation passed.
