# character_web.py: Interactive Character Relationship Web Panel
#
# This module provides an interactive visualization of character relationships
# using a force-directed graph layout with PySide6 and NetworkX.

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QToolBar, QAction, 
                              QLabel, QComboBox, QSizePolicy, QMenu, QGraphicsView)
from PySide6.QtCore import Qt, QSize, Signal, QPointF
from PySide6.QtGui import QAction, QIcon, QPainter, QPen, QColor

# Import visualization components
from ....visualization.graph_renderer import RelationshipGraph, GraphRenderer

class CharacterWebPanel(QWidget):
    """Interactive panel for visualizing character relationships as a force-directed graph."""
    
    # Signals
    node_selected = Signal(str)  # Emitted when a node is selected (node_id)
    node_double_clicked = Signal(str)  # Emitted when a node is double-clicked
    edge_selected = Signal(str, str)  # Emitted when an edge is selected (source_id, target_id)
    
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
        self.toolbar = QToolBar("Character Web Tools")
        self.toolbar.setIconSize(QSize(16, 16))
        
        # Add layout options
        self.toolbar.addWidget(QLabel("Layout: "))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["Force-Directed", "Circular", "Hierarchical"])
        self.layout_combo.setCurrentIndex(0)
        self.toolbar.addWidget(self.layout_combo)
        
        # Add filter options
        self.toolbar.addSeparator()
        self.toolbar.addWidget(QLabel("Filter: "))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Characters Only", "Factions Only", "Locations Only"])
        self.toolbar.addWidget(self.filter_combo)
        
        # Add zoom actions
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
        
        # Add graph view
        self.graph_view = RelationshipGraph()
        self.graph_view.setRenderHints(
            QPainter.Antialiasing | 
            QPainter.TextAntialiasing | 
            QPainter.SmoothPixmapTransform
        )
        self.graph_view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.graph_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.graph_view.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.graph_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.graph_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.graph_view.setDragMode(QGraphicsView.ScrollHandDrag)
        
        # Add to layout
        layout.addWidget(self.toolbar)
        layout.addWidget(self.graph_view)
        
        # Initialize graph renderer
        self.renderer = GraphRenderer(self.graph_view)
        
    def setup_connections(self):
        """Connect signals and slots."""
        # Toolbar actions
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.zoom_fit_action.triggered.connect(self.zoom_fit)
        self.layout_combo.currentIndexChanged.connect(self.change_layout)
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)
        
        # Graph view signals
        self.graph_view.node_clicked.connect(self.on_node_clicked)
        self.graph_view.node_double_clicked.connect(self.on_node_double_clicked)
        self.graph_view.edge_clicked.connect(self.on_edge_clicked)
        
    def setup_context_menu(self):
        """Set up the context menu for the graph view."""
        self.graph_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.graph_view.customContextMenuRequested.connect(self.show_context_menu)
        
        # Create context menu actions
        self.add_node_action = QAction("Add Node", self)
        self.add_node_action.triggered.connect(self.add_node_dialog)
        
        self.add_edge_action = QAction("Add Edge", self)
        self.add_edge_action.triggered.connect(self.add_edge_dialog)
        
        self.delete_selected_action = QAction("Delete Selected", self)
        self.delete_selected_action.triggered.connect(self.delete_selected)
        
        self.arrange_graph_action = QAction("Arrange Graph", self)
        self.arrange_graph_action.triggered.connect(self.arrange_graph)
        
    def show_context_menu(self, position):
        """Show the context menu at the given position."""
        menu = QMenu()
        menu.addAction(self.add_node_action)
        menu.addAction(self.add_edge_action)
        menu.addSeparator()
        menu.addAction(self.delete_selected_action)
        menu.addAction(self.arrange_graph_action)
        menu.exec_(self.graph_view.viewport().mapToGlobal(position))
        
    def zoom_in(self):
        """Zoom in on the graph."""
        self.graph_view.scale(1.2, 1.2)
        
    def zoom_out(self):
        """Zoom out from the graph."""
        self.graph_view.scale(1/1.2, 1/1.2)
        
    def zoom_fit(self):
        """Zoom to fit the entire graph in the view."""
        self.graph_view.fitInView(self.graph_view.sceneRect(), Qt.KeepAspectRatio)
        
    def change_layout(self, index):
        """Change the graph layout algorithm."""
        layouts = ["force_directed", "circular", "hierarchical"]
        self.renderer.set_layout(layouts[index])
        
    def apply_filter(self, index):
        """Apply a filter to show/hide node types."""
        filters = {
            0: None,  # All
            1: "character",
            2: "faction",
            3: "location"
        }
        self.renderer.apply_filter(filters.get(index))
        
    def on_node_clicked(self, node_id):
        """Handle node click events."""
        self.node_selected.emit(node_id)
        
    def on_node_double_clicked(self, node_id):
        """Handle node double-click events."""
        self.node_double_clicked.emit(node_id)
        
    def on_edge_clicked(self, source_id, target_id):
        """Handle edge click events."""
        self.edge_selected.emit(source_id, target_id)
        
    def add_node(self, node_id, name, node_type="character", **kwargs):
        """Add a node to the graph.
        
        Args:
            node_id (str): Unique identifier for the node
            name (str): Display name for the node
            node_type (str): Type of node (character, faction, location, etc.)
            **kwargs: Additional node properties (color, size, etc.)
        """
        self.renderer.add_node(node_id, name, node_type, **kwargs)
        
    def add_edge(self, source_id, target_id, relationship="", **kwargs):
        """Add an edge between two nodes.
        
        Args:
            source_id (str): ID of the source node
            target_id (str): ID of the target node
            relationship (str): Type of relationship
            **kwargs: Additional edge properties (color, weight, etc.)
        """
        self.renderer.add_edge(source_id, target_id, relationship, **kwargs)
        
    def remove_node(self, node_id):
        """Remove a node from the graph."""
        self.renderer.remove_node(node_id)
        
    def remove_edge(self, source_id, target_id):
        """Remove an edge from the graph."""
        self.renderer.remove_edge(source_id, target_id)
        
    def clear(self):
        """Clear all nodes and edges from the graph."""
        self.renderer.clear()
        
    def refresh(self):
        """Refresh the graph view."""
        self.renderer.refresh()
        
    def arrange_graph(self):
        """Re-arrange the graph using the current layout algorithm."""
        self.renderer.arrange()
        
    def add_node_dialog(self):
        """Show a dialog to add a new node."""
        # Implementation would show a dialog to enter node details
        pass
        
    def add_edge_dialog(self):
        """Show a dialog to add a new edge."""
        # Implementation would show a dialog to select nodes and edge properties
        pass
        
    def delete_selected(self):
        """Delete the currently selected items."""
        self.renderer.delete_selected()
        
    def get_selected_nodes(self):
        """Get a list of selected node IDs."""
        return self.renderer.get_selected_nodes()
        
    def get_selected_edges(self):
        """Get a list of selected edges as (source_id, target_id) tuples."""
        return self.renderer.get_selected_edges()
