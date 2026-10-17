import sys

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QLabel,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont


class CANSentinelDashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CAN-Sentinel Dashboard")
        self.resize(850, 500)

        # Main layout
        layout = QVBoxLayout()

        # Dashboard title
        title = QLabel("CAN-Sentinel")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(
            "Automotive ECU Intrusion Detection System"
        )
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Summary section
        summary_layout = QHBoxLayout()

        total_messages = sum(
            [25, 18, 10, 45]
        )

        messages_label = QLabel(
            f"Total CAN Messages: {total_messages}"
        )
        messages_label.setFont(QFont("Arial", 12, QFont.Bold))

        status_label = QLabel("System Status: Monitoring")
        status_label.setFont(QFont("Arial", 12, QFont.Bold))

        summary_layout.addWidget(messages_label)
        summary_layout.addWidget(status_label)

        layout.addLayout(summary_layout)

        # CAN message table
        table = QTableWidget(4, 3)

        table.setHorizontalHeaderLabels(
            ["CAN ID", "Message Count", "Status"]
        )

        sample_data = [
            ("0x123", "25", "NORMAL"),
            ("0x456", "18", "NORMAL"),
            ("0x789", "10", "NORMAL"),
            ("0x310", "45", "ANOMALY"),
        ]

        for row, values in enumerate(sample_data):
            for column, value in enumerate(values):

                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)

                if column == 2:
                    if value == "NORMAL":
                        item.setForeground(
                            QColor("green")
                        )
                    elif value == "ANOMALY":
                        item.setForeground(
                            QColor("red")
                        )

                table.setItem(row, column, item)

        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(table)

        # Footer
        footer = QLabel(
            "CAN-Sentinel | Dashboard Module | Day 2"
        )
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        # Main window
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = CANSentinelDashboard()
    window.show()

    sys.exit(app.exec_())