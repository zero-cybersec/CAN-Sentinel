import sys
import csv
import random
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QHeaderView,
    QAbstractItemView,
    QFileDialog,
    QMessageBox,
)

from PyQt5.QtCore import Qt, QTimer


class CANSentinelDashboard(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "CAN-Sentinel | ECU Security Dashboard"
        )
        self.resize(1200, 750)

        # Demonstration data only.
        # These are NOT actual CAN bus observations or ML predictions.
        self.sample_data = [
            {
                "traffic_type": "Normal",
                "can_id": "0x123",
                "message_count": 250,
                "messages_per_second": 25.0,
                "detection_status": "Normal",
            },
            {
                "traffic_type": "Normal",
                "can_id": "0x456",
                "message_count": 180,
                "messages_per_second": 18.0,
                "detection_status": "Normal",
            },
            {
                "traffic_type": "Simulated High-Rate",
                "can_id": "0x123",
                "message_count": 1200,
                "messages_per_second": 120.0,
                "detection_status": "Suspicious",
            },
            {
                "traffic_type": "Simulated High-Rate",
                "can_id": "0x456",
                "message_count": 950,
                "messages_per_second": 95.0,
                "detection_status": "Suspicious",
            },
        ]

        self.data_source = "Sample demonstration data"

        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a;
            }

            QWidget {
                font-family: Segoe UI;
                font-size: 12px;
            }

            QLabel {
                color: #e2e8f0;
            }

            QFrame#card {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 10px;
            }

            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                padding: 10px 18px;
                border-radius: 6px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }

            QPushButton:disabled {
                background-color: #475569;
                color: #cbd5e1;
            }

            QTableWidget {
                background-color: #1e293b;
                alternate-background-color: #263449;
                color: #e2e8f0;
                gridline-color: #334155;
                border: 1px solid #334155;
                border-radius: 8px;
                selection-background-color: #334155;
                selection-color: white;
            }

            QHeaderView::section {
                background-color: #334155;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)

        self.init_ui()
        self.update_dashboard(update_time=True)

    # --------------------------------------------------
    # USER INTERFACE
    # --------------------------------------------------

    def init_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Header
        heading_layout = QHBoxLayout()

        title = QLabel("CAN-SENTINEL")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #60a5fa;
        """)

        subtitle = QLabel(
            "Automotive ECU Intrusion Detection Dashboard"
        )
        subtitle.setStyleSheet(
            "font-size: 13px; color: #94a3b8;"
        )

        title_layout = QVBoxLayout()
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        heading_layout.addLayout(title_layout)
        heading_layout.addStretch()

        # Load CSV button
        self.load_button = QPushButton("Load CSV")
        self.load_button.clicked.connect(self.load_csv)

        heading_layout.addWidget(self.load_button)

        # Refresh button
        self.refresh_button = QPushButton(
            "Refresh Sample Data"
        )
        self.refresh_button.clicked.connect(
            self.refresh_sample_data
        )

        heading_layout.addWidget(self.refresh_button)

        main_layout.addLayout(heading_layout)

        # Summary cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.total_messages_value = self.create_card(
            cards_layout,
            "TOTAL MESSAGES",
            "0",
            "#60a5fa",
        )

        self.unique_ids_value = self.create_card(
            cards_layout,
            "UNIQUE CAN IDs",
            "0",
            "#34d399",
        )

        self.normal_rows_value = self.create_card(
            cards_layout,
            "NORMAL ROWS",
            "0",
            "#34d399",
        )

        self.suspicious_rows_value = self.create_card(
            cards_layout,
            "SUSPICIOUS ROWS",
            "0",
            "#fb7185",
        )

        main_layout.addLayout(cards_layout)

        # Table title
        table_title = QLabel("CAN Traffic Overview")
        table_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #f8fafc;
        """)

        main_layout.addWidget(table_title)

        # Traffic table
        self.table = QTableWidget(0, 5)

        self.table.setHorizontalHeaderLabels([
            "Traffic Type",
            "CAN ID",
            "Message Count",
            "Messages/sec",
            "ML Detection Status (Sample)",
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        main_layout.addWidget(self.table)

        # Data disclaimer
        self.disclaimer_label = QLabel(
            "DEMO MODE: Sample data only. "
            "Detection statuses are illustrative, "
            "not actual ML predictions."
        )

        self.disclaimer_label.setWordWrap(True)
        self.disclaimer_label.setAlignment(Qt.AlignCenter)
        self.disclaimer_label.setStyleSheet("""
            color: #fbbf24;
            font-size: 12px;
            font-weight: bold;
            padding: 8px;
        """)

        main_layout.addWidget(self.disclaimer_label)

        # Last updated label
        self.last_refresh_label = QLabel(
            "Source: Sample demonstration data"
        )

        self.last_refresh_label.setAlignment(Qt.AlignCenter)
        self.last_refresh_label.setStyleSheet(
            "color: #94a3b8; font-size: 11px;"
        )

        main_layout.addWidget(self.last_refresh_label)

        # Footer
        footer = QLabel(
            "CAN-Sentinel | Dashboard Module | Day 5"
        )

        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(
            "color: #64748b; font-size: 11px; padding: 5px;"
        )

        main_layout.addWidget(footer)

    # --------------------------------------------------
    # SUMMARY CARDS
    # --------------------------------------------------

    def create_card(
        self, layout, heading, value, accent_color
    ):

        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(100)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)

        heading_label = QLabel(heading)
        heading_label.setStyleSheet("""
            font-size: 11px;
            font-weight: bold;
            color: #94a3b8;
        """)

        value_label = QLabel(value)
        value_label.setStyleSheet(
            f"font-size: 28px; font-weight: bold; "
            f"color: {accent_color};"
        )

        card_layout.addWidget(heading_label)
        card_layout.addWidget(value_label)
        card_layout.addStretch()

        layout.addWidget(card)

        return value_label

    # --------------------------------------------------
    # UPDATE TABLE AND SUMMARY CARDS
    # --------------------------------------------------

    def update_dashboard(self, update_time=True):

        self.table.setRowCount(len(self.sample_data))

        for row, record in enumerate(self.sample_data):

            values = [
                record["traffic_type"],
                record["can_id"],
                str(record["message_count"]),
                str(record["messages_per_second"]),
                record["detection_status"],
            ]

            for column, value in enumerate(values):

                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)

                # Color the displayed detection status.
                if column == 4:

                    if value.strip().lower() == "normal":
                        item.setForeground(Qt.green)

                    elif value.strip().lower() in (
                        "suspicious",
                        "attack",
                        "anomaly",
                    ):
                        item.setForeground(Qt.red)

                    else:
                        item.setForeground(Qt.yellow)

                self.table.setItem(row, column, item)

            self.table.setRowHeight(row, 38)

        # Summary statistics from the currently displayed data.
        total_messages = sum(
            record["message_count"]
            for record in self.sample_data
        )

        unique_ids = len({
            record["can_id"]
            for record in self.sample_data
        })

        normal_rows = sum(
            1 for record in self.sample_data
            if record["traffic_type"].strip().lower() == "normal"
        )

        suspicious_rows = sum(
            1 for record in self.sample_data
            if record["detection_status"].strip().lower()
            in ("suspicious", "attack", "anomaly")
        )

        self.total_messages_value.setText(
            str(total_messages)
        )

        self.unique_ids_value.setText(
            str(unique_ids)
        )

        self.normal_rows_value.setText(
            str(normal_rows)
        )

        self.suspicious_rows_value.setText(
            str(suspicious_rows)
        )

        if update_time:

            current_time = datetime.now().strftime(
                "%d-%m-%Y %I:%M:%S %p"
            )

            self.last_refresh_label.setText(
                f"Source: {self.data_source} | "
                f"Last updated: {current_time}"
            )

    # --------------------------------------------------
    # LOAD TRAFFIC DATA FROM CSV
    # --------------------------------------------------

    def load_csv(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CAN Traffic CSV",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )

        if not file_path:
            return

        try:
            loaded_data = self.read_csv(file_path)

            if not loaded_data:
                raise ValueError(
                    "The CSV file contains no data rows."
                )

            # Replace dashboard data only after successful validation.
            self.sample_data = loaded_data
            self.data_source = file_path.split("/")[-1]

            self.update_dashboard(update_time=True)

            QMessageBox.information(
                self,
                "CSV Loaded",
                f"Successfully loaded {len(loaded_data)} rows.",
            )

        except (OSError, UnicodeError, csv.Error, ValueError, KeyError) as error:

            QMessageBox.critical(
                self,
                "CSV Loading Error",
                f"Could not load the CSV file.\n\n{error}\n\n"
                "Please check the file and its column headings.",
            )

    def read_csv(self, file_path):

        required_columns = {
            "traffic_type",
            "can_id",
            "message_count",
            "messages_per_second",
            "detection_status",
        }

        loaded_data = []

        with open(
            file_path,
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as csv_file:

            reader = csv.DictReader(csv_file)

            if not reader.fieldnames:
                raise ValueError(
                    "The CSV file must contain a header row."
                )

            # Allow extra whitespace around column headings.
            reader.fieldnames = [
                heading.strip().lower()
                for heading in reader.fieldnames
            ]

            missing_columns = (
                required_columns - set(reader.fieldnames)
            )

            if missing_columns:
                raise ValueError(
                    "Missing required columns: "
                    + ", ".join(sorted(missing_columns))
                )

            for line_number, row in enumerate(reader, start=2):

                try:
                    record = {
                        key.strip().lower(): (
                            value.strip() if value is not None else ""
                        )
                        for key, value in row.items()
                        if key is not None
                    }

                    traffic_type = record["traffic_type"]
                    can_id = record["can_id"]
                    detection_status = record["detection_status"]

                    if not traffic_type or not can_id:
                        raise ValueError(
                            "Traffic type and CAN ID cannot be empty."
                        )

                    if not detection_status:
                        raise ValueError(
                            "Detection status cannot be empty."
                        )

                    message_count = int(
                        record["message_count"]
                    )

                    messages_per_second = float(
                        record["messages_per_second"]
                    )

                    if message_count < 0:
                        raise ValueError(
                            "Message count cannot be negative."
                        )

                    if messages_per_second < 0:
                        raise ValueError(
                            "Messages/sec cannot be negative."
                        )

                    loaded_data.append({
                        "traffic_type": traffic_type,
                        "can_id": can_id,
                        "message_count": message_count,
                        "messages_per_second": messages_per_second,
                        "detection_status": detection_status,
                    })

                except (ValueError, KeyError) as error:
                    raise ValueError(
                        f"Invalid data on CSV line {line_number}: {error}"
                    ) from error

        return loaded_data

    # --------------------------------------------------
    # REFRESH SAMPLE DATA
    # --------------------------------------------------

    def refresh_sample_data(self):

        reply = QMessageBox.question(
            self,
            "Refresh Sample Data",
            "This will replace the currently displayed data "
            "with demonstration data.\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        self.sample_data = [
            {
                "traffic_type": "Normal",
                "can_id": "0x123",
                "message_count": random.randint(150, 300),
                "messages_per_second": round(
                    random.uniform(15, 30), 1
                ),
                "detection_status": "Normal",
            },
            {
                "traffic_type": "Normal",
                "can_id": "0x456",
                "message_count": random.randint(100, 220),
                "messages_per_second": round(
                    random.uniform(10, 22), 1
                ),
                "detection_status": "Normal",
            },
            {
                "traffic_type": "Simulated High-Rate",
                "can_id": "0x123",
                "message_count": random.randint(800, 1500),
                "messages_per_second": round(
                    random.uniform(80, 150), 1
                ),
                "detection_status": "Suspicious",
            },
            {
                "traffic_type": "Simulated High-Rate",
                "can_id": "0x456",
                "message_count": random.randint(700, 1200),
                "messages_per_second": round(
                    random.uniform(70, 120), 1
                ),
                "detection_status": "Suspicious",
            },
        ]

        self.data_source = "Sample demonstration data"

        self.update_dashboard(update_time=True)


# ------------------------------------------------------
# APPLICATION ENTRY POINT
# ------------------------------------------------------

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = CANSentinelDashboard()
    window.show()

    sys.exit(app.exec_())