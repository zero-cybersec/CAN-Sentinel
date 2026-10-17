import sys
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
)

from PyQt5.QtCore import Qt, QTimer


class CANSentinelDashboard(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "CAN-Sentinel | ECU Security Dashboard"
        )
        self.resize(1000, 650)

        # Demonstration data only; not live CAN traffic.
        self.sample_data = [
            {"can_id": "0x123", "count": 25, "status": "Normal"},
            {"can_id": "0x456", "count": 18, "status": "Normal"},
            {"can_id": "0x789", "count": 10, "status": "Monitoring"},
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

    def init_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(20)

        # Header
        heading_layout = QHBoxLayout()

        title = QLabel("CAN-SENTINEL")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #60a5fa;
        """)

        subtitle = QLabel(
            "Automotive ECU Intrusion Detection System"
        )
        subtitle.setStyleSheet(
            "font-size: 13px; color: #94a3b8;"
        )

        title_layout = QVBoxLayout()
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        heading_layout.addLayout(title_layout)
        heading_layout.addStretch()

        self.refresh_button = QPushButton(
            "Refresh Dashboard"
        )
        self.refresh_button.clicked.connect(
            self.refresh_dashboard
        )

        heading_layout.addWidget(self.refresh_button)
        main_layout.addLayout(heading_layout)

        # Summary cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        self.total_messages_value = self.create_card(
            cards_layout,
            "TOTAL CAN MESSAGES",
            "0",
            "#60a5fa"
        )

        self.active_ids_value = self.create_card(
            cards_layout,
            "ACTIVE CAN IDs",
            "0",
            "#34d399"
        )

        self.alerts_value = self.create_card(
            cards_layout,
            "MONITORING ALERTS",
            "0",
            "#fb923c"
        )

        main_layout.addLayout(cards_layout)

        # Table heading
        table_title = QLabel("CAN Traffic Overview")
        table_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #f8fafc;
        """)

        main_layout.addWidget(table_title)

        # Traffic table
        self.table = QTableWidget(0, 3)

        self.table.setHorizontalHeaderLabels([
            "CAN ID",
            "Message Count",
            "Status"
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

        # Last refreshed time
        self.last_refresh_label = QLabel(
            "Last refreshed: Not yet"
        )
        self.last_refresh_label.setAlignment(
            Qt.AlignCenter
        )
        self.last_refresh_label.setStyleSheet(
            "color: #94a3b8; font-size: 12px;"
        )

        main_layout.addWidget(self.last_refresh_label)

        # Footer
        footer = QLabel(
            "CAN-Sentinel | Dashboard Module | Day 3"
        )
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(
            "color: #64748b; font-size: 12px; padding: 8px;"
        )

        main_layout.addWidget(footer)

        # Display initial data
        self.update_dashboard(update_time=False)

    def create_card(
        self, layout, heading, value, accent_color
    ):

        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(115)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 15, 18, 15)

        heading_label = QLabel(heading)
        heading_label.setStyleSheet("""
            font-size: 11px;
            font-weight: bold;
            color: #94a3b8;
        """)

        value_label = QLabel(value)
        value_label.setStyleSheet(
            f"font-size: 30px; font-weight: bold; "
            f"color: {accent_color};"
        )

        card_layout.addWidget(heading_label)
        card_layout.addWidget(value_label)
        card_layout.addStretch()

        layout.addWidget(card)

        return value_label

    def update_dashboard(self, update_time=True):

        self.table.setRowCount(len(self.sample_data))

        for row, message in enumerate(self.sample_data):

            values = [
                message["can_id"],
                str(message["count"]),
                message["status"]
            ]

            for column, value in enumerate(values):

                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)

                if column == 2:
                    if value == "Normal":
                        item.setForeground(
                            Qt.GlobalColor.green
                        )
                    else:
                        item.setForeground(
                            Qt.GlobalColor.yellow
                        )

                self.table.setItem(row, column, item)

            self.table.setRowHeight(row, 48)

        # Calculate summary values from the displayed data
        total_messages = sum(
            message["count"]
            for message in self.sample_data
        )

        active_ids = len(self.sample_data)

        alerts = sum(
            1 for message in self.sample_data
            if message["status"] == "Monitoring"
        )

        self.total_messages_value.setText(
            str(total_messages)
        )
        self.active_ids_value.setText(
            str(active_ids)
        )
        self.alerts_value.setText(str(alerts))

        if update_time:
            current_time = datetime.now().strftime(
                "%d-%m-%Y %I:%M:%S %p"
            )
            self.last_refresh_label.setText(
                f"Last refreshed: {current_time}"
            )

    def refresh_dashboard(self):

        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Refreshing...")

        QTimer.singleShot(300, self.complete_refresh)

    def complete_refresh(self):

        # Generate new demonstration counts.
        # These values are NOT from a real CAN bus.
        for message in self.sample_data:

            message["count"] = random.randint(10, 100)

            if message["count"] > 70:
                message["status"] = "Monitoring"
            else:
                message["status"] = "Normal"

        self.update_dashboard(update_time=True)

        self.refresh_button.setText("Refresh Dashboard")
        self.refresh_button.setEnabled(True)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = CANSentinelDashboard()
    window.show()

    sys.exit(app.exec_())