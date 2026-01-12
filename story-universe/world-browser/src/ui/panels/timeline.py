# timeline.py: Simple timeline panel for World Browser UI
#
# This module provides a basic PySide6 widget to display a timeline of events.
# Intended for integration into the main_window.py and event_log.py panels.

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget

class TimelinePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Timeline")
        layout = QVBoxLayout()
        self.label = QLabel("Event Timeline:")
        self.list_widget = QListWidget()
        layout.addWidget(self.label)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def add_event(self, event_str):
        """Append a new event string to the timeline."""
        self.list_widget.addItem(event_str)
        self.list_widget.scrollToBottom()
