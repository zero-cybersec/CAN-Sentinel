import sys

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QLabel,
)


class CANSentinelDashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CAN-Sentinel Dashboard")
        self.resize(700, 400)

        layout = QVBoxLayout()

        title = QLabel("CAN-Sentinel - ECU Intrusion Detection System")
        layout.addWidget(title)

        table = QTableWidget(3, 3)
        table.setHorizontalHeaderLabels(
            ["CAN ID", "Message Count", "Status"]
        )

        sample_data = [
            ("0x123", "25", "Normal"),
            ("0x456", "18", "Normal"),
            ("0x789", "10", "Monitoring"),
        ]

        for row, values in enumerate(sample_data):
            for column, value in enumerate(values):
                table.setItem(
                    row, column, QTableWidgetItem(value)
                )

        layout.addWidget(table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CANSentinelDashboard()
    window.show()
    sys.exit(app.exec_())