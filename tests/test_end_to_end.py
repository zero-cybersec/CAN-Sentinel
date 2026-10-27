import csv

import pandas as pd
import pytest

from src import integration_test as integration


class FakeModel:
    def predict(self, features):
        return [1] * len(features)

    def decision_function(self, features):
        return [0.25] * len(features)


def write_traffic(path, interval_seconds):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=["timestamp_s", "can_id", "data"]
        )
        writer.writeheader()

        for i in range(100):
            writer.writerow({
                "timestamp_s": i * interval_seconds,
                "can_id": "123",
                "data": f"{i % 8:02X}",
            })


def test_end_to_end_pipeline(tmp_path, monkeypatch):
    results_dir = tmp_path / "results"
    results_dir.mkdir()

    write_traffic(results_dir / "normal_traffic.csv", 0.1)
    write_traffic(results_dir / "high_rate_traffic.csv", 0.001)

    model_file = tmp_path / "can_model.joblib"
    model_file.touch()
    output_file = results_dir / "integration_results.csv"

    monkeypatch.setattr(integration, "RESULTS_DIR", results_dir)
    monkeypatch.setattr(integration, "MODEL_FILE", model_file)
    monkeypatch.setattr(integration, "OUTPUT_FILE", output_file)
    monkeypatch.setattr(
        integration.joblib, "load", lambda _: FakeModel()
    )

    integration.main()

    result = pd.read_csv(output_file)

    assert len(result) == 2
    assert {
        "source_file", "can_id", "prediction",
        "ml_prediction", "rate_based_prediction", "anomaly_score"
    }.issubset(result.columns)

    normal = result[result["source_file"] == "normal_traffic.csv"]
    high_rate = result[result["source_file"] == "high_rate_traffic.csv"]

    assert len(normal) == 1
    assert len(high_rate) == 1
    assert normal.iloc[0]["prediction"] == "NORMAL"
    assert high_rate.iloc[0]["prediction"] == "HIGH_RATE_SUSPECTED"


def test_missing_traffic_input_reports_error(tmp_path, monkeypatch):
    results_dir = tmp_path / "results"
    results_dir.mkdir()

    model_file = tmp_path / "can_model.joblib"
    model_file.touch()

    monkeypatch.setattr(integration, "RESULTS_DIR", results_dir)
    monkeypatch.setattr(integration, "MODEL_FILE", model_file)

    with pytest.raises(FileNotFoundError, match="Waiting for"):
        integration.main()
