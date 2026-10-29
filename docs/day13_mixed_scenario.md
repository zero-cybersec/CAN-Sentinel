# Day 13: Combined Mixed-Traffic Scenario

## Scenario design

A single reproducible, time-ordered CAN traffic sequence is generated
using seed 13 and the existing normal traffic dataset.

The sequence contains four consecutive stages:

1. Normal traffic: 40 frames at 20 ms intervals.
2. Burst traffic: 40 frames at 2 ms intervals.
3. Replay traffic: 40 frames repeating 10 previously generated
   burst CAN ID/payload pairs.
4. Recovery traffic: 40 frames at 20 ms intervals.

## Expected behavior

- Normal traffic should carry the normal label.
- Burst traffic should carry the attack label.
- Replay traffic should carry the attack label.
- Recovery traffic should carry the normal label.
- Timestamps should increase strictly throughout the sequence.
- Replay messages should match previously generated CAN ID/payload pairs.

## Actual observations

- Total generated frames: 160
- Normal frames: 40
- Burst frames: 40
- Replay frames: 40
- Recovery frames: 40
- Timestamp ordering: PASS
- Replay payload validation: PASS
- Reproducibility seed: 13

## Limitations

These results validate the generated dataset and its structure.
They do not represent predictions or accuracy measurements from the
production ML intrusion detector.

## Input and output

- Input: results/normal_traffic.csv
- Output: results/day13_mixed_scenario_traffic.csv
