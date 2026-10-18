## Week 1 Progress Report

### Project Overview
CAN-Sentinel is an automotive cybersecurity project designed
to visualize CAN traffic and support the identification of
potentially suspicious communication patterns.

### Completed Work

#### Dashboard Development
- Developed a graphical dashboard using Python and PyQt5.
- Implemented a dark-themed user interface.
- Added summary cards for total messages, unique CAN IDs,
  normal records, and suspicious records.
- Created a traffic table to display CAN traffic information.

#### Traffic Visualization
- Added Traffic Type, CAN ID, Message Count,
  Messages/sec, and Detection Status columns.
- Prepared the dashboard to display normal and simulated
  high-rate traffic.
- Added color-coded detection status indicators.

#### CSV Loading
- Added functionality to select and load CSV files.
- Implemented validation for required CSV columns.
- Added error messages for invalid CSV files.
- Updated dashboard statistics using loaded records.

#### Dashboard Refresh
- Added a refresh button for demonstration data.
- Implemented summary updates and a last-updated timestamp.

### Current Status
The dashboard uses sample data for demonstration and supports
loading traffic records from CSV files.

Sample traffic values and detection statuses are illustrative.
They are not verified live CAN traffic or actual ML predictions.

### Pending Tasks
- Complete CSV loading tests using valid and invalid files.
- Capture a screenshot of the CSV-loaded dashboard.
- Integrate actual traffic comparison results when available.
- Display ML evaluation results when available.
- Verify dashboard output against actual project results.
- Commit and push the completed work to the development branch.

### Technologies Used
- Python
- PyQt5
- CSV
- Git and GitHub