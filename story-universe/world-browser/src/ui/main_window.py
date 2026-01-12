# main_window.py: Main window for World Browser UI
#
# This module provides a basic PySide6 main window integrating the event log and timeline panels.

from PySide6.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import QTimer
from .panels.event_log import EventLogPanel
from .panels.timeline import TimelinePanel
from .panels.character_web import CharacterWebPanel
from .panels.map_view import MapViewPanel
from .panels.character_detail import CharacterDetailPanel
from .panels.inventory_panel import InventoryPanel
import os
import json
from datetime import datetime
import urllib.request
import urllib.error

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("World Browser")
        self.resize(800, 600)
        self.tabs = QTabWidget()
        self.event_log = EventLogPanel()
        self.timeline = TimelinePanel()
        self.character_web = CharacterWebPanel()
        self.map_view_panel = MapViewPanel()
        self.tabs.addTab(self.event_log, "Event Log")
        self.tabs.addTab(self.timeline, "Timeline")
        self.tabs.addTab(self.character_web, "Characters")
        self.tabs.addTab(self.character_detail, "Character Detail")
        self.tabs.addTab(self.map_view_panel, "Map")
        self.tabs.addTab(self.inventory_panel, "Inventory")
        central = QWidget()
        layout = QVBoxLayout()
        # Top controls (test event button, future filters)
        controls = QWidget()
        ctl_layout = QHBoxLayout()
        ctl_layout.setContentsMargins(0, 0, 0, 0)
        self.send_test_btn = QPushButton("Send Test Event")
        self.send_test_btn.clicked.connect(self.on_send_test_clicked)
        ctl_layout.addWidget(self.send_test_btn)
        controls.setLayout(ctl_layout)
        layout.addWidget(controls)
        layout.addWidget(self.tabs)
        central.setLayout(layout)
        self.setCentralWidget(central)
        # API config
        self.mock_mode = os.environ.get("MOCK_MODE", "0") == "1"
        if self.mock_mode:
            self.pi_base = os.environ.get("CHRONICLE_BASE_URL", "http://127.0.0.1:8002")
        else:
            self.pi_base = os.environ.get("CHRONICLE_BASE_URL", "http://127.0.0.1:8001")
        self.seen_ids = set()

        # Start polling for events
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(2000)
        self.poll_timer.timeout.connect(self.fetch_events)
        self.poll_timer.start()
        # Polling backoff state
        self._base_interval = 2000
        self._max_interval = 15000
        self._miss_count = 0

        # World state polling (less frequent)
        self.world_timer = QTimer(self)
        self.world_timer.setInterval(10000)
        self.world_timer.timeout.connect(self.fetch_world)
        self.world_timer.start()
        # Fetch initial world state
        try:
            self.fetch_world()
        except Exception:
            pass
        # Character detail + inventory panels
        self.character_detail = CharacterDetailPanel()
        self.inventory_panel = InventoryPanel()
        # Hook selection from character web to populate details and inventory
        try:
            self.character_web.node_selected.connect(self.on_character_selected)
        except Exception:
            pass

    def add_event(self, event_str):
        # event_str may be a dict or string
        if isinstance(event_str, dict):
            ev = event_str
            title = ev.get('description') or ev.get('data', {}).get('title') or ev.get('type')
            self.event_log.add_event(f"{ev.get('id')}: {title}")
            # Convert timestamp to datetime
            ts = ev.get('timestamp')
            try:
                start = datetime.fromtimestamp(float(ts))
            except Exception:
                start = datetime.now()
            self.timeline.add_event({
                'id': str(ev.get('id')),
                'start': start,
                'title': title,
                'description': ev.get('description', ''),
                'track': ev.get('type', 'events')
            })
        else:
            self.event_log.add_event(str(event_str))

    def fetch_events(self):
        """Poll the Chronicle Keeper for recent events and add new ones to the UI."""
        # Prefer the canonical recent events endpoint; fall back to simpler /events for mock server
        url_candidates = [f"{self.pi_base}/world/events/recent", f"{self.pi_base}/events", f"{self.pi_base}/events/recent"]
        body = None
        for u in url_candidates:
            try:
                with urllib.request.urlopen(u, timeout=2) as resp:
                    body = resp.read()
                    break
            except Exception:
                continue
        if not body:
            return
        try:
            events = json.loads(body)
        except Exception:
            return

        # Normalize common shapes:
        # - list of event dicts
        # - {"events": [...]}
        # - {id: {...}, ...}
        if isinstance(events, dict):
            if 'events' in events and isinstance(events['events'], list):
                events = events['events']
            else:
                # dict mapping ids -> event objects
                possible = []
                for k, v in events.items():
                    if isinstance(v, dict) and ('type' in v or 'timestamp' in v):
                        # ensure id present
                        v.setdefault('id', k)
                        possible.append(v)
                if possible:
                    events = possible
                else:
                    # unknown dict shape; give up
                    return

        # Server returns list of events (most recent first). Add in chronological order.
        new_found = 0
        for raw in reversed(events):
            # tolerate non-dict list entries
            if not isinstance(raw, dict):
                continue
            # normalize individual event fields
            ev = {}
            ev['id'] = raw.get('id') or raw.get('event_id') or raw.get('evt_id')
            ev['timestamp'] = raw.get('timestamp') or raw.get('ts') or raw.get('time')
            ev['type'] = raw.get('type') or raw.get('event_type') or (raw.get('data') or {}).get('type')
            ev['description'] = raw.get('description') or raw.get('desc') or (raw.get('data') or {}).get('description') or ''
            # normalize involved characters/locations which may be stored as JSON strings
            def _parse_field(x):
                if x is None:
                    return []
                if isinstance(x, list):
                    return x
                if isinstance(x, str):
                    try:
                        import ast
                        parsed = ast.literal_eval(x)
                        return parsed if isinstance(parsed, list) else [parsed]
                    except Exception:
                        try:
                            return json.loads(x)
                        except Exception:
                            return [x]
                return [x]

            ev['involved_characters'] = _parse_field(raw.get('involved_characters') or raw.get('characters') or raw.get('participants'))
            ev['involved_locations'] = _parse_field(raw.get('involved_locations') or raw.get('locations'))

            ev_id = ev.get('id')
            if not ev_id:
                # generate a local id if missing
                import time, random
                ev_id = f"local_{int(time.time())}_{random.randint(0,9999)}"
                ev['id'] = ev_id

            if ev_id in self.seen_ids:
                continue
            self.seen_ids.add(ev_id)
            self.add_event(ev)
            new_found += 1

        # Adjust polling interval (simple exponential backoff when no new events)
        try:
            if new_found > 0:
                self._miss_count = 0
                url_candidates = [f"{self.pi_base}/world/state", f"{self.pi_base}/world", f"{self.pi_base}/worlds"]
                body = None
                for u in url_candidates:
                    try:
                        with urllib.request.urlopen(u, timeout=3) as resp:
                            body = resp.read()
                            break
                    except Exception:
                        continue
                if not body:
                    return
                try:
                    data = json.loads(body)
                except Exception:
                    return

                # Try to locate characters and locations under several possible keys
                chars = {}
                if isinstance(data, dict):
                    if 'characters' in data:
                        chars = data.get('characters') or {}
                    elif 'people' in data:
                        chars = data.get('people') or {}
                    else:
                        # maybe top-level is a list
                        if isinstance(data, list):
                            chars = data

                # clear and add nodes
                try:
                    self.character_web.clear()
                    if isinstance(chars, dict):
                        for cid, c in chars.items():
                            name = c.get('name') if isinstance(c, dict) else str(c)
                            self.character_web.add_node(str(cid), name, node_type='character')
                    elif isinstance(chars, list):
                        for c in chars:
                            node_id = str(c.get('id') or c.get('uid') or c.get('name'))
                            name = c.get('name') or c.get('display') or node_id
                            self.character_web.add_node(node_id, name, node_type='character')
                except Exception:
                    pass

                # Locations
                locs = {}
                if isinstance(data, dict):
                    locs = data.get('locations') or data.get('places') or {}
                if isinstance(locs, dict):
                    try:
                        self.map_view_panel.clear()
                        for lid, l in locs.items():
                            name = l.get('name') if isinstance(l, dict) else str(l)
                            self.map_view_panel.add_location(str(lid), name)
                    except Exception:
                        pass
                elif isinstance(locs, list):
                    try:
                        self.map_view_panel.clear()
                        for l in locs:
                            lid = str(l.get('id') or l.get('uid') or l.get('name'))
                            name = l.get('name') or lid
                            self.map_view_panel.add_location(lid, name)
                    except Exception:
                        pass

                def on_character_selected(self, node_id: str):
                    """Load character details and inventory when a node is selected in the graph."""
                    # Attempt to fetch character by id from backend
                    try:
                        import urllib.request, json
                        url = f"{self.pi_base}/world/characters"
                        with urllib.request.urlopen(url, timeout=3) as resp:
                            body = resp.read()
                            chars = json.loads(body)
                    except Exception:
                        chars = []

                    found = None
                    if isinstance(chars, list):
                        for c in chars:
                            if str(c.get('id')) == str(node_id) or str(c.get('name')) == str(node_id):
                                found = c
                                break
                    elif isinstance(chars, dict):
                        found = chars.get(str(node_id))

                    if found:
                        try:
                            self.character_detail.load_character(found)
                        except Exception:
                            pass
                    else:
                        # fallback: use node id as name
                        self.character_detail.load_character({'name': node_id})

                    # Load inventory for this character
                    try:
                        self.inventory_panel.refresh('character', node_id)
                    except Exception:
                        pass
            self.add_event({'id': 'local_error', 'timestamp': int(time.time()), 'type': 'ui_test', 'description': f"send failed: {e}"})

    def fetch_world(self):
        """Fetch world snapshot and populate character/map panels."""
        # Prefer canonical snapshot endpoint first
        url_candidates = [f"{self.pi_base}/world/state", f"{self.pi_base}/world", f"{self.pi_base}/worlds"]
        body = None
        for u in url_candidates:
            try:
                with urllib.request.urlopen(u, timeout=3) as resp:
                    body = resp.read()
                    break
            except Exception:
                continue
        if not body:
            return
        try:
            data = json.loads(body)
        except Exception:
            return

        # Populate character web
        try:
            chars = data.get('characters') or {}
            # clear and add nodes
            self.character_web.clear()
            for cid, c in (chars.items() if isinstance(chars, dict) else enumerate(chars)):
                # accept both dict-of-dicts and list formats
                if isinstance(chars, dict):
                    node_id = str(cid)
                    name = c.get('name')
                else:
                    node_id = str(c.get('id'))
                    name = c.get('name')
                self.character_web.add_node(node_id, name, node_type='character')
        except Exception:
            pass

        # Populate map
        try:
            locs = data.get('locations') or {}
            self.map_view_panel.clear()
            if isinstance(locs, dict):
                for lid, l in locs.items():
                    self.map_view_panel.add_location(str(lid), l.get('name'))
            else:
                for l in locs:
                    self.map_view_panel.add_location(str(l.get('id')), l.get('name'))
        except Exception:
            pass


# Launch the application if run as a script or module
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
