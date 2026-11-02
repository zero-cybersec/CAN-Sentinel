
"""Generate the CAN-Sentinel HTML dashboard from existing CSV results."""

import csv
import html
import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "results" / "integration_results.csv"
METRICS_FILE = PROJECT_ROOT / "results" / "detector_evaluation_metrics.csv"
EDGE_CASE_FILE = PROJECT_ROOT / "results" / "edge_case_validation.csv"

# Optional experimental ML predictions from Nikhil's branch.
EXPERIMENTAL_ML_FILE = (
    PROJECT_ROOT / "results" / "experimental_ml_predictions.csv"
)

OUTPUT_FILE = PROJECT_ROOT / "reports" / "detector_dashboard.html"

REQUIRED_COLUMNS = {
    "source_file",
    "can_id",
    "message_count",
    "ml_prediction",
    "rate_based_prediction",
    "prediction",
}

EXPERIMENTAL_REQUIRED_COLUMNS = {
    "source",
    "window",
    "can_id",
    "message_count",
    "label",
    "prediction",
    "anomaly_score",
    "reference_prediction",
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
def ml_model_comparison_table():
    """Display Nikhil's Day 15 ML model evaluation results."""

    models = [
        {
            "name": "Baseline (0.05)",
            "tp": 40, "fp": 2, "tn": 38, "fn": 0,
            "accuracy": "97.50%",
            "precision": "95.24%",
            "recall": "100.00%",
            "f1": "97.56%",
        },
        {
            "name": "Updated (0.01)",
            "tp": 0, "fp": 1, "tn": 39, "fn": 40,
            "accuracy": "48.75%",
            "precision": "0.00%",
            "recall": "0.00%",
            "f1": "0.00%",
        },
        {
            "name": "Over-sensitive (0.10)",
            "tp": 40, "fp": 4, "tn": 36, "fn": 0,
            "accuracy": "95.00%",
            "precision": "90.91%",
            "recall": "100.00%",
            "f1": "95.24%",
        },
    ]

    headers = [
        "Model Configuration", "TP", "FP", "TN", "FN",
        "Accuracy", "Precision", "Recall", "F1-score"
    ]

    header_html = "".join(
        f"<th>{escape(header)}</th>" for header in headers
    )

    body = ""

    for model in models:
        values = [
            model["name"], model["tp"], model["fp"],
            model["tn"], model["fn"], model["accuracy"],
            model["precision"], model["recall"], model["f1"]
        ]

        cells = "".join(
            f"<td>{escape(value)}</td>" for value in values
        )

        body += f"<tr>{cells}</tr>"

    return f"""
    <section class="card">
        <h2>ML Model Evaluation Comparison</h2>
        <p>Validation samples: 80 (40 Normal + 40 High-Rate Attack)</p>
        <table>
            <tr>{header_html}</tr>
            {body}
        </table>
        <p class="notice">
            Recommended configuration: Baseline (contamination = 0.05).
            It achieved 100% attack recall and 97.50% accuracy.
        </p>
        <p>
            The updated configuration (0.01) showed threshold collapse
            and missed all 40 attack windows.
        </p>
    </section>
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


def experimental_ml_summary(rows):
    """Display experimental ML predictions and anomaly scores."""
    if not rows:
        return """
        <div class="card">
            <p>Experimental ML prediction data is not available.</p>
            <p>Expected file: results/experimental_ml_predictions.csv</p>
        </div>
        """

    groups = defaultdict(list)

    for row in rows:
        groups[row.get("source", "Unknown")].append(row)

    total_mismatches = sum(
        row.get("prediction", "").strip().upper()
        != row.get("reference_prediction", "").strip().upper()
        for row in rows
    )

    result = f"""
    <div class="card">
        <h3>Experimental ML Overview</h3>
        <p>Total samples: <strong>{len(rows)}</strong></p>
        <p>Prediction/reference mismatches:
        <strong>{total_mismatches}</strong></p>
        <p class="notice">
            Reference predictions are comparison values.
            They are not assumed to be verified ground-truth labels.
        </p>
    </div>
    """

    for source, group in sorted(groups.items()):
        predictions = Counter(
            row.get("prediction", "Unknown").strip().upper()
            for row in group
        )

        references = Counter(
            row.get("reference_prediction", "Unknown").strip().upper()
            for row in group
        )

        mismatches = sum(
            row.get("prediction", "").strip().upper()
            != row.get("reference_prediction", "").strip().upper()
            for row in group
        )

        scores = []

        for row in group:
            try:
                scores.append(float(row.get("anomaly_score", "")))
            except (ValueError, TypeError):
                continue

        if scores:
            score_summary = (
                f"<p>Average anomaly score: {sum(scores) / len(scores):.6f}</p>"
                f"<p>Minimum anomaly score: {min(scores):.6f}</p>"
                f"<p>Maximum anomaly score: {max(scores):.6f}</p>"
            )
        else:
            score_summary = "<p>Anomaly scores unavailable.</p>"

        result += f"""
        <section class="card">
            <h3>{escape(source)}</h3>
            <p>Samples: <strong>{len(group)}</strong></p>
            <p>Prediction counts: {escape(dict(predictions))}</p>
            <p>Reference prediction counts: {escape(dict(references))}</p>
            <p>Prediction/reference mismatches: <strong>{mismatches}</strong></p>
            {score_summary}
        </section>
        """

    detail_rows = ""

    for row in rows:
        prediction = row.get("prediction", "").strip().upper()
        reference = row.get("reference_prediction", "").strip().upper()
        mismatch = prediction != reference

        detail_rows += f"""
        <tr>
            <td>{escape(row.get('source', ''))}</td>
            <td>{escape(row.get('window', ''))}</td>
            <td>{escape(row.get('can_id', ''))}</td>
            <td>{escape(row.get('message_count', ''))}</td>
            <td>{escape(row.get('label', ''))}</td>
            <td>{escape(prediction)}</td>
            <td>{escape(row.get('anomaly_score', ''))}</td>
            <td>{escape(reference)}</td>
            <td>{'Mismatch' if mismatch else 'Match'}</td>
        </tr>
        """

    result += f"""
    <div class="card">
        <h3>Experimental ML Sample Details</h3>
        <table>
            <tr>
                <th>Source</th>
                <th>Window</th>
                <th>CAN ID</th>
                <th>Message Count</th>
                <th>Label</th>
                <th>ML Prediction</th>
                <th>Anomaly Score</th>
                <th>Reference Prediction</th>
                <th>Comparison</th>
            </tr>
            {detail_rows}
        </table>
    </div>
    """

    return result


def build_html(
    rows,
    metrics_rows=None,
    edge_rows=None,
    metadata=None,
    experimental_rows=None,
):
    """Build the complete dashboard page."""
    metrics_rows = metrics_rows or []
    edge_rows = edge_rows or []
    metadata = metadata or {}
    experimental_rows = experimental_rows or []

    input_dataset = metadata.get("input_dataset", "Not available")
    model_file = metadata.get("model_file", "Not available")
    rate_threshold = metadata.get("rate_threshold", "Not available")
    sample_count = metadata.get("sample_count", len(rows))
    run_timestamp = metadata.get("run_timestamp", "Not available")

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
    <p>Input dataset: {escape(input_dataset)}</p>
    <p>Model file: {escape(model_file)}</p>
    <p>Rate-based threshold: {escape(rate_threshold)}</p>
    <p>Run timestamp: {escape(run_timestamp)}</p>
    <p>Sample count: <strong>{escape(sample_count)}</strong></p>
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

<h2>Experimental ML Prediction Results</h2>

{experimental_ml_summary(experimental_rows)}

<h2>Detector Evaluation Metrics</h2>

<div class="card">
    {metrics_table(metrics_rows)}
</div>

<h2>Edge-Case Validation Results</h2>

<div class="card">
    {edge_case_table(edge_rows)}
    
</div>
{ml_model_comparison_table()}
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
        experimental_rows = []

        if METRICS_FILE.exists():
            _, metrics_rows = read_csv(METRICS_FILE)

        if EDGE_CASE_FILE.exists():
            _, edge_rows = read_csv(EDGE_CASE_FILE)

        if EXPERIMENTAL_ML_FILE.exists():
            experimental_headers, experimental_rows = read_csv(
                EXPERIMENTAL_ML_FILE
            )

            missing_experimental = (
                EXPERIMENTAL_REQUIRED_COLUMNS - set(experimental_headers)
            )

            if missing_experimental:
                print(
                    "WARNING: Experimental ML CSV missing columns: "
                    + ", ".join(sorted(missing_experimental))
                )
                experimental_rows = []
        else:
            print(
                "WARNING: Experimental ML file not found. "
                "Its dashboard section will show unavailable."
            )

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
            "sample_count": len(rows),
        }

        page = build_html(
            rows,
            metrics_rows,
            edge_rows,
            metadata,
            experimental_rows,
        )

        OUTPUT_FILE.write_text(page, encoding="utf-8")

        print(f"Dashboard updated successfully: {OUTPUT_FILE}")
        print(f"Integration records: {len(rows)}")
        print(f"Metrics records: {len(metrics_rows)}")
        print(f"Edge-case scenarios: {len(edge_rows)}")
        print(f"Experimental ML records: {len(experimental_rows)}")

        return 0

    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
