import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import generate_dashboard_report as dashboard


class TestDashboard(unittest.TestCase):

    def test_metrics_csv_contains_required_metrics(self):
        metrics_file = PROJECT_ROOT / "results" / "detector_evaluation_metrics.csv"

        if not metrics_file.exists():
            self.skipTest("Metrics CSV is not available")

        with metrics_file.open("r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            self.assertIsNotNone(reader.fieldnames)

            required = {
                "detector", "TP", "FP", "TN", "FN",
                "precision", "recall", "f1_score", "accuracy"
            }
            self.assertTrue(required.issubset(set(reader.fieldnames)))

    def test_dashboard_contains_all_detector_summaries(self):
        rows = [
            {
                "source_file": "normal_traffic.csv",
                "can_id": "123",
                "message_count": "10",
                "ml_prediction": "Normal",
                "rate_based_prediction": "Normal",
                "prediction": "Normal",
            }
        ]

        output = dashboard.build_html(rows)

        self.assertIn("ML Detector", output)
        self.assertIn("Rate-Based Detector", output)
        self.assertIn("Hybrid Detector", output)
        self.assertIn("Normal Traffic", output)

    def test_empty_rows_do_not_create_dashboard_html(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / "integration_results.csv"
            output_file = Path(temp_dir) / "detector_dashboard.html"

            input_file.write_text(
                "source_file,can_id,message_count,ml_prediction,"
                "rate_based_prediction,prediction\n",
                encoding="utf-8",
            )

            with patch.object(dashboard, "INPUT_FILE", input_file), \
                 patch.object(dashboard, "OUTPUT_FILE", output_file):
                result = dashboard.main()

            self.assertEqual(result, 1)
            self.assertFalse(output_file.exists())

    def test_missing_input_file_is_handled(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / "missing.csv"
            output_file = Path(temp_dir) / "detector_dashboard.html"

            with patch.object(dashboard, "INPUT_FILE", input_file), \
                 patch.object(dashboard, "OUTPUT_FILE", output_file):
                result = dashboard.main()

            self.assertEqual(result, 1)
            self.assertFalse(output_file.exists())


if __name__ == "__main__":
    unittest.main()