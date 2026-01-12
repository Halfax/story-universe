from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import math

from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem, 
                              QGraphicsTextItem, QGraphicsRectItem, QGraphicsLineItem,
                              QMenu, QGraphicsSceneMouseEvent, QGraphicsSceneWheelEvent,
                              QApplication, QStyleOptionGraphicsItem, QWidget)
from PySide6.QtCore import (Qt, QPointF, QRectF, QLineF, QTimer, QSizeF, 
                           QEasingCurve, QPropertyAnimation, QObject, Property,
                           Signal, Slot, QDateTime, QTimeZone)
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QFont, QPainterPath, 
                          QLinearGradient, QRadialGradient, QPainterPathStroker,
                          QFontMetricsF, QTransform)

class TimeScale(Enum):
    YEARS = 0
    MONTHS = 1
    DAYS = 2
    HOURS = 3
    MINUTES = 4

class TimelineView(QGraphicsView):
    """Interactive timeline view for displaying events chronologically."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up the scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Configure the view
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | 
                           QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # Timeline properties
        self.start_date = datetime.now() - timedelta(days=365)
        self.end_date = datetime.now()
        self.current_scale = TimeScale.MONTHS
        self.visible_start = self.start_date
        self.visible_end = self.end_date
        self.zoom_level = 1.0
        
        # Visual settings
        self.time_ruler_height = 40
        self.track_height = 60
        self.track_spacing = 20
        self.margin = 20
        self.minor_tick_height = 15
        self.major_tick_height = 30
        
        # Animation
        self.animation = QPropertyAnimation(self, b"view_rect")
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setDuration(300)
        
        # Data
        self.tracks = {}  # Track ID -> Track data
        self.events = {}  # Event ID -> Event data
        self.categories = {}  # Category ID -> Category data
        
        # Current selection
        self.selected_event = None
        
        # Initialize the timeline
        self.setup_timeline()
        
    def setup_timeline(self):
        """Set up the initial timeline visualization."""
        self.scene.clear()
        self.draw_time_ruler()
        
    def draw_time_ruler(self):
        """Draw the time ruler with ticks and labels."""
        # Clear existing ruler items
        for item in self.scene.items():
            if hasattr(item, 'is_ruler') and item.is_ruler:
                self.scene.removeItem(item)
        
        # Calculate time range and major/minor intervals
        time_range = (self.visible_end - self.visible_start).total_seconds()
        if time_range <= 0:
            return
            
        # Determine major and minor tick intervals based on scale
        if self.current_scale == TimeScale.YEARS:
            major_interval = 365 * 24 * 3600  # 1 year in seconds
            minor_interval = 30 * 24 * 3600   # 1 month in seconds
            time_format = "yyyy"
        elif self.current_scale == TimeScale.MONTHS:
            major_interval = 30 * 24 * 3600   # 1 month in seconds
            minor_interval = 7 * 24 * 3600     # 1 week in seconds
            time_format = "MMM yyyy"
        elif self.current_scale == TimeScale.DAYS:
            major_interval = 24 * 3600         # 1 day in seconds
            minor_interval = 6 * 3600           # 6 hours in seconds
            time_format = "MMM d, yyyy"
        elif self.current_scale == TimeScale.HOURS:
            major_interval = 3600               # 1 hour in seconds
            minor_interval = 15 * 60             # 15 minutes in seconds
            time_format = "h:mm ap"
        else:  # MINUTES
            major_interval = 60                 # 1 minute in seconds
            minor_interval = 15                 # 15 seconds
            time_format = "h:mm:ss ap"
        
        # Draw the ruler background
        ruler_rect = QRectF(0, 0, self.width(), self.time_ruler_height)
        ruler = self.scene.addRect(ruler_rect, QPen(Qt.NoPen), QBrush(QColor(240, 240, 240)))
        ruler.is_ruler = True
        ruler.setZValue(100)
        
        # Draw major and minor ticks
        current = self.visible_start
        while current <= self.visible_end:
            x = self.date_to_x(current)
            
            # Draw major tick and label
            if current.minute == 0 or self.current_scale in [TimeScale.YEARS, TimeScale.MONTHS, TimeScale.DAYS]:
                tick = self.scene.addLine(x, 0, x, self.major_tick_height, QPen(Qt.black, 1.5))
                tick.is_ruler = True
                tick.setZValue(101)
                
                # Add date/time label
                label = self.scene.addText(current.strftime(time_format))
                label.setDefaultTextColor(Qt.black)
                label.setPos(x + 5, 5)
                label.is_ruler = True
                label.setZValue(101)
            # Draw minor tick
            else:
                tick = self.scene.addLine(x, 0, x, self.minor_tick_height, QPen(Qt.gray, 0.5))
                tick.is_ruler = True
                tick.setZValue(100)
            
            # Move to next interval
            if self.current_scale == TimeScale.YEARS:
                current = current.replace(year=current.year + 1)
            elif self.current_scale == TimeScale.MONTHS:
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
            else:
                current = current + timedelta(seconds=minor_interval)
        
        # Draw current time indicator
        now = datetime.now()
        if self.visible_start <= now <= self.visible_end:
            x = self.date_to_x(now)
            now_line = self.scene.addLine(x, 0, x, self.height(), QPen(Qt.red, 2, Qt.DashLine))
            now_line.is_ruler = True
            now_line.setZValue(99)
    
    def date_to_x(self, date: datetime) -> float:
        """Convert a datetime to an x-coordinate in the view."""
        if self.visible_end == self.visible_start:
            return 0
            
        view_width = self.width()
        total_seconds = (self.visible_end - self.visible_start).total_seconds()
        seconds = (date - self.visible_start).total_seconds()
        
        return (seconds / total_seconds) * view_width
    
    def x_to_date(self, x: float) -> datetime:
        """Convert an x-coordinate to a datetime."""
        if self.width() == 0:
            return self.visible_start
            
        total_seconds = (self.visible_end - self.visible_start).total_seconds()
        seconds = (x / self.width()) * total_seconds
        
        return self.visible_start + timedelta(seconds=seconds)
    
    def add_track(self, track_id: str, name: str, **kwargs):
        """Add a track to the timeline."""
        self.tracks[track_id] = {
            'id': track_id,
            'name': name,
            'visible': True,
            'color': kwargs.get('color', QColor(200, 200, 255)),
            'events': []
        }
        self.update_tracks()
    
    def add_event(self, event_id: str, track_id: str, start: datetime, end: datetime, 
                 title: str, description: str = "", **kwargs):
        """Add an event to the timeline."""
        if track_id not in self.tracks:
            self.add_track(track_id, track_id.capitalize())
            
        event = {
            'id': event_id,
            'track_id': track_id,
            'start': start,
            'end': end,
            'title': title,
            'description': description,
            'color': kwargs.get('color', QColor(100, 150, 255)),
            'selected': False,
            'item': None
        }
        
        self.events[event_id] = event
        self.tracks[track_id]['events'].append(event_id)
        
        self.update_events()
        return event
    
    def update_tracks(self):
        """Update the visualization of tracks."""
        # Clear existing track items
        for item in self.scene.items():
            if hasattr(item, 'is_track') and item.is_track:
                self.scene.removeItem(item)
        
        # Draw tracks
        y = self.time_ruler_height + 10
        for i, (track_id, track) in enumerate(self.tracks.items()):
            if not track['visible']:
                continue
                
            # Draw track background
            track_rect = QRectF(0, y, self.width(), self.track_height)
            track_bg = self.scene.addRect(
                track_rect, 
                QPen(Qt.gray, 0.5), 
                QBrush(track['color'].lighter(120))
            )
            track_bg.is_track = True
            track_bg.track_id = track_id
            track_bg.setZValue(0)
            
            # Draw track label
            label = self.scene.addText(track['name'])
            label.setDefaultTextColor(Qt.black)
            label.setPos(5, y + 5)
            label.is_track = True
            label.setZValue(10)
            
            y += self.track_height + self.track_spacing
    
    def update_events(self):
        """Update the visualization of events."""
        # Clear existing event items
        for item in self.scene.items():
            if hasattr(item, 'is_event') and item.is_event:
                self.scene.removeItem(item)
        
        # Draw events on their respective tracks
        track_y = {}
        y = self.time_ruler_height + 10
        
        for track_id, track in self.tracks.items():
            if not track['visible']:
                continue
                
            track_y[track_id] = y
            y += self.track_height + self.track_spacing
            
            for event_id in track['events']:
                if event_id not in self.events:
                    continue
                    
                event = self.events[event_id]
                x1 = self.date_to_x(event['start'])
                x2 = self.date_to_x(event['end']) if event['end'] > event['start'] else x1 + 10
                
                # Create event rectangle
                event_rect = QRectF(
                    x1, 
                    track_y[track_id] + 5, 
                    max(5, x2 - x1),  # Minimum width of 5 pixels
                    self.track_height - 10
                )
                
                # Create event item
                event_item = self.scene.addRect(
                    event_rect,
                    QPen(Qt.black, 1),
                    QBrush(event['color'])
                )
                
                # Add event properties
                event_item.is_event = True
                event_item.event_id = event_id
                event_item.setZValue(20)
                event_item.setToolTip(f"<b>{event['title']}</b><br/>{event['description']}")
                
                # Add event title
                if event_rect.width() > 50:  # Only show title if there's enough space
                    title = self.scene.addText(event['title'])
                    title.setDefaultTextColor(Qt.black)
                    title.setPos(x1 + 5, track_y[track_id] + 10)
                    title.is_event = True
                    title.event_id = event_id
                    title.setZValue(21)
                    
                    # Make text fit within the event
                    text_width = title.boundingRect().width()
                    if text_width > event_rect.width() - 10:
                        title.setScale((event_rect.width() - 10) / text_width)
                
                event['item'] = event_item
    
    def zoom_in(self):
        """Zoom in on the timeline."""
        self.zoom_level *= 1.2
        self.update_visible_range()
    
    def zoom_out(self):
        """Zoom out from the timeline."""
        self.zoom_level = max(0.1, self.zoom_level / 1.2)
        self.update_visible_range()
    
    def zoom_fit(self):
        """Zoom to fit the entire time range."""
        self.zoom_level = 1.0
        self.visible_start = self.start_date
        self.visible_end = self.end_date
        self.update_visible_range()
    
    def update_visible_range(self):
        """Update the visible time range based on zoom level and scroll position."""
        total_range = self.end_date - self.start_date
        visible_range = total_range / self.zoom_level
        
        # Center the visible range on the current center
        current_center = self.visible_start + (self.visible_end - self.visible_start) / 2
        half_range = visible_range / 2
        
        self.visible_start = max(self.start_date, current_center - half_range)
        self.visible_end = min(self.end_date, current_center + half_range)
        
        # If we hit a boundary, adjust the other side
        if self.visible_start == self.start_date:
            self.visible_end = min(self.end_date, self.start_date + visible_range)
        elif self.visible_end == self.end_date:
            self.visible_start = max(self.start_date, self.end_date - visible_range)
        
        self.redraw()
    
    def redraw(self):
        """Redraw the entire timeline."""
        self.draw_time_ruler()
        self.update_tracks()
        self.update_events()
    
    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
        self.redraw()
    
    def wheelEvent(self, event):
        """Handle zooming with the mouse wheel."""
        if event.modifiers() & Qt.ControlModifier:
            # Zoom in/out with Ctrl + Wheel
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Default scrolling behavior
            super().wheelEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)

class TimelineRenderer:
    """High-level interface for the timeline visualization."""
    def __init__(self, view: TimelineView = None):
        self.view = view or TimelineView()
    
    def add_event(self, event_id: str, track_id: str, start: datetime, end: datetime, 
                 title: str, description: str = "", **kwargs):
        """Add an event to the timeline."""
        return self.view.add_event(event_id, track_id, start, end, title, description, **kwargs)
    
    def add_track(self, track_id: str, name: str, **kwargs):
        """Add a track to the timeline."""
        self.view.add_track(track_id, name, **kwargs)
    
    def set_time_range(self, start: datetime, end: datetime):
        """Set the overall time range of the timeline."""
        self.view.start_date = min(start, end)
        self.view.end_date = max(start, end)
        self.view.visible_start = self.view.start_date
        self.view.visible_end = self.view.end_date
        self.view.redraw()
    
    def zoom_to_fit(self):
        """Zoom to fit all events in the view."""
        self.view.zoom_fit()
    
    def get_view(self) -> TimelineView:
        """Get the underlying QGraphicsView widget."""
        return self.view
