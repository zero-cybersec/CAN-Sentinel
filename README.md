### Overview

The CAN-Sentinel dashboard has been enhanced to display CAN traffic
information from CSV files. The dashboard supports the visualization
of normal traffic and simulated high-rate traffic results.

This update extends the existing PyQt5 dashboard with CSV loading,
traffic statistics, and detection status indicators.

### Features Implemented

- Added a CSV file loading button.
- Displayed traffic information in a structured table.
- Added Traffic Type, CAN ID, Message Count, Messages/sec,
  and Detection Status columns.
- Added summary cards for total messages, unique CAN IDs,
  normal rows, and suspicious rows.
- Used color-coded indicators for normal and suspicious statuses.
- Added error handling for invalid or unreadable CSV files.
- Displayed the data source and last-updated timestamp.
- Retained sample data for dashboard demonstration and testing.

### Technologies Used

- Python
- PyQt5
- CSV module
- Git and GitHub

### Setup Instructions

1. Install Python 3 if it is not already installed.
2. Open a terminal in the project directory.
3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt