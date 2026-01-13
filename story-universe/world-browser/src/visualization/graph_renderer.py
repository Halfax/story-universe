from typing import Dict, List, Optional, Tuple, Any
import math
import networkx as nx
from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem, 
                              QGraphicsTextItem, QMenu, QGraphicsSceneMouseEvent)
from PySide6.QtCore import Qt, QPointF, Signal, QRectF, QLineF, QTimer, Property
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QFont, QPainterPath, 
                          QLinearGradient, QRadialGradient, QPainterPathStroker)

class GraphNode(QGraphicsItem):
    """Custom graphics item for character nodes in the relationship graph."""
    def __init__(self, node_id: str, name: str, node_type: str = "character", 
                 size: float = 50.0, color: QColor = None):
        super().__init__()
        self.node_id = node_id
        self.name = name
        self.node_type = node_type
        self.size = size
        self._color = color or self._get_default_color()
        self._highlighted = False
        self._highlight_color = QColor(255, 215, 0)  # Gold
        
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        # Add text label
        self.label = QGraphicsTextItem(self)
        self.label.setPlainText(name)
        self.label.setDefaultTextColor(Qt.black)
        self.label.setTextWidth(100)
        self._update_label_position()
        
    def _get_default_color(self) -> QColor:
        """Get a color based on node type."""
        colors = {
            "character": QColor(100, 150, 255),  # Blue
            "faction": QColor(255, 150, 100),    # Orange
            "location": QColor(100, 255, 150),   # Green
            "item": QColor(200, 150, 255),       # Purple
        }
        return colors.get(self.node_type.lower(), QColor(200, 200, 200))  # Default gray
        
    def boundingRect(self) -> QRectF:
        padding = 5  # Extra space for highlight
        return QRectF(
            -self.size/2 - padding, 
            -self.size/2 - padding, 
            self.size + 2*padding, 
            self.size + 2*padding + 20  # Extra space for label
        )
        
    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addEllipse(-self.size/2, -self.size/2, self.size, self.size)
        return path
        
    def paint(self, painter: QPainter, option, widget=None):
        # Draw shadow
        shadow_offset = 3.0
        shadow_rect = QRectF(
            -self.size/2 + shadow_offset, 
            -self.size/2 + shadow_offset, 
            self.size, 
            self.size
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 80))
        painter.drawEllipse(shadow_rect)
        
        # Draw main circle
        rect = QRectF(-self.size/2, -self.size/2, self.size, self.size)
        
        # Create gradient
        gradient = QRadialGradient(0, 0, self.size/2)
        gradient.setColorAt(0, self._color.lighter(150))
        gradient.setColorAt(1, self._color.darker(120))
        
        # Draw highlight if selected or hovered
        if self.isSelected() or self._highlighted:
            highlight_pen = QPen(self._highlight_color, 3)
            highlight_pen.setCosmetic(True)
            painter.setPen(highlight_pen)
        else:
            painter.setPen(QPen(Qt.black, 1.5))
            
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(rect)
        
    def _update_label_position(self):
        """Position the label below the node."""
        text_rect = self.label.boundingRect()
        self.label.setPos(-text_rect.width()/2, self.size/2 + 5)
        
    def setHighlighted(self, highlighted: bool):
        """Set highlight state of the node."""
        if self._highlighted != highlighted:
            self._highlighted = highlighted
            self.update()
            
    def hoverEnterEvent(self, event):
        self.setZValue(10)  # Bring to front
        self.setScale(1.1)  # Slightly enlarge on hover
        self.setToolTip(f"{self.name} ({self.node_type})")
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self.setZValue(0)  # Reset z-index
        self.setScale(1.0)  # Reset size
        super().hoverLeaveEvent(event)
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            # Notify scene that nodes have moved
            self.scene().update()
        return super().itemChange(change, value)

