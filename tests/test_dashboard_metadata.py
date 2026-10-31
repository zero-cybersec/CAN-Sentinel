
import sys
import unittest
from pathlib import Path

# Add src folder to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from generate_dashboard_report import build_html, read_csv


class TestDashboardMetadata(unittest.TestCase):

    def setUp(self):
        self.rows = [
            {
                "source_file": "normal_traffic.csv",
                "can_id": "123",
                "message_count": "10",
                "ml_prediction": "NORMAL",
                "rate_based_prediction": "NORMAL",
                "prediction": "NORMAL"
            }
        ]

    def test_metadata_display(self):
        metadata = {
            "input_dataset": "results/integration_results.csv",
            "model_file": "can_model.joblib",
            "rate_threshold": "Not available",
            "sample_count": 1,
            "run_timestamp": "2026-10-31 10:00:00"
        }

        html = build_html(self.rows, metadata=metadata)

        self.assertIn("results/integration_results.csv", html)
        self.assertIn("can_model.joblib", html)
        self.assertIn("Not available", html)
        self.assertIn("2026-10-31 10:00:00", html)
        self.assertIn("1", html)

    def test_missing_metadata_display(self):
        metadata = {
            "input_dataset": "Not available",
            "model_file": "Not available",
            "rate_threshold": "Not available",
            "sample_count": "Not available",
            "run_timestamp": "Not available"
        }

        html = build_html(self.rows, metadata=metadata)

        self.assertIn("Not available", html)

    def test_empty_input_handling(self):
        metadata = {
            "input_dataset": "Not available",
            "model_file": "Not available",
            "rate_threshold": "Not available",
            "sample_count": 0,
            "run_timestamp": "Not available"
        }

        html = build_html([], metadata=metadata)

        self.assertIn("Not available", html)

    def test_missing_input_file_handling(self):
        missing_file = (
            PROJECT_ROOT / "results" / "missing_test_file.csv"
        )

        with self.assertRaises(FileNotFoundError):
            read_csv(missing_file)


if __name__ == "__main__":
    unittest.main()
