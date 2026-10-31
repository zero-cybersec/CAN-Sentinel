"""Generate the CAN-Sentinel HTML dashboard from existing CSV results."""

import csv
import html
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "results" / "integration_results.csv"
METRICS_FILE = PROJECT_ROOT / "results" / "detector_evaluation_metrics.csv"
EDGE_CASE_FILE = PROJECT_ROOT / "results" / "edge_case_validation.csv"

OUTPUT_FILE = PROJECT_ROOT / "reports" / "detector_dashboard.html"

REQUIRED_COLUMNS = {
    "source_file",
    "can_id",
    "message_count",
    "ml_prediction",
    "rate_based_prediction",
    "prediction",
}


def escape(value):
    """Safely convert values into HTML text."""
    return html.escape(str(value))


def read_csv(file_path):
    """Read a CSV file and return its headers and rows."""
    if not file_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {file_path}")

    with file_path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {file_path.name}")

        rows = list(reader)

    return reader.fieldnames, rows


def prediction_summary(rows, column, detector_name):
    """Generate prediction counts for one detector."""
    counts = Counter(
        str(row.get(column, "")).strip() or "Unknown"
        for row in rows
    )

    table_rows = ""

    for label, count in sorted(counts.items()):
        table_rows += (
            f"<tr><td>{escape(label)}</td>"
            f"<td>{count}</td></tr>"
        )

    return f"""
    <section class="card">
        <h2>{escape(detector_name)}</h2>
        <p>Total records: <strong>{len(rows)}</strong></p>
        <table>
            <tr><th>Prediction</th><th>Count</th></tr>
            {table_rows}
        </table>
    </section>
    """


def metrics_table(rows):
    """Display available detector evaluation metrics."""
    if not rows:
        return "<p>Evaluation metrics unavailable.</p>"

    columns = [
        "detector",
        "evaluated_windows",
        "TP",
        "FP",
        "TN",
        "FN",
        "precision",
        "recall",
        "f1_score",
        "accuracy",
    ]

    available = [col for col in columns if col in rows[0]]

    if not available:
        return "<p>Required metric columns unavailable.</p>"

    header = "".join(f"<th>{escape(col)}</th>" for col in available)

    body = ""

    for row in rows:
        cells = "".join(
            f"<td>{escape(row.get(col, 'Unavailable'))}</td>"
            for col in available
        )
        body += f"<tr>{cells}</tr>"

    return f"""
    <table>
        <tr>{header}</tr>
        {body}
    </table>
    """


def edge_case_table(rows):
    """Display available edge-case validation results."""
    if not rows:
        return "<p>Edge-case results unavailable.</p>"

    columns = [
        "scenario",
        "input_count",
        "detector_output_count",
        "baseline_output_count",
        "expected_behavior",
        "observed_result",
        "status",
    ]

    available = [col for col in columns if col in rows[0]]

    if not available:
        return "<p>Edge-case columns unavailable.</p>"

    header = "".join(f"<th>{escape(col)}</th>" for col in available)

    body = ""

    for row in rows:
        cells = "".join(
            f"<td>{escape(row.get(col, 'Unavailable'))}</td>"
            for col in available
        )
        body += f"<tr>{cells}</tr>"

    return f"""
    <table>
        <tr>{header}</tr>
        {body}
    </table>
    """


def traffic_summary(rows):
    """Separate normal and high-rate traffic using source filenames."""
    groups = {
        "Normal Traffic": [],
        "High-Rate Traffic": [],
        "Other Traffic": [],
    }

    for row in rows:
        source = str(row.get("source_file", "")).lower()

        if "high_rate" in source or "high-rate" in source:
            groups["High-Rate Traffic"].append(row)
        elif "normal" in source:
            groups["Normal Traffic"].append(row)
        else:
            groups["Other Traffic"].append(row)

    result = ""

    for name, group in groups.items():
        if group:
            result += f"""
            <section class="card">
                <h2>{escape(name)}</h2>
                <p>Records: {len(group)}</p>
                {prediction_summary(group, "ml_prediction", "ML Detector")}
                {prediction_summary(group, "rate_based_prediction", "Rate-Based Detector")}
                {prediction_summary(group, "prediction", "Hybrid Detector")}
            </section>
            """

    return result