class GraphEdge(QGraphicsItem):
    """Edge connecting two nodes in the relationship graph."""
    def __init__(self, source: GraphNode, target: GraphNode, 
                 relationship: str = "", weight: float = 1.0):
        super().__init__()
        self.source = source
        self.target = target
        self.relationship = relationship
        self.weight = weight
        self._color = QColor(150, 150, 150)
        
        # Make sure edges are drawn behind nodes
        self.setZValue(-1)
        
        # Update position when nodes move
        self.source.addToGroup(self)
        self.target.addToGroup(self)
        
        # Label for relationship type
        self.label = QGraphicsTextItem(self)
        self.label.setPlainText(relationship)
        self.label.setDefaultTextColor(Qt.darkGray)
        self.label.setZValue(1)  # Above the edge
        
        self.update_position()
        
    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle of the edge."""
        if not self.source or not self.target:
            return QRectF()
            
        # Include some padding for the line width and arrow
        padding = 10
        rect = QRectF(self.source.pos(), self.target.pos()).normalized()
        rect.adjust(-padding, -padding, padding, padding)
        return rect
        
    def shape(self) -> QPainterPath:
        """Return the shape of the edge for collision detection."""
        if not self.source or not self.target:
            return QPainterPath()
            
        path = QPainterPath()
        path.moveTo(self.source.pos())
        path.lineTo(self.target.pos())
        
        # Create a wider path for easier selection
        stroker = QPainterPathStroker()
        stroker.setWidth(10)
        return stroker.createStroke(path)
        
    def paint(self, painter: QPainter, option, widget=None):
        if not self.source or not self.target:
            return
            
        # Calculate line between centers
        line = QLineF(self.source.pos(), self.target.pos())
        if line.length() == 0:
            return
            
        # Draw the line
        pen = QPen(QBrush(self._color), 2 + self.weight, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        
        # Dashed line for negative relationships
        if self.relationship.lower() in ['enemy', 'rival', 'hate']:
            pen.setStyle(Qt.DashLine)
            pen.setColor(QColor(200, 50, 50))  # Reddish for negative
        
        painter.setPen(pen)
        painter.drawLine(line)
        
        # Draw arrow head
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = 2 * math.pi - angle
            
        arrow_size = 10 + self.weight * 2
        arrow_p1 = line.p2() - QPointF(
            math.cos(angle - math.pi / 3) * arrow_size,
            math.sin(angle - math.pi / 3) * arrow_size
        )
        arrow_p2 = line.p2() - QPointF(
            math.cos(angle - math.pi + math.pi / 3) * arrow_size,
            math.sin(angle - math.pi + math.pi / 3) * arrow_size
        )
        
        painter.setBrush(QBrush(pen.color()))
        painter.drawPolygon([line.p2(), arrow_p1, arrow_p2])
        
    def update_position(self):
        """Update edge position when nodes move."""
        if not self.source or not self.target:
            return
            
        # Update line position
        self.prepareGeometryChange()
        
        # Position label in the middle of the edge
        if self.relationship:
            center = (self.source.pos() + self.target.pos()) / 2
            text_rect = self.label.boundingRect()
            self.label.setPos(center - QPointF(text_rect.width()/2, text_rect.height()/2))
            
        self.update()

class RelationshipGraph(QGraphicsView):
    """Interactive view for displaying and editing relationship graphs."""
    # Signals for external panels
    node_clicked = Signal(str)
    node_double_clicked = Signal(str)
    edge_clicked = Signal(str, str)

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
        
        # Graph data
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[Tuple[str, str], GraphEdge] = {}
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)  # ~30 FPS
        
        # Physics simulation parameters
        self.cooling_factor = 0.95
        self.temperature = 10.0
        self.min_temperature = 0.1
        self.ideal_edge_length = 150
        self.repulsion = 1000.0
        self.attraction = 0.1
        
    def add_node(self, node_id: str, name: str, node_type: str = "character", 
                pos: QPointF = None, **kwargs):
        """Add a node to the graph."""
        if node_id in self.nodes:
            return self.nodes[node_id]
            
        # Create and position the node
        if pos is None:
            # Position in a circle around the center
            angle = len(self.nodes) * (2 * 3.14159 / 10)  # 10 nodes per circle
            radius = 100 * (1 + len(self.nodes) // 10)  # Increase radius as needed
            pos = QPointF(
                radius * math.cos(angle),
                radius * math.sin(angle)
            )
            
        node = GraphNode(node_id, name, node_type, **kwargs)
        node.setPos(pos)
        
        # Add to scene and data structures
        self.scene.addItem(node)
        self.nodes[node_id] = node
        self.graph.add_node(node_id, item=node, pos=pos, **kwargs)
        
        return node
        
    def add_edge(self, source_id: str, target_id: str, relationship: str = "", 
                weight: float = 1.0, **kwargs):
        """Add a directed edge between two nodes."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None
            
        edge_key = (source_id, target_id)
        if edge_key in self.edges:
            return self.edges[edge_key]
            
        source = self.nodes[source_id]
        target = self.nodes[target_id]
        
        # Create and add the edge
        edge = GraphEdge(source, target, relationship, weight, **kwargs)
        self.scene.addItem(edge)
        self.edges[edge_key] = edge
        self.graph.add_edge(source_id, target_id, item=edge, relationship=relationship, 
                          weight=weight, **kwargs)
        
        return edge
        
    def remove_node(self, node_id: str):
        """Remove a node and all its edges."""
        if node_id not in self.nodes:
            return
            
        # Remove connected edges first
        for source, target in list(self.graph.edges()):
            if source == node_id or target == node_id:
                self.remove_edge(source, target)
                
        # Remove the node
        node = self.nodes.pop(node_id)
        self.scene.removeItem(node)
        self.graph.remove_node(node_id)
        
    def remove_edge(self, source_id: str, target_id: str):
        """Remove an edge between two nodes."""
        edge_key = (source_id, target_id)
        if edge_key not in self.edges:
            return
            
        edge = self.edges.pop(edge_key)
        self.scene.removeItem(edge)
        self.graph.remove_edge(source_id, target_id)
        
    def clear(self):
        """Clear the entire graph."""
        self.scene.clear()
        self.nodes.clear()
        self.edges.clear()
        self.graph.clear()
        
    def wheelEvent(self, event):
        """Handle zooming with the mouse wheel."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        # Save the scene position
        old_pos = self.mapToScene(event.position().toPoint())
        
        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
            
        self.scale(zoom_factor, zoom_factor)
        
        # Center the view on the old position
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
        
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release events and emit click signals."""
        if event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)

        # On left click, detect the topmost item under cursor and emit signals
        try:
            if event.button() == Qt.LeftButton:
                pos = self.mapToScene(event.position().toPoint())
                items = self.scene.items(pos)
                for it in items:
                    if isinstance(it, GraphNode):
                        try:
                            self.node_clicked.emit(it.node_id)
                        except Exception:
                            pass
                        return
                    if isinstance(it, GraphEdge):
                        try:
                            self.edge_clicked.emit(it.source.node_id, it.target.node_id)
                        except Exception:
                            pass
                        return
        except Exception:
            pass

    def mouseDoubleClickEvent(self, event):
        """Handle double-click events and emit node double-click signal."""
        super().mouseDoubleClickEvent(event)
        try:
            if event.button() == Qt.LeftButton:
                pos = self.mapToScene(event.position().toPoint())
                items = self.scene.items(pos)
                for it in items:
                    if isinstance(it, GraphNode):
                        try:
                            self.node_double_clicked.emit(it.node_id)
                        except Exception:
                            pass
                        return
        except Exception:
            pass
        
    def animate(self):
        """Update the graph layout using a force-directed algorithm."""
        if len(self.nodes) < 2:
            return
            
        # Cool down the system
        self.temperature = max(self.min_temperature, self.temperature * self.cooling_factor)
        
        # Calculate repulsion between all nodes
        for node1 in self.nodes.values():
            node1.force = QPointF(0, 0)
            
            for node2 in self.nodes.values():
                if node1 == node2:
                    continue
                    
                # Calculate repulsion
                delta = node1.pos() - node2.pos()
                distance = max(1.0, math.hypot(delta.x(), delta.y()))
                
                # Coulomb's law: F = k * q1*q2 / r^2
                force = self.repulsion / (distance * distance)
                
                # Update forces
                if distance > 0:
                    node1.force += (delta / distance) * force
        
        # Calculate attraction along edges
        for source_id, target_id, data in self.graph.edges(data=True):
            source = self.nodes[source_id]
            target = self.nodes[target_id]
            
            # Calculate attraction
            delta = target.pos() - source.pos()
            distance = max(1.0, math.hypot(delta.x(), delta.y()))
            
            # Hooke's law: F = -kx
            force = self.attraction * (distance - self.ideal_edge_length)
            
            # Update forces
            if distance > 0:
                source.force += (delta / distance) * force
                target.force -= (delta / distance) * force
        
        # Update node positions
        for node in self.nodes.values():
            # Limit force by temperature
            force_magnitude = math.hypot(node.force.x(), node.force.y())
            if force_magnitude > 0:
                node.force = (node.force / force_magnitude) * min(force_magnitude, self.temperature)
                
                # Apply the force
                node.setPos(node.pos() + node.force * 0.1)  # Dampening factor
                
        # Update edge positions
        for edge in self.edges.values():
            edge.update_position()

