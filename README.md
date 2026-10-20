# CAN-Sentinel
### Automotive ECU Intrusion Detection System

CAN-Sentinel is an automotive cybersecurity project focused on
visualizing Controller Area Network (CAN) traffic and supporting
the identification of potentially suspicious communication
patterns using traffic analysis and machine-learning techniques.

The project aims to compare normal CAN traffic with simulated
high-rate traffic and provide a dashboard for reviewing traffic
statistics and detection results.

> **Current Status:** The PyQt5 dashboard supports sample-data
> visualization and CSV loading. Integration with verified
> machine-learning predictions and actual traffic datasets is
> still subject to testing.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Objectives](#project-objectives)
3. [Dashboard Features](#dashboard-features)
4. [Dashboard Metrics](#dashboard-metrics)
5. [Technologies Used](#technologies-used)
6. [Project Structure](#project-structure)
7. [Installation](#installation)
8. [Running the Dashboard](#running-the-dashboard)
9. [Loading Traffic Data from CSV](#loading-traffic-data-from-csv)
10. [Sample CSV Format](#sample-csv-format)
11. [Week 1 Progress Report](#week-1-progress-report)
12. [Pending Integration Work](#pending-integration-work)
13. [Limitations](#limitations)
14. [Team Responsibilities](#team-responsibilities)

---

## Project Overview

Modern vehicles use the Controller Area Network (CAN) protocol
to enable communication between Electronic Control Units (ECUs).

Monitoring CAN traffic can help identify unusual communication
patterns, including unexpectedly high message rates.

CAN-Sentinel is being developed to support this process through:

- CAN traffic simulation and analysis.
- Feature extraction for machine-learning models.
- Model evaluation and prediction testing.
- A graphical dashboard for displaying traffic statistics.
- Comparison of normal and simulated high-rate traffic.
- Documentation of integration and testing requirements.

The dashboard provides a visual interface for reviewing
available traffic data and, after integration, verified
machine-learning detection results.

## Project Objectives

The main objectives are:

- Visualize CAN traffic statistics through a graphical interface.
- Compare normal and simulated high-rate traffic.
- Display message counts and traffic rates.
- Present detection statuses from verified model outputs.
- Support loading traffic and result data from CSV files.
- Integrate the dashboard with the project's existing
  feature-extraction and machine-learning pipeline.
- Document implementation progress, testing requirements,
  and remaining integration work.

---

## Dashboard Features

The dashboard is developed using Python and PyQt5.

### 1. Dashboard Interface

The interface uses a dark theme and contains:

- CAN-Sentinel project heading.
- Summary cards for traffic statistics.
- A CAN traffic overview table.
- A CSV-loading control.
- A sample-data refresh control.
- Data-source and last-updated information.

### 2. Traffic Comparison

The dashboard layout supports displaying both normal and
simulated high-rate traffic.

The traffic table includes:

| Field | Description |
|---|---|
| Traffic Type | Normal or simulated high-rate traffic |
| CAN ID | Identifier associated with the traffic record |
| Message Count | Number of messages represented by the record |
| Messages/sec | Observed or calculated message rate |
| Detection Status | Classification or status associated with the record |

### 3. Summary Cards

The dashboard is designed to summarize:

- Total messages.
- Unique CAN IDs.
- Normal traffic records.
- Suspicious or anomalous records.

The exact meaning of each metric depends on the loaded dataset
and its documented schema.

### 4. CSV Loading

The dashboard includes a CSV-loading interface for selecting
a local data file and displaying its contents.

The CSV format must match the columns expected by the dashboard.
Files with missing columns or invalid values should produce
a clear error message.

### 5. Demonstration Data

Sample data can be used to test the layout and demonstrate
how normal and high-rate traffic may appear.

**Important:** Demonstration values and sample detection
statuses are illustrative only. They must not be presented
as actual CAN observations, verified attack detections,
or machine-learning predictions.

---

## Dashboard Metrics

### Total Messages

The sum of message counts represented by the loaded records.

### Unique CAN IDs

The number of distinct CAN identifiers in the loaded dataset.

### Normal Messages

The total message count associated with records classified
as normal by the selected, documented classification source.

### Anomalies

The number of records or messages classified as anomalous.
The dashboard must specify whether this metric counts records
or individual messages.

### Messages per Second

The rate at which CAN messages are observed or generated.

When a reliable message count and simulation duration are
available, the rate can be calculated as:

`Messages per second = Message count / Duration in seconds`

The dashboard should use a rate supplied by the logger or
verified dataset when available.

A message count must not be treated as a messages-per-second
value without confirming the measurement interval.

### Detection Status

Possible statuses include:

- Normal
- Suspicious
- Anomaly
- Unknown

Actual statuses must come from the project's documented
classification logic or verified model output.

A high message rate alone does not prove that an attack
has been detected.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| PyQt5 | Graphical dashboard interface |
| CSV | Traffic-data and result exchange format |
| Machine Learning | Traffic classification and evaluation |
| Git | Version control |
| GitHub | Source-code collaboration and project hosting |

The precise model, feature-extraction methods, and CAN logging
implementation are maintained in their respective project
modules.

---

## Project Structure

The current dashboard-related files include:

```text
CAN-Sentinel/
├── dashboard.py
├── README.md
├── requirements.txt
├── sample_traffic.csv
├── CanSentinel_Cybersecurity_Overview
├── screenshots/
│   ├── dashboard_day1.png.png
│   └── dashboard_progress.png
└── docs/
    └── dashboard_spec.md