# timeline.py: Interactive Timeline Panel for World Browser
#
# This module provides an interactive timeline visualization for displaying
# and navigating chronological events in the story universe.

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QToolBar,
                              QLabel, QSizePolicy)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon

# Import visualization components
from visualization.timeline_renderer import TimelineView, TimelineRenderer

class TimelinePanel(QWidget):
    """Interactive timeline panel for visualizing chronological events."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create toolbar
        self.toolbar = QToolBar("Timeline Tools")
        self.toolbar.setIconSize(QSize(16, 16))
        
        # Add actions
        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.setShortcut("Ctrl++")
        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_fit_action = QAction("Fit to View", self)
        self.zoom_fit_action.setShortcut("Ctrl+0")
        
        # Add actions to toolbar
        self.toolbar.addAction(self.zoom_in_action)
        self.toolbar.addAction(self.zoom_out_action)
        self.toolbar.addAction(self.zoom_fit_action)
        
        # Create timeline view
        self.timeline_view = TimelineView()
        self.timeline_view.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        
        # Add to layout
        layout.addWidget(self.toolbar)
        layout.addWidget(self.timeline_view)
        
        # Initialize timeline renderer
        self.renderer = TimelineRenderer(self.timeline_view)
        
    def setup_connections(self):
        """Connect signals and slots."""
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.zoom_fit_action.triggered.connect(self.zoom_fit)
        
    def zoom_in(self):
        """Zoom in on the timeline."""
        self.timeline_view.zoom_in()
        
    def zoom_out(self):
        """Zoom out from the timeline."""
        self.timeline_view.zoom_out()
        
    def zoom_fit(self):
        """Zoom to fit all events in the view."""
        self.timeline_view.zoom_fit()
        
    def add_event(self, event_data):
        """Add an event to the timeline.
        
        Args:
            event_data (dict): Dictionary containing event details.
                Required keys: 'id', 'start', 'title'
                Optional keys: 'end', 'description', 'track', 'color'
        """
        track_id = event_data.get('track', 'default')
        self.renderer.add_event(
            event_id=event_data.get('id'),
            track_id=track_id,
            start=event_data.get('start'),
            end=event_data.get('end', event_data.get('start')),
            title=event_data.get('title', 'Untitled Event'),
            description=event_data.get('description', ''),
            color=event_data.get('color')
        )
        
    def add_track(self, track_id, name, **kwargs):
        """Add a track to the timeline.
        
        Args:
            track_id (str): Unique identifier for the track
            name (str): Display name for the track
            **kwargs: Additional track properties (color, etc.)
        """
        self.renderer.add_track(track_id, name, **kwargs)
        
    def set_time_range(self, start, end):
        """Set the visible time range.
        
        Args:
            start (datetime): Start of the time range
            end (datetime): End of the time range
        """
        self.renderer.set_time_range(start, end)
        
    def refresh(self):
        """Refresh the timeline view."""
        self.timeline_view.redraw()
        
    def clear(self):
        """Clear all events from the timeline."""
        # Implementation depends on the TimelineRenderer's clear method
        if hasattr(self.renderer, 'clear'):
            self.renderer.clear()