class GraphRenderer:
    """High-level interface for rendering relationship graphs."""
    def __init__(self, view: RelationshipGraph = None):
        self.view = view or RelationshipGraph()
        self.graph = self.view.graph
        
    def render(self, graph_data: dict):
        """Render a graph from data.
        
        Args:
            graph_data: Dictionary containing 'nodes' and 'edges' lists.
                Example:
                {
                    'nodes': [
                        {'id': '1', 'name': 'Alice', 'type': 'character'},
                        {'id': '2', 'name': 'Bob', 'type': 'character'},
                    ],
                    'edges': [
                        {'source': '1', 'target': '2', 'relationship': 'friend', 'weight': 0.8},
                    ]
                }
        """
        self.view.clear()
        
        # Add nodes
        for node_data in graph_data.get('nodes', []):
            self.view.add_node(
                node_data['id'],
                node_data.get('name', 'Unnamed'),
                node_data.get('type', 'character'),
                **{k: v for k, v in node_data.items() if k not in ['id', 'name', 'type']}
            )
            
        # Add edges
        for edge_data in graph_data.get('edges', []):
            self.view.add_edge(
                edge_data['source'],
                edge_data['target'],
                edge_data.get('relationship', ''),
                edge_data.get('weight', 1.0),
                **{k: v for k, v in edge_data.items() if k not in ['source', 'target', 'relationship', 'weight']}
            )
            
        # Start with a nice layout
        self.view.temperature = 20.0  # Reset temperature for animation
        
    def get_view(self) -> RelationshipGraph:
        """Get the underlying QGraphicsView widget."""
        return self.view
