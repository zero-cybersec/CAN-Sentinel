# Day 17 — Integration Validation

## Objective
Validate the CAN-Sentinel integration pipeline using normal, high-rate, and mixed CAN traffic inputs.

## Validation Performed
- Reviewed the end-to-end integration test.
- Validated the normal traffic input.
- Validated the high-rate traffic input.
- Added mixed-traffic input coverage to the end-to-end test.
- Preserved the existing 0.5-second windowing behavior.
- Kept the existing model and threshold configuration unchanged.

## Test Results
- End-to-end tests: 2 passed.
- Full test suite: 23 passed.
- No test failures observed.

## Regression Test Notes
The synthetic mixed-traffic fixture contains 100 frames at 0.1-second intervals. With 0.5-second windows, it produces 20 output rows.

The fixture validates integration output structure and accepted prediction labels. It does not independently simulate the full Normal, Burst, Replay, and Recovery scenario sequence.

## Limitations
- Validation uses synthetic CAN traffic.
- Burst and Replay detection limitations remain as previously documented.
- Results should not be interpreted as validation against real vehicle CAN traffic.

## Conclusion
The integration test suite passes. Day 17 integration validation is complete for the current synthetic test coverage.
