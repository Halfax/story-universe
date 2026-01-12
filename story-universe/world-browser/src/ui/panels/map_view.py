# map_view.py: Interactive Map View Panel for World Browser
#
# This module provides an interactive map visualization for displaying
# locations and their connections in the story universe.

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QToolBar,
                              QLabel, QComboBox, QSizePolicy, QMenu)
from PySide6.QtCore import Qt, QSize, Signal, QPointF
from PySide6.QtGui import QAction, QIcon, QPainter, QPen, QColor

# Import visualization components
from visualization.map_renderer import MapView, MapRenderer

class MapViewPanel(QWidget):
    """Interactive panel for visualizing locations and their connections on a map."""
    
    # Signals
    location_selected = Signal(str)  # Emitted when a location is selected (location_id)
    location_double_clicked = Signal(str)  # Emitted when a location is double-clicked
    connection_selected = Signal(str, str)  # Emitted when a connection is selected (loc1_id, loc2_id)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self.setup_context_menu()
        
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create toolbar
        self.toolbar = QToolBar("Map Tools")
        self.toolbar.setIconSize(QSize(16, 16))
        
        # Add view mode options
        self.toolbar.addWidget(QLabel("View: "))
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["Map View", "Graph View", "Hybrid"])
        self.view_mode_combo.setCurrentIndex(0)
        self.toolbar.addWidget(self.view_mode_combo)
        
        # Add layer controls
        self.toolbar.addSeparator()
        self.toolbar.addWidget(QLabel("Layers: "))
        self.show_locations_action = QAction("Locations", self)
        self.show_locations_action.setCheckable(True)
        self.show_locations_action.setChecked(True)
        self.toolbar.addAction(self.show_locations_action)
        
        self.show_connections_action = QAction("Connections", self)
        self.show_connections_action.setCheckable(True)
        self.show_connections_action.setChecked(True)
        self.toolbar.addAction(self.show_connections_action)
        
        self.show_labels_action = QAction("Labels", self)
        self.show_labels_action.setCheckable(True)
        self.show_labels_action.setChecked(True)
        self.toolbar.addAction(self.show_labels_action)
        
        # Add zoom controls
        self.toolbar.addSeparator()
        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.setShortcut("Ctrl++")
        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_fit_action = QAction("Fit to View", self)
        self.zoom_fit_action.setShortcut("Ctrl+0")
        
        self.toolbar.addAction(self.zoom_in_action)
        self.toolbar.addAction(self.zoom_out_action)
        self.toolbar.addAction(self.zoom_fit_action)
        
        # Create map view
        self.map_view = MapView()
        self.map_view.setRenderHints(
            QPainter.Antialiasing | 
            QPainter.TextAntialiasing | 
            QPainter.SmoothPixmapTransform
        )
        self.map_view.setViewportUpdateMode(MapView.FullViewportUpdate)
        self.map_view.setTransformationAnchor(MapView.AnchorUnderMouse)
        self.map_view.setResizeAnchor(MapView.AnchorViewCenter)
        self.map_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.map_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.map_view.setDragMode(MapView.ScrollHandDrag)
        
        # Add to layout
        layout.addWidget(self.toolbar)
        layout.addWidget(self.map_view)
        
        # Initialize map renderer
        self.renderer = MapRenderer(self.map_view)
        
    def setup_connections(self):
        """Connect signals and slots."""
        # Toolbar actions
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.zoom_fit_action.triggered.connect(self.zoom_fit)
        self.view_mode_combo.currentIndexChanged.connect(self.change_view_mode)
        self.show_locations_action.toggled.connect(self.toggle_locations_visibility)
        self.show_connections_action.toggled.connect(self.toggle_connections_visibility)
        self.show_labels_action.toggled.connect(self.toggle_labels_visibility)
        
        # Map view signals
        self.map_view.location_clicked.connect(self.on_location_clicked)
        self.map_view.location_double_clicked.connect(self.on_location_double_clicked)
        self.map_view.connection_clicked.connect(self.on_connection_clicked)
        
    def setup_context_menu(self):
        """Set up the context menu for the map view."""
        self.map_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.map_view.customContextMenuRequested.connect(self.show_context_menu)
        
        # Create context menu actions
        self.add_location_action = QAction("Add Location", self)
        self.add_location_action.triggered.connect(self.add_location_dialog)
        
        self.add_connection_action = QAction("Add Connection", self)
        self.add_connection_action.triggered.connect(self.add_connection_dialog)
        
        self.delete_selected_action = QAction("Delete Selected", self)
        self.delete_selected_action.triggered.connect(self.delete_selected)
        
        self.arrange_map_action = QAction("Auto-Arrange", self)
        self.arrange_map_action.triggered.connect(self.arrange_map)
        
    def show_context_menu(self, position):
        """Show the context menu at the given position."""
        menu = QMenu()
        menu.addAction(self.add_location_action)
        menu.addAction(self.add_connection_action)
        menu.addSeparator()
        menu.addAction(self.delete_selected_action)
        menu.addAction(self.arrange_map_action)
        menu.exec_(self.map_view.viewport().mapToGlobal(position))
        
    def zoom_in(self):
        """Zoom in on the map."""
        self.map_view.scale(1.2, 1.2)
        
    def zoom_out(self):
        """Zoom out from the map."""
        self.map_view.scale(1/1.2, 1/1.2)
        
    def zoom_fit(self):
        """Zoom to fit the entire map in the view."""
        self.map_view.fitInView(self.map_view.sceneRect(), Qt.KeepAspectRatio)
        
    def change_view_mode(self, index):
        """Change the map view mode."""
        view_modes = ["map", "graph", "hybrid"]
        self.renderer.set_view_mode(view_modes[index])
        
    def toggle_locations_visibility(self, visible):
        """Toggle visibility of location markers."""
        self.renderer.set_locations_visible(visible)
        
    def toggle_connections_visibility(self, visible):
        """Toggle visibility of connections."""
        self.renderer.set_connections_visible(visible)
        
    def toggle_labels_visibility(self, visible):
        """Toggle visibility of labels."""
        self.renderer.set_labels_visible(visible)
        
    def on_location_clicked(self, location_id):
        """Handle location click events."""
        self.location_selected.emit(location_id)
        
    def on_location_double_clicked(self, location_id):
        """Handle location double-click events."""
        self.location_double_clicked.emit(location_id)
        
    def on_connection_clicked(self, loc1_id, loc2_id):
        """Handle connection click events."""
        self.connection_selected.emit(loc1_id, loc2_id)
        
    def add_location(self, location_id, name, pos=None, **kwargs):
        """Add a location to the map.
        
        Args:
            location_id (str): Unique identifier for the location
            name (str): Display name for the location
            pos (QPointF, optional): Position of the location. If None, will be placed automatically.
            **kwargs: Additional location properties (color, size, icon, etc.)
        """
        self.renderer.add_location(location_id, name, pos, **kwargs)
        
    def add_connection(self, loc1_id, loc2_id, **kwargs):
        """Add a connection between two locations.
        
        Args:
            loc1_id (str): ID of the first location
            loc2_id (str): ID of the second location
            **kwargs: Additional connection properties (color, weight, style, etc.)
        """
        self.renderer.add_connection(loc1_id, loc2_id, **kwargs)
        
    def remove_location(self, location_id):
        """Remove a location from the map."""
        self.renderer.remove_location(location_id)
        
    def remove_connection(self, loc1_id, loc2_id):
        """Remove a connection between two locations."""
        self.renderer.remove_connection(loc1_id, loc2_id)
        
    def clear(self):
        """Clear all locations and connections from the map."""
        self.renderer.clear()
        
    def refresh(self):
        """Refresh the map view."""
        self.renderer.refresh()
        
    def arrange_map(self):
        """Auto-arrange the locations on the map."""
        self.renderer.arrange()
        
    def add_location_dialog(self):
        """Show a dialog to add a new location."""
        # Implementation would show a dialog to enter location details
        pass
        
    def add_connection_dialog(self):
        """Show a dialog to add a new connection."""
        # Implementation would show a dialog to select locations and connection properties
        pass
        
    def delete_selected(self):
        """Delete the currently selected items."""
        self.renderer.delete_selected()
        
    def get_selected_locations(self):
        """Get a list of selected location IDs."""
        return self.renderer.get_selected_locations()
        
    def get_selected_connections(self):
        """Get a list of selected connections as (loc1_id, loc2_id) tuples."""
        return self.renderer.get_selected_connections()
        
    def load_map_data(self, map_data):
        """Load map data from a dictionary.
        
        Args:
            map_data (dict): Dictionary containing map data with 'locations' and 'connections' keys
        """
        if 'locations' in map_data:
            for loc_data in map_data['locations']:
                self.add_location(**loc_data)
                
        if 'connections' in map_data:
            for conn_data in map_data['connections']:
                self.add_connection(**conn_data)
                
        # Auto-arrange if there are locations
        if self.renderer.locations:
            self.arrange_map()
