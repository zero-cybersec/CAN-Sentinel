import csv
import subprocess
import sys
from pathlib import Path


def test_missing_required_column_fails(tmp_path):
    project_dir = Path(__file__).resolve().parents[1]
    traffic_file = tmp_path / "can_traffic.csv"

    with traffic_file.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["timestamp", "data"])
        writer.writeheader()
        writer.writerow({"timestamp": "0.1", "data": "AABB"})

    result = subprocess.run(
        [sys.executable, str(project_dir / "src" / "extract_features.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
