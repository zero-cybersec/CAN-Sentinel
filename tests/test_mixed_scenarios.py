import csv
import pytest

from src.integration_test import extract_features
from src.evaluate_holdout import hybrid_prediction


@pytest.mark.parametrize(
    "scenario, interval_ms, expected",
    [
        ("burst", 2.0, "HIGH_RATE_SUSPECTED"),
        ("normal", 20.0, "NORMAL"),
        ("recovery", 20.0, "NORMAL"),
        ("replay", 10.0, "HIGH_RATE_SUSPECTED"),
    ],
)
def test_mixed_scenario_classification(
    tmp_path, scenario, interval_ms, expected
):
    traffic_file = tmp_path / f"{scenario}.csv"

    with traffic_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=["timestamp_s", "can_id", "data"]
        )
        writer.writeheader()

        for i in range(25):
            writer.writerow({
                "timestamp_s": i * interval_ms / 1000,
                "can_id": f"{i % 4:03X}",
                "data": f"{i:02X}",
            })

    rows = extract_features(traffic_file)

    assert len(rows) == 1
    assert rows[0]["avg_interval_ms"] == pytest.approx(interval_ms)

    prediction = (
        "HIGH_RATE_SUSPECTED"
        if rows[0]["avg_interval_ms"] <= 10.0
        else "NORMAL"
    )
    assert prediction == expected


@pytest.mark.parametrize(
    "rate, sequence, ml, expected",
    [
        ("HIGH_RATE_SUSPECTED", "NORMAL_BY_SEQUENCE", "NORMAL",
         "HIGH_RATE_SUSPECTED"),
        ("NORMAL_BY_BASELINE", "REPLAY_SUSPECTED", "NORMAL",
         "REPLAY_SUSPECTED"),
        ("NORMAL_BY_BASELINE", "NORMAL_BY_SEQUENCE", "NORMAL",
         "NORMAL"),
        ("NORMAL_BY_BASELINE", "NORMAL_BY_SEQUENCE", "ANOMALY",
         "ANOMALY"),
    ],
)
def test_hybrid_prediction_fusion(rate, sequence, ml, expected):
    assert hybrid_prediction(rate, sequence, ml) == expected
