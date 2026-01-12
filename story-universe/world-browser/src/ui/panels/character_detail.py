from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt


class CharacterDetailPanel(QWidget):
    """Displays detailed information about a character."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.name_label = QLabel("Name: ")
        self.status_label = QLabel("Status: ")
        self.location_label = QLabel("Location: ")
        self.traits_box = QTextEdit()
        self.traits_box.setReadOnly(True)
        self.traits_box.setFixedHeight(120)

        layout.addWidget(self.name_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.location_label)
        layout.addWidget(QLabel("Traits / Notes:"))
        layout.addWidget(self.traits_box)
        layout.addStretch()
        self.setLayout(layout)

    def clear(self):
        self.name_label.setText("Name: ")
        self.status_label.setText("Status: ")
        self.location_label.setText("Location: ")
        self.traits_box.setPlainText("")

    def load_character(self, char: dict):
        try:
            self.name_label.setText(f"Name: {char.get('name')}")
            self.status_label.setText(f"Status: {char.get('status')}")
            loc = char.get('location_id') or char.get('location') or ''
            self.location_label.setText(f"Location: {loc}")
            traits = char.get('traits') or char.get('metadata') or char.get('notes') or ''
            # Normalize traits to string
            if isinstance(traits, (list, dict)):
                import json
                traits = json.dumps(traits, indent=2)
            self.traits_box.setPlainText(str(traits))
        except Exception:
            self.clear()
