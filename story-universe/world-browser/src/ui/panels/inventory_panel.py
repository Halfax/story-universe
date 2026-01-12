from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel, QHBoxLayout
from PySide6.QtCore import Qt
import urllib.request, urllib.error, json


class InventoryPanel(QWidget):
    """Displays inventory items for an owner (character or location)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.owner_type = None
        self.owner_id = None

    def setup_ui(self):
        layout = QVBoxLayout()
        self.title = QLabel("Inventory")
        self.list_widget = QListWidget()
        btn_row = QWidget()
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        self.refresh_btn = QPushButton("Refresh")
        self.use_btn = QPushButton("Use Selected")
        self.refresh_btn.clicked.connect(self.on_refresh)
        self.use_btn.clicked.connect(self.on_use_selected)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.use_btn)
        btn_row.setLayout(btn_layout)

        layout.addWidget(self.title)
        layout.addWidget(self.list_widget)
        layout.addWidget(btn_row)
        self.setLayout(layout)

    def clear(self):
        self.list_widget.clear()
        self.owner_type = None
        self.owner_id = None

    def on_refresh(self):
        if self.owner_type and self.owner_id is not None:
            self.refresh(self.owner_type, self.owner_id)

    def refresh(self, owner_type: str, owner_id: str):
        """Fetch inventory from backend and populate list."""
        self.owner_type = owner_type
        self.owner_id = str(owner_id)
        url = f"{self._base_url()}/world/inventory/{owner_type}/{owner_id}"
        try:
            with urllib.request.urlopen(url, timeout=4) as resp:
                body = resp.read()
                items = json.loads(body)
        except Exception:
            items = []
        self.list_widget.clear()
        for it in items:
            # item row may be dict or simple string
            if isinstance(it, dict):
                label = f"[{it.get('id')}] {it.get('name') or it.get('label') or it.get('sku') or 'item'} x{it.get('quantity',1)}"
            else:
                label = str(it)
            self.list_widget.addItem(label)

    def _base_url(self) -> str:
        # read environment variable if present to match MainWindow behavior
        import os
        base = os.environ.get('CHRONICLE_BASE_URL') or os.environ.get('CHRONICLE_BASE_URL') or 'http://127.0.0.1:8001'
        return base

    def on_use_selected(self):
        """Attempt to trigger a use decision for the selected inventory item.

        This sends a POST to `/world/inventory/{inventory_id}/use_decision` if possible.
        """
        sel = self.list_widget.currentItem()
        if not sel:
            return
        text = sel.text()
        # try to parse leading [id]
        import re, time
        m = re.match(r"\[(\d+)\]", text)
        if not m:
            return
        inventory_id = m.group(1)
        url = f"{self._base_url()}/world/inventory/{inventory_id}/use_decision"
        payload = {'character_id': None, 'quantity': 1}
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                body = resp.read()
                result = json.loads(body)
        except Exception as e:
            result = {'status': 'error', 'reason': str(e)}
        # reflect result in the UI
        self.list_widget.addItem(f"Action result: {result.get('status')} {result.get('reason','')}")
