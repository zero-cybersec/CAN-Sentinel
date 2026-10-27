import pytest

from src.evaluate_detectors import (
    actual_label,
    calculate_metrics,
    predicted_label,
)


def test_confusion_matrix_and_metrics():
    result = calculate_metrics(
        actual=[0, 0, 1, 1],
        predicted=[0, 1, 1, 0],
    )

    assert result["TP"] == 1
    assert result["FP"] == 1
    assert result["TN"] == 1
    assert result["FN"] == 1
    assert result["precision"] == 0.5
    assert result["recall"] == 0.5
    assert result["f1_score"] == 0.5
    assert result["accuracy"] == 0.5


def test_perfect_detection_metrics():
    result = calculate_metrics(
        actual=[0, 0, 1, 1],
        predicted=[0, 0, 1, 1],
    )

    assert result["TP"] == 2
    assert result["TN"] == 2
    assert result["FP"] == 0
    assert result["FN"] == 0
    assert result["f1_score"] == 1.0
    assert result["accuracy"] == 1.0


def test_zero_positive_predictions():
    result = calculate_metrics(
        actual=[0, 1],
        predicted=[0, 0],
    )

    assert result["precision"] == 0.0
    assert result["recall"] == 0.0
    assert result["f1_score"] == 0.0


def test_label_mapping():
    assert actual_label("normal_traffic.csv") == 0
    assert actual_label("high_rate_traffic.csv") == 1
    assert predicted_label("NORMAL") == 0
    assert predicted_label("NORMAL_BY_BASELINE") == 0
    assert predicted_label("ANOMALY") == 1
    assert predicted_label("HIGH_RATE_SUSPECTED") == 1


def test_unknown_label_is_rejected():
    with pytest.raises(ValueError):
        actual_label("unknown_traffic.csv")

    with pytest.raises(ValueError):
        predicted_label("UNKNOWN")
