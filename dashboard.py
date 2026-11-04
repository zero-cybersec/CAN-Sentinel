import sys
import csv
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QFrame, QHeaderView, QAbstractItemView, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt


class CANSentinelDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAN-Sentinel | ECU Security Dashboard")
        self.resize(1450, 800)
        self.base_dir = Path(__file__).resolve().parent
        self.default_csv = self.base_dir / "results" / "integration_results.csv"
        self.records = []
        self.data_source = "No integration results loaded"

        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QWidget { font-family: Segoe UI; font-size: 12px; }
            QLabel { color: #e2e8f0; }
            QFrame#card {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #2563eb; color: white; border: none;
                padding: 10px 18px; border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QTableWidget {
                background-color: #1e293b;
                alternate-background-color: #263449;
                color: #e2e8f0; gridline-color: #334155;
                border: 1px solid #334155; border-radius: 8px;
                selection-background-color: #334155; selection-color: white;
            }
            QHeaderView::section {
                background-color: #334155; color: white;
                padding: 9px; border: none; font-weight: bold;
            }
        """)
        self.init_ui()
        if self.default_csv.exists():
            try:
                self.load_integration_csv(str(self.default_csv))
            except (OSError, csv.Error, ValueError) as error:
                QMessageBox.warning(self, "CSV Loading", str(error))
        else:
            self.update_dashboard()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(15)

        heading_layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        title = QLabel("CAN-SENTINEL")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #60a5fa;")
        subtitle = QLabel("Automotive ECU Intrusion Detection Dashboard")
        subtitle.setStyleSheet("font-size: 13px; color: #94a3b8;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        heading_layout.addLayout(title_layout)
        heading_layout.addStretch()

        self.load_button = QPushButton("Load Integration CSV")
        self.load_button.clicked.connect(self.load_csv)
        heading_layout.addWidget(self.load_button)
        self.refresh_button = QPushButton("Reload Default Results")
        self.refresh_button.clicked.connect(self.reload_default_csv)
        heading_layout.addWidget(self.refresh_button)
        main_layout.addLayout(heading_layout)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)
        self.windows_value = self.create_card(cards_layout, "TOTAL WINDOWS", "0", "#60a5fa")
        self.messages_value = self.create_card(cards_layout, "TOTAL MESSAGES", "0", "#34d399")
        self.normal_value = self.create_card(cards_layout, "NORMAL HYBRID", "0", "#34d399")
        self.alerts_value = self.create_card(cards_layout, "DETECTION ALERTS", "0", "#fb7185")
        main_layout.addLayout(cards_layout)

        table_title = QLabel("Detector Predictions")
        table_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        main_layout.addWidget(table_title)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels([
            "Source / Scenario", "Messages", "Avg Interval (ms)",
            "Unique CAN IDs", "ML Prediction", "Anomaly Score",
            "Rate Prediction", "Sequence Prediction", "Hybrid Prediction"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        main_layout.addWidget(self.table)

        self.disclaimer_label = QLabel(
            "Predictions are read from the integration results CSV. "
            "Sequence fields show NOT AVAILABLE if the CSV was generated "
            "before sequence prediction was added."
        )
        self.disclaimer_label.setWordWrap(True)
        self.disclaimer_label.setAlignment(Qt.AlignCenter)
        self.disclaimer_label.setStyleSheet(
            "color: #fbbf24; font-size: 12px; font-weight: bold; padding: 8px;"
        )
        main_layout.addWidget(self.disclaimer_label)

        self.last_refresh_label = QLabel("Source: No file loaded")
        self.last_refresh_label.setAlignment(Qt.AlignCenter)
        self.last_refresh_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        main_layout.addWidget(self.last_refresh_label)

        footer = QLabel("CAN-Sentinel | Dashboard Module")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #64748b; font-size: 11px; padding: 5px;")
        main_layout.addWidget(footer)

    def create_card(self, layout, heading, value, accent_color):
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(100)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)

        heading_label = QLabel(heading)
        heading_label.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #94a3b8;"
        )
        value_label = QLabel(value)
        value_label.setStyleSheet(
            f"font-size: 28px; font-weight: bold; color: {accent_color};"
        )
        card_layout.addWidget(heading_label)
        card_layout.addWidget(value_label)
        card_layout.addStretch()
        layout.addWidget(card)
        return value_label

    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Integration Results CSV",
            str(self.base_dir / "results"), "CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            return
        try:
            self.load_integration_csv(file_path)
            QMessageBox.information(
                self, "CSV Loaded",
                f"Successfully loaded {len(self.records)} integration rows."
            )
        except (OSError, UnicodeError, csv.Error, ValueError) as error:
            QMessageBox.critical(self, "CSV Loading Error", str(error))

    def load_integration_csv(self, file_path):
        required = {
            "source_file", "message_count", "avg_interval_ms",
            "ml_prediction", "anomaly_score",
            "rate_based_prediction", "prediction"
        }
        loaded = []
        with open(file_path, "r", newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            if not reader.fieldnames:
                raise ValueError("CSV must contain a header row.")
            reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
            missing = required - set(reader.fieldnames)
            if missing:
                raise ValueError("Missing integration columns: " + ", ".join(sorted(missing)))
            if "unique_can_ids" not in reader.fieldnames and "can_id" not in reader.fieldnames:
                raise ValueError("CSV must contain either 'unique_can_ids' or 'can_id'.")

            for line_number, row in enumerate(reader, start=2):
                record = {
                    (key or "").strip().lower():
                    (value.strip() if value is not None else "")
                    for key, value in row.items() if key is not None
                }
                try:
                    record["message_count"] = int(record["message_count"])
                    record["avg_interval_ms"] = float(record["avg_interval_ms"])
                    if record.get("unique_can_ids"):
                        record["unique_can_ids"] = int(record["unique_can_ids"])
                    record["anomaly_score"] = float(record["anomaly_score"])
                except (ValueError, KeyError) as error:
                    raise ValueError(f"Invalid value on CSV line {line_number}: {error}") from error
                loaded.append(record)

        if not loaded:
            raise ValueError("The integration CSV contains no data rows.")
        self.records = loaded
        self.data_source = Path(file_path).name
        self.update_dashboard()

    def reload_default_csv(self):
        if not self.default_csv.exists():
            QMessageBox.warning(
                self, "File Not Found",
                f"Default integration file not found:\n{self.default_csv}"
            )
            return
        try:
            self.load_integration_csv(str(self.default_csv))
        except (OSError, csv.Error, ValueError) as error:
            QMessageBox.critical(self, "CSV Loading Error", str(error))

    def update_dashboard(self):
        self.table.setRowCount(len(self.records))
        total_messages = 0
        normal_rows = 0
        alert_rows = 0

        for row_index, record in enumerate(self.records):
            hybrid = record.get("prediction", "NOT AVAILABLE")
            sequence = record.get("sequence_prediction", "NOT AVAILABLE")
            values = [
                record.get("source_file", "Unknown"),
                str(record.get("message_count", "")),
                str(record.get("avg_interval_ms", "")),
                str(record.get("unique_can_ids", record.get("can_id", ""))),
                record.get("ml_prediction", "NOT AVAILABLE"),
                str(record.get("anomaly_score", "")),
                record.get("rate_based_prediction", "NOT AVAILABLE"),
                sequence,
                hybrid
            ]
            total_messages += record.get("message_count", 0)
            if hybrid.strip().upper() in ("NORMAL", "NORMAL_BY_BASELINE"):
                normal_rows += 1
            else:
                alert_rows += 1

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                if column in (4, 6, 7, 8):
                    upper = value.strip().upper()
                    if upper in ("NORMAL", "NORMAL_BY_BASELINE"):
                        item.setForeground(Qt.green)
                    elif upper in (
                        "HIGH_RATE_SUSPECTED", "REPLAY_SUSPECTED",
                        "ANOMALY", "ATTACK"
                    ):
                        item.setForeground(Qt.red)
                    elif upper == "NOT AVAILABLE":
                        item.setForeground(Qt.yellow)
                self.table.setItem(row_index, column, item)
            self.table.setRowHeight(row_index, 38)

        self.windows_value.setText(str(len(self.records)))
        self.messages_value.setText(str(total_messages))
        self.normal_value.setText(str(normal_rows))
        self.alerts_value.setText(str(alert_rows))

        current_time = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
        self.last_refresh_label.setText(
            f"Source: {self.data_source} | Last updated: {current_time}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CANSentinelDashboard()
    window.show()
    sys.exit(app.exec_())
