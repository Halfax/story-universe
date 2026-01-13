import math
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QMenu, QGraphicsSceneMouseEvent, QGraphicsPathItem
from PySide6.QtCore import Qt, QPointF, Signal, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath
import networkx as nx
from typing import Dict, List, Optional, Tuple, Any

class MapView(QGraphicsView):
    """Interactive map view with zoom and pan functionality."""
    # Signals exposed to UI panels
    location_clicked = Signal(str)
    location_double_clicked = Signal(str)
    connection_clicked = Signal(str, str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.scale_factor = 1.0
        
    def wheelEvent(self, event):
        # Zoom in/out with mouse wheel
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        
        # Save the scene position
        old_pos = self.mapToScene(event.position().toPoint())
        
        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
            
        self.scale(zoom_factor, zoom_factor)
        self.scale_factor *= zoom_factor
        
        # Center the view on the old position
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def mouseReleaseEvent(self, event):
        """Emit signals for clicks on locations or connections."""
        super().mouseReleaseEvent(event)
        try:
            if event.button() == Qt.LeftButton:
                pos = self.mapToScene(event.position().toPoint())
                items = self.scene().items(pos)
                for it in items:
                    # location items store attribute `location_id`
                    try:
                        loc_id = getattr(it, 'location_id', None)
                        if loc_id:
                            try:
                                self.location_clicked.emit(loc_id)
                            except Exception:
                                pass
                            return
                    except Exception:
                        pass
                    # connection/path items
                    if isinstance(it, QGraphicsPathItem):
                        # Attempt to infer endpoints from path points
                        path = it.path()
                        if path.elementCount() >= 2:
                            e0 = path.elementAt(0)
                            e1 = path.elementAt(path.elementCount() - 1)
                            p0 = QPointF(e0.x, e0.y)
                            p1 = QPointF(e1.x, e1.y)
                            # find nearest locations
                            nearest = []
                            renderer = getattr(self, '_map_renderer', None)
                            if renderer:
                                for lid, item in renderer.locations.items():
                                    d0 = (item.pos() - p0).manhattanLength()
                                    d1 = (item.pos() - p1).manhattanLength()
                                    nearest.append((lid, min(d0, d1)))
                            if nearest:
                                nearest.sort(key=lambda x: x[1])
                                a = nearest[0][0]
                                b = nearest[1][0] if len(nearest) > 1 else nearest[0][0]
                                try:
                                    self.connection_clicked.emit(a, b)
                                except Exception:
                                    pass
                                return
        except Exception:
            pass

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        try:
            if event.button() == Qt.LeftButton:
                pos = self.mapToScene(event.position().toPoint())
                items = self.scene().items(pos)
                for it in items:
                    try:
                        loc_id = getattr(it, 'location_id', None)
                        if loc_id:
                            try:
                                self.location_double_clicked.emit(loc_id)
                            except Exception:
                                pass
                            return
                    except Exception:
                        pass
        except Exception:
            pass

class MapItem(QGraphicsItem):
    """Custom graphics item for map elements."""
    def __init__(self, name: str, pos: Tuple[float, float], size: float = 50.0, 
                 color: QColor = QColor(100, 150, 255), parent=None):
        super().__init__(parent)
        self.name = name
        self.setPos(*pos)
        self.size = size
        self.color = color
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
    def boundingRect(self) -> QRectF:
        return QRectF(-self.size/2, -self.size/2, self.size, self.size)
    
    def paint(self, painter: QPainter, option, widget=None):
        # Draw circle
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(-self.size/2, -self.size/2, self.size, self.size)
        
        # Draw name
        painter.setPen(Qt.black)
        painter.drawText(0, 0, self.name)
        
    def hoverEnterEvent(self, event):
        self.setToolTip(self.name)
        super().hoverEnterEvent(event)

class MapRenderer:
    """Renders an interactive map with locations and connections."""
    def __init__(self, view: MapView):
        self.view = view
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        # Expose renderer from the view so view event handlers can access locations
        try:
            self.view._map_renderer = self
        except Exception:
            pass
        self.locations: Dict[str, MapItem] = {}
        self.graph = nx.Graph()
        
    def add_location(self, location_id: str, name: str, pos: Tuple[float, float] = None, **kwargs):
        """Add a location to the map."""
        if location_id in self.locations:
            return

        if pos is None:
            pos = (0.0, 0.0)
        item = MapItem(name, pos, **kwargs)
        # store the canonical id on the item for event callbacks
        item.location_id = location_id
        self.locations[location_id] = item
        self.graph.add_node(location_id, pos=pos, item=item)
        self.scene.addItem(item)
        
    def add_connection(self, loc1: str, loc2: str, **kwargs):
        """Add a connection between two locations."""
        if loc1 in self.locations and loc2 in self.locations:
            self.graph.add_edge(loc1, loc2, **kwargs)
            self._update_connections()
            
    def _update_connections(self):
        """Update the visual representation of connections."""
        # Clear existing connection lines
        for item in list(self.scene.items()):
            if isinstance(item, QGraphicsPathItem):
                self.scene.removeItem(item)
                
        # Draw new connections
        for u, v, data in self.graph.edges(data=True):
            item1 = self.locations.get(u)
            item2 = self.locations.get(v)
            if not item1 or not item2:
                continue

            path = QPainterPath()
            path.moveTo(item1.pos())
            path.lineTo(item2.pos())

            line = self.scene.addPath(path, QPen(Qt.gray, 2))
            line.setZValue(-1)  # Ensure lines are behind nodes
            
    def render(self, layout_algorithm='spring', **kwargs):
        """Render the map with the specified layout algorithm."""
        if not self.graph.nodes:
            return
            
        # Apply layout
        if layout_algorithm == 'spring':
            pos = nx.spring_layout(self.graph, **kwargs)
        elif layout_algorithm == 'circular':
            pos = nx.circular_layout(self.graph, **kwargs)
        else:  # default to spring
            pos = nx.spring_layout(self.graph, **kwargs)
            
        # Update node positions
        for node, (x, y) in pos.items():
            if node in self.locations:
                self.locations[node].setPos(x * 300, y * 300)  # Scale the positions
                
        self._update_connections()
        
    def clear(self):
        """Clear all locations and connections."""
        self.scene.clear()
        self.locations.clear()
        self.graph.clear()
