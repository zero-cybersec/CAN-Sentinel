import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import rule_baseline


class RuleBaselineTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.results_dir = Path(self.temp_dir.name)

        patcher = patch.object(
            rule_baseline, "RESULTS_DIR", self.results_dir
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def write_dataset(self, filename, timestamps, fields=None):
        path = self.results_dir / filename
        fields = fields or ["timestamp_s", "mode", "can_id", "data"]

        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()

            for timestamp in timestamps:
                row = {
                    "timestamp_s": timestamp,
                    "mode": "test",
                    "can_id": "0x100",
                    "data": "00",
                }
                writer.writerow({key: row[key] for key in fields if key in row})

        return path

    def test_high_rate_traffic_is_flagged(self):
        self.write_dataset(
            "high.csv", [i * 0.005 for i in range(100)]
        )
        results = rule_baseline.analyse_file("high.csv", "TEST")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["prediction"], "HIGH_RATE_SUSPECTED")

    def test_normal_traffic_is_not_flagged(self):
        self.write_dataset(
            "normal.csv", [i * 0.05 for i in range(100)]
        )
        results = rule_baseline.analyse_file("normal.csv", "TEST")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["prediction"], "NORMAL_BY_BASELINE")

    def test_short_window_is_skipped(self):
        self.write_dataset("short.csv", [i * 0.01 for i in range(9)])
        results = rule_baseline.analyse_file("short.csv", "TEST")
        self.assertEqual(results, [])

    def test_missing_required_columns_raise_error(self):
        self.write_dataset(
            "invalid.csv", [0.0],
            fields=["timestamp_s", "mode", "data"],
        )
        with self.assertRaises(ValueError):
            rule_baseline.analyse_file("invalid.csv", "TEST")


if __name__ == "__main__":
    unittest.main()
