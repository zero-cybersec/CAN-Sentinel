# CAN-Sentinel Dataset Validation Report

## 1. Objective
Validate the normal and simulated high-rate CAN traffic datasets,
compare their message rates, and document the observed results.

## 2. Datasets
- Normal: `results/normal_traffic.csv`
- High-rate: `results/high_rate_traffic.csv`
- Summary: `results/summary.csv`
- Existing observations: `results/observations.txt`

## 3. Validation Results

| Check | Normal | Simulated High-Rate |
|---|---:|---:|
| Message count | 500 | 5000 |
| Duration | 10 seconds | 10 seconds |
| Message rate | 50 messages/sec | 500 messages/sec |
| First timestamp | 0.000 s | 0.000 s |
| Last timestamp | 9.980 s | 9.998 s |
| Average message interval | 0.020 s | 0.002 s |
| Timestamp ordering | Non-decreasing | Non-decreasing |
| Unique CAN IDs | 4 | 4 |
| Data bytes per message | 8 | 8 |

### CAN IDs observed in both datasets
- `0x100`
- `0x120`
- `0x200`
- `0x300`

## 4. Comparison and Observations
- The high-rate dataset contains 10 times as many messages as the normal dataset.
- Its recorded message rate is 10 times higher.
- The average interval between consecutive messages is 0.002 seconds
  for high-rate traffic and 0.020 seconds for normal traffic.
- Both datasets have non-decreasing timestamps and 8 data bytes per message.
- The summary records `0x300` as the most common normal CAN ID and
  `0x100` as the most common high-rate CAN ID. These frequency counts
  have not been independently verified in this report.
- Existing simulation observations are documented in `results/observations.txt`.

## 5. Scope and Limitations
These are synthetic CAN traffic simulation results, not measurements
from a real vehicle. The results demonstrate a difference in simulated
message rates; they do not establish that a real attack occurred.

## 6. Validation Status
Message counts, timestamp ordering, first and last timestamps,
average intervals, unique CAN IDs, and data-byte lengths were checked.
The reported most-common CAN ID frequency counts have not been
independently verified.
