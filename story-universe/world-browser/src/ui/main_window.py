# main_window.py: Main window for World Browser UI
#
# This module provides a basic PySide6 main window integrating the event log and timeline panels.

from PySide6.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout
from .panels.event_log import EventLogPanel
from .panels.timeline import TimelinePanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("World Browser")
        self.resize(800, 600)
        self.tabs = QTabWidget()
        self.event_log = EventLogPanel()
        self.timeline = TimelinePanel()
        self.tabs.addTab(self.event_log, "Event Log")
        self.tabs.addTab(self.timeline, "Timeline")
        central = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def add_event(self, event_str):
        self.event_log.add_event(event_str)
        self.timeline.add_event(event_str)


# Launch the application if run as a script or module
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
