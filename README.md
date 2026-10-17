## Development Progress

### Day 1: Dashboard Interface Development

The initial phase focused on developing the graphical user interface
for the CAN-Sentinel project using Python and PyQt5.

The dashboard was designed to display essential CAN traffic
information in a structured table format.

**Features Implemented:**
- Created the initial dashboard window.
- Added a table to display CAN IDs.
- Included message count information for each CAN ID.
- Added a status column to represent the current traffic status.
- Integrated sample CAN traffic data for demonstration.

### Day 2: Dashboard UI Enhancement

The dashboard interface was enhanced to improve its appearance
and usability.

**Improvements:**
- Refined the dashboard layout.
- Introduced a dark-themed user interface.
- Added summary cards to display traffic statistics.
- Improved the organization of CAN traffic information.
- Enhanced the overall readability of the dashboard.

### Day 3: Dynamic Dashboard Refresh

The third development phase focused on making the dashboard
more interactive by introducing a refresh mechanism.

**Features Implemented:**

1. **Dynamic Sample Data Updates**
   - Implemented functionality to update CAN message counts
     when the refresh button is clicked.
   - Used simulated data to demonstrate changing traffic values.

2. **Traffic Status Updates**
   - Added logic to update the displayed traffic status
     based on message counts.
   - Used different status labels to distinguish normal
     traffic from traffic requiring further attention.

3. **Refresh Dashboard Button**
   - Added a button to manually refresh dashboard information.
   - Introduced a brief refresh delay to simulate the update process.
   - Temporarily disabled the button while refreshing.

4. **Last Refreshed Timestamp**
   - Added a timestamp to indicate when the dashboard
     was last updated.
   - Updated the timestamp whenever the refresh operation completes.

5. **Dashboard Summary Updates**
   - Updated the summary information after refreshing the data.
   - Ensured that the displayed statistics reflect the
     currently loaded sample data.

### Current Implementation Status

The dashboard currently demonstrates CAN traffic monitoring
using simulated sample data.

The refresh functionality updates the sample message counts,
traffic statuses, and dashboard summary information.

**Note:** The current implementation uses simulated data.
It is not yet connected to a live CAN bus or a real vehicle network.
The displayed statuses are demonstration results and do not
represent a validated intrusion detection system.

### Planned Future Enhancements

- Implement suspicious CAN traffic identification.
- Introduce intrusion detection alerts.
- Develop configurable traffic thresholds.
- Integrate real-time CAN traffic data.
- Evaluate detection logic against representative CAN traffic datasets.
- Improve dashboard visualization and monitoring capabilities.

### Technologies Used

- Python
- PyQt5
- Git and GitHub

### Project Objective

CAN-Sentinel aims to provide a dashboard for visualizing
Controller Area Network (CAN) traffic and supporting the
identification of potentially suspicious communication patterns.

The project is being developed incrementally, starting with
the dashboard interface and progressing toward traffic analysis
and intrusion detection capabilities.