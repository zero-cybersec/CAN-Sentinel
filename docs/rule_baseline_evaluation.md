# Rule-Based CAN Traffic Baseline Evaluation

## Objective
Evaluate a simple message-interval rule against the available synthetic normal and high-rate CAN traffic datasets. This baseline is separate from the Isolation Forest ML model.

## Method
- Input datasets: `results/normal_traffic.csv` and `results/high_rate_traffic.csv`
- Windowing: up to 100 messages per CAN ID per window; windows with fewer than 10 messages are skipped.
- Feature: average time interval between consecutive messages, in milliseconds.
- Experimental rule: flag a window as `HIGH_RATE_SUSPECTED` when its average interval is below 30 ms; otherwise label it `NORMAL_BY_BASELINE`.

## Observed Results
| Dataset | Windows flagged | Windows not flagged | Total windows |
|---|---:|---:|---:|
| Normal traffic | 0 | 8 | 8 |
| High-rate traffic | 52 | 0 | 52 |
| Total | 52 | 8 | 60 |

The observed average per-CAN-ID intervals were approximately 68–91 ms for normal traffic and 7.9–8.1 ms for high-rate traffic.

## Interpretation
On these available synthetic datasets, the 30 ms rule separated all evaluated high-rate windows from all evaluated normal windows. This is a baseline result, not proof of general detection accuracy.

## Limitations
- The threshold is experimental and was evaluated on these datasets only.
- Real vehicle CAN traffic has not been validated with this rule.
- The result does not mean the Isolation Forest model has been fixed; ML detection must be evaluated separately.
- More varied traffic, additional normal scenarios, and false-positive/false-negative testing are needed before making broader claims.
