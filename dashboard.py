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

    REQUIRED_COLUMNS = {
        "traffic_type",
        "can_id",
        "message_count",
        "messages_per_second",
        "detection_status",
    }

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "CAN-Sentinel | ECU Security Dashboard"
        )
        self.resize(1150, 700)

        # Sample demonstration data only.
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

        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a;
            }

            QWidget {
                font-family: Segoe UI;
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
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
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

    def init_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()

        title_layout = QVBoxLayout()

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

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        self.load_button = QPushButton("Load CSV")
        self.load_button.clicked.connect(self.load_csv)
        header_layout.addWidget(self.load_button)

        self.refresh_button = QPushButton(
            "Refresh Sample Data"
        )
        self.refresh_button.clicked.connect(
            self.refresh_sample_data
        )
        header_layout.addWidget(self.refresh_button)

        main_layout.addLayout(header_layout)

        # Summary cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.total_messages_value = self.create_card(
            cards_layout,
            "TOTAL MESSAGES",
            "0",
            "#60a5fa"
        )

        self.active_ids_value = self.create_card(
            cards_layout,
            "UNIQUE CAN IDs",
            "0",
            "#34d399"
        )

        self.normal_value = self.create_card(
            cards_layout,
            "NORMAL ROWS",
            "0",
            "#34d399"
        )

        self.alerts_value = self.create_card(
            cards_layout,
            "SUSPICIOUS ROWS",
            "0",
            "#fb7185"
        )

        main_layout.addLayout(cards_layout)

        table_title = QLabel("CAN Traffic Overview")
        table_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #f8fafc;
        """)
        main_layout.addWidget(table_title)

        # Five-column traffic table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Traffic Type",
            "CAN ID",
            "Message Count",
            "Messages/sec",
            "Detection Status",
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

        self.last_refresh_label = QLabel(
            "Data source: Sample demonstration data"
        )
        self.last_refresh_label.setAlignment(Qt.AlignCenter)
        self.last_refresh_label.setStyleSheet(
            "color: #94a3b8; font-size: 12px;"
        )
        main_layout.addWidget(self.last_refresh_label)

        footer = QLabel(
            "CAN-Sentinel | Dashboard Module | Day 4"
        )
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(
            "color: #64748b; font-size: 12px; padding: 5px;"
        )
        main_layout.addWidget(footer)

        self.update_dashboard(
            self.sample_data,
            "Sample demonstration data"
        )

    def create_card(self, layout, heading, value, accent_color):

        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(100)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 12, 15, 12)

        heading_label = QLabel(heading)
        heading_label.setStyleSheet("""
            font-size: 10px;
            font-weight: bold;
            color: #94a3b8;
        """)

        value_label = QLabel(value)
        value_label.setStyleSheet(
            f"font-size: 27px; font-weight: bold; "
            f"color: {accent_color};"
        )

        card_layout.addWidget(heading_label)
        card_layout.addWidget(value_label)
        card_layout.addStretch()

        layout.addWidget(card)

        return value_label

    def update_dashboard(self, data, source_name):

        # Store the currently displayed data.
        self.current_data = data

        self.table.setRowCount(len(data))

        for row, message in enumerate(data):

            values = [
                message["traffic_type"],
                message["can_id"],
                str(message["message_count"]),
                str(message["messages_per_second"]),
                message["detection_status"],
            ]

            for column, value in enumerate(values):

                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)

                if column == 4:
                    status = value.strip().lower()

                    if status == "normal":
                        item.setForeground(
                            Qt.GlobalColor.green
                        )
                    elif status in {
                        "suspicious",
                        "detected",
                        "attack",
                    }:
                        item.setForeground(
                            Qt.GlobalColor.red
                        )
                    else:
                        item.setForeground(
                            Qt.GlobalColor.yellow
                        )

                self.table.setItem(row, column, item)

            self.table.setRowHeight(row, 42)

        total_messages = sum(
            int(item["message_count"])
            for item in data
        )

        unique_ids = len({
            item["can_id"] for item in data
        })

        normal_rows = sum(
            1 for item in data
            if item["detection_status"].strip().lower()
            == "normal"
        )

        suspicious_rows = sum(
            1 for item in data
            if item["detection_status"].strip().lower()
            in {"suspicious", "detected", "attack"}
        )

        self.total_messages_value.setText(
            str(total_messages)
        )
        self.active_ids_value.setText(str(unique_ids))
        self.normal_value.setText(str(normal_rows))
        self.alerts_value.setText(str(suspicious_rows))

        current_time = datetime.now().strftime(
            "%d-%m-%Y %I:%M:%S %p"
        )

        self.last_refresh_label.setText(
            f"Source: {source_name} | Last updated: {current_time}"
        )

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
                        "The CSV file is empty or has no header row."
                    )

                # Ignore surrounding whitespace and case in headers.
                original_headers = reader.fieldnames
                normalized_headers = {
                    header.strip().lower(): header
                    for header in original_headers
                    if header
                }

                missing = (
                    self.REQUIRED_COLUMNS
                    - set(normalized_headers.keys())
                )

                if missing:
                    raise ValueError(
                        "Missing required columns: "
                        + ", ".join(sorted(missing))
                        + "\nPlease use the CSV format shown "
                        "in the README."
                    )

                for line_number, row in enumerate(
                    reader, start=2
                ):

                    # Skip completely blank rows.
                    if not any(
                        value and value.strip()
                        for value in row.values()
                        if value is not None
                    ):
                        continue

                    record = {
                        key: (
                            row.get(original_key, "") or ""
                        ).strip()
                        for key, original_key
                        in normalized_headers.items()
                    }

                    try:
                        message_count = int(
                            record["message_count"]
                        )
                        messages_per_second = float(
                            record["messages_per_second"]
                        )

                        if message_count < 0:
                            raise ValueError(
                                "message_count cannot be negative"
                            )

                        if messages_per_second < 0:
                            raise ValueError(
                                "messages_per_second cannot be negative"
                            )

                        if not record["can_id"]:
                            raise ValueError(
                                "can_id cannot be empty"
                            )

                        if not record["traffic_type"]:
                            raise ValueError(
                                "traffic_type cannot be empty"
                            )

                        if not record["detection_status"]:
                            raise ValueError(
                                "detection_status cannot be empty"
                            )

                    except (ValueError, TypeError) as error:
                        raise ValueError(
                            f"Invalid data on CSV line "
                            f"{line_number}: {error}"
                        ) from error

                    loaded_data.append({
                        "traffic_type": record["traffic_type"],
                        "can_id": record["can_id"],
                        "message_count": message_count,
                        "messages_per_second": messages_per_second,
                        "detection_status": record[
                            "detection_status"
                        ],
                    })

            if not loaded_data:
                raise ValueError(
                    "No traffic records were found in the CSV."
                )

            # Update only after the complete file validates.
            self.update_dashboard(
                loaded_data,
                file_path
            )

            QMessageBox.information(
                self,
                "CSV Loaded",
                f"Successfully loaded {len(loaded_data)} rows."
            )

        except (OSError, UnicodeError, csv.Error, ValueError) as error:
            QMessageBox.critical(
                self,
                "CSV Loading Error",
                f"Could not load the selected CSV file.\n\n{error}"
            )

    def refresh_sample_data(self):

        # Refresh uses demonstration data, not actual CAN traffic.
        new_data = []

        for original in self.sample_data:

            count = random.randint(10, 100)

            new_data.append({
                "traffic_type": original["traffic_type"],
                "can_id": original["can_id"],
                "message_count": count,
                "messages_per_second": round(
                    count / 1.0, 2
                ),
                "detection_status": (
                    "Suspicious" if count > 70 else "Normal"
                ),
            })

        self.update_dashboard(
            new_data,
            "Random sample demonstration data"
        )


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = CANSentinelDashboard()
    window.show()

    sys.exit(app.exec_())