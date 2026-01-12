# event_log.py: Simple event log panel for World Browser UI
#
# This module provides a basic PySide6 widget to display a live feed of events.
# Intended for integration into the main_window.py and timeline.py panels.

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel

class EventLogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Event Log")
        layout = QVBoxLayout()
        self.label = QLabel("Live Event Feed:")
        self.list_widget = QListWidget()
        layout.addWidget(self.label)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def add_event(self, event_str):
        """Append a new event string to the log."""
        self.list_widget.addItem(event_str)
        self.list_widget.scrollToBottom()