def build_html(rows, metrics_rows=None, edge_rows=None, metadata=None):
    """Build the complete dashboard page."""
    metrics_rows = metrics_rows or []
    edge_rows = edge_rows or []
    metadata = metadata or {}

    input_dataset = metadata.get("input_dataset", "Not available")
    model_file = metadata.get("model_file", "Not available")
    rate_threshold = metadata.get("rate_threshold", "Not available")
    sample_count = metadata.get("sample_count", len(rows))
    run_timestamp = metadata.get("run_timestamp", "Not available")

    generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CAN-Sentinel Dashboard</title>

<style>
body {{
    margin: 0;
    padding: 24px;
    font-family: Arial, sans-serif;
    background: #f1f5f9;
    color: #172033;
}}
header {{
    background: #132238;
    color: white;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 24px;
}}
.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 18px;
}}
.card {{
    background: white;
    padding: 18px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    margin-bottom: 18px;
    overflow-x: auto;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 12px;
}}
th, td {{
    text-align: left;
    padding: 10px;
    border-bottom: 1px solid #e2e8f0;
}}
th {{
    background: #e8eef6;
}}
.notice {{
    background: #fff4d6;
    padding: 14px;
    border-radius: 8px;
}}
footer {{
    margin-top: 24px;
    color: #64748b;
    font-size: 13px;
}}
</style>
</head>

<body>

<header>
    <h1>CAN-Sentinel Detector Dashboard</h1>
    <p>Vehicle CAN Network Intrusion Detection System</p>
    <p>Input dataset: {escape(str(input_dataset))}</p>
<p>Model file: {escape(str(model_file))}</p>
<p>Rate-based threshold: {escape(str(rate_threshold))}</p>
<p>Run timestamp: {escape(str(run_timestamp))}</p>
<p>Sample count: <strong>{escape(str(sample_count))}</strong></p>
</header>

<div class="notice">
    <strong>Limitation:</strong>
    Results are based on the available CSV files.
    Synthetic or previously generated data should not be treated
    as proof of real-world production performance.
</div>

<h2>Overall Detector Summaries</h2>

<div class="grid">
    {prediction_summary(rows, "ml_prediction", "ML Detector")}
    {prediction_summary(rows, "rate_based_prediction", "Rate-Based Detector")}
    {prediction_summary(rows, "prediction", "Hybrid Detector")}
</div>

<h2>Normal and High-Rate Traffic Results</h2>

{traffic_summary(rows)}

<h2>Detector Evaluation Metrics</h2>

<div class="card">
    {metrics_table(metrics_rows)}
</div>

<h2>Edge-Case Validation Results</h2>

<div class="card">
    {edge_case_table(edge_rows)}
</div>

<footer>
    Generated by src/generate_dashboard_report.py
</footer>

</body>
</html>
"""


def main():
    """Validate CSV inputs and generate the HTML dashboard."""
    try:
        headers, rows = read_csv(INPUT_FILE)

        missing = REQUIRED_COLUMNS - set(headers)

        if missing:
            print(
                "ERROR: Missing required columns: "
                + ", ".join(sorted(missing))
            )
            return 1

        if not rows:
            print("ERROR: Integration CSV contains no data rows.")
            return 1

        metrics_rows = []
        edge_rows = []

        if METRICS_FILE.exists():
            _, metrics_rows = read_csv(METRICS_FILE)

        if EDGE_CASE_FILE.exists():
            _, edge_rows = read_csv(EDGE_CASE_FILE)

        if OUTPUT_FILE.exists() and "--force" not in sys.argv:
            print(f"ERROR: Report already exists: {OUTPUT_FILE}")
            print("Use --force to intentionally update the report.")
            return 1

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        metadata = {
    "input_dataset": str(INPUT_FILE.relative_to(PROJECT_ROOT)),
    "model_file": "Not available",
    "rate_threshold": "Not available",
    "run_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "sample_count": len(rows)
}

        page = build_html(rows, metrics_rows, edge_rows, metadata)
        OUTPUT_FILE.write_text(page, encoding="utf-8")

        print(f"Dashboard updated successfully: {OUTPUT_FILE}")
        print(f"Integration records: {len(rows)}")
        print(f"Metrics records: {len(metrics_rows)}")
        print(f"Edge-case scenarios: {len(edge_rows)}")

        return 0

    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())