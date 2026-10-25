
"""Generate an HTML dashboard from CAN-Sentinel integration results."""

import csv
import html
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "results" / "integration_results.csv"
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
    """Escape values before inserting them into HTML."""
    return html.escape(str(value))


def prediction_summary(rows, column, detector_name):
    """Create a summary table showing prediction counts."""
    counts = Counter(
        str(row.get(column, "")).strip() or "Unknown"
        for row in rows
    )

    table_rows = "".join(
        f"<tr><td>{escape(label)}</td><td>{count}</td></tr>"
        for label, count in sorted(counts.items())
    )

    return f"""
    <section class="card">
      <h2>{escape(detector_name)}</h2>
      <p>Total records: <strong>{len(rows)}</strong></p>
      <table>
        <thead><tr><th>Prediction</th><th>Count</th></tr></thead>
        <tbody>{table_rows}</tbody>
      </table>
    </section>
    """


def traffic_summary(rows):
    """Group results into normal, high-rate, and other traffic."""
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

    sections = []

    for label, group_rows in groups.items():
        if not group_rows:
            continue

        sections.append(
            f"<section class='card'><h2>{escape(label)}</h2>"
            f"<p>Records: <strong>{len(group_rows)}</strong></p>"
            f"{prediction_summary(group_rows, 'ml_prediction', 'ML Predictions')}"
            f"{prediction_summary(group_rows, 'rate_based_prediction', 'Rate-Based Predictions')}"
            f"{prediction_summary(group_rows, 'prediction', 'Hybrid Predictions')}"
            "</section>"
        )

    return "\n".join(sections)


def build_html(rows):
    """Build the complete dashboard HTML."""
    total_records = len(rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CAN-Sentinel Detector Dashboard</title>
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
h1 {{ margin-top: 0; }}
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
th {{ background: #e8eef6; }}
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
    <p>ML, rate-based, and hybrid detector prediction summaries</p>
    <p>Total integration records: <strong>{total_records}</strong></p>
</header>

<h2>Overall Detector Summaries</h2>
<div class="grid">
{prediction_summary(rows, 'ml_prediction', 'ML Detector')}
{prediction_summary(rows, 'rate_based_prediction', 'Rate-Based Detector')}
{prediction_summary(rows, 'prediction', 'Hybrid Detector')}
</div>

<h2>Traffic Dataset Results</h2>
{traffic_summary(rows)}

<footer>
Generated from results/integration_results.csv by
src/generate_dashboard_report.py.
</footer>
</body>
</html>
"""


def main():
    """Validate the input and generate the dashboard report."""
    if not INPUT_FILE.exists():
        print(f"ERROR: Input CSV not found: {INPUT_FILE}")
        return 1

    try:
        with INPUT_FILE.open("r", newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)

            if not reader.fieldnames:
                print("ERROR: The input CSV is empty or has no header row.")
                return 1

            missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

            if missing_columns:
                print(
                    "ERROR: Missing required CSV columns: "
                    + ", ".join(sorted(missing_columns))
                )
                return 1

            rows = list(reader)

    except (OSError, UnicodeError, csv.Error) as error:
        print(f"ERROR: Could not read input CSV: {error}")
        return 1

    if not rows:
        print("ERROR: The input CSV contains a header but no data rows.")
        return 1

    # Avoid silently replacing an existing report.
    if OUTPUT_FILE.exists() and "--force" not in sys.argv:
        print(f"ERROR: Report already exists: {OUTPUT_FILE}")
        print("To replace it intentionally, run again with the --force option.")
        return 1

    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(build_html(rows), encoding="utf-8")
    except OSError as error:
        print(f"ERROR: Could not write dashboard report: {error}")
        return 1

    print(f"Dashboard generated successfully: {OUTPUT_FILE}")
    print(f"Records processed: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
