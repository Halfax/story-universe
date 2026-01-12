# Story Universe - Visualization Components

This document provides an overview of the visualization components in the World Browser application, including the Timeline, Character Web, and Map View panels.

## Table of Contents
- [Overview](#overview)
- [Timeline Panel](#timeline-panel)
- [Character Web Panel](#character-web-panel)
- [Map View Panel](#map-view-panel)
- [Integration Guide](#integration-guide)
- [API Reference](#api-reference)
- [Customization](#customization)

## Overview

The World Browser provides three main visualization components:

1. **Timeline Panel**: For chronological visualization of events
2. **Character Web Panel**: For visualizing relationships between characters and entities
3. **Map View Panel**: For geographical visualization of locations and their connections

All components are built using PySide6 and support interactive features like zooming, panning, and selection.

## Timeline Panel

### Features
- Display events on a horizontal timeline
- Support for multiple tracks/categories
- Zoom and pan functionality
- Event selection and tooltips
- Customizable appearance

### Usage
```python
# Create and configure the timeline panel
timeline = TimelinePanel()

# Add a track
timeline.add_track("main", "Main Storyline", color="#3498db")

# Add an event
from datetime import datetime, timedelta
now = datetime.now()
timeline.add_event({
    'id': 'event1',
    'track': 'main',
    'start': now,
    'end': now + timedelta(days=3),
    'title': 'The Journey Begins',
    'description': 'The hero starts their adventure',
    'color': '#e74c3c'
})
```

## Character Web Panel

### Features
- Force-directed graph layout
- Node and edge interaction
- Filtering by node type
- Context menu for adding/removing elements
- Custom styling options

### Usage
```python
# Create and configure the character web
web = CharacterWebPanel()

# Add nodes (characters, factions, locations)
web.add_node("char1", "Aragorn", node_type="character", color="#2ecc71")
web.add_node("faction1", "The Fellowship", node_type="faction", color="#9b59b6")

# Add relationships
web.add_edge("char1", "faction1", "member_of", color="#f1c40f")

# Apply layout
web.arrange_graph()
```

## Map View Panel

### Features
- Interactive map with zoom/pan
- Location markers and connections
- Layer controls
- Multiple view modes (Map, Graph, Hybrid)
- Context menu for editing

### Usage
```python
# Create and configure the map view
map_view = MapViewPanel()

# Add locations
map_view.add_location("rivendell", "Rivendell", pos=QPointF(100, 200), color="#27ae60")
map_view.add_location("mordor", "Mordor", pos=QPointF(500, 400), color="#c0392b")

# Add connections
map_view.add_connection("rivendell", "mordor", "journey", color="#7f8c8d")

# Auto-arrange locations
map_view.arrange_map()
```

## Integration Guide

### Adding Panels to Main Window
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create panels
        self.timeline = TimelinePanel()
        self.character_web = CharacterWebPanel()
        self.map_view = MapViewPanel()
        
        # Add panels to tabs
        self.tabs.addTab(self.timeline, "Timeline")
        self.tabs.addTab(self.character_web, "Character Web")
        self.tabs.addTab(self.map_view, "World Map")
        
        # Set central widget
        self.setCentralWidget(self.tabs)
```

### Data Loading
```python
def load_story_data(self):
    # Example: Load timeline events
    events = get_events_from_database()
    for event in events:
        self.timeline.add_event(event)
    
    # Example: Load character relationships
    characters = get_characters_from_database()
    for char in characters:
        self.character_web.add_node(
            char['id'], 
            char['name'], 
            node_type=char.get('type', 'character'),
            **char.get('style', {})
        )
    
    # Example: Load map data
    locations = get_locations_from_database()
    for loc in locations:
        self.map_view.add_location(
            loc['id'],
            loc['name'],
            pos=QPointF(loc['x'], loc['y']),
            **loc.get('style', {})
        )
```

## API Reference

### Common Methods
- `refresh()`: Redraw the visualization
- `clear()`: Remove all elements
- `fit_to_view()`: Zoom to show all elements

### TimelinePanel
- `add_track(track_id, name, **style)`: Add a new track
- `add_event(event_data)`: Add an event to the timeline
- `set_time_range(start, end)`: Set visible time range

### CharacterWebPanel
- `add_node(node_id, name, node_type, **style)`: Add a node
- `add_edge(source_id, target_id, relationship, **style)`: Add an edge
- `apply_filter(node_type)`: Filter by node type
- `arrange_graph()`: Recalculate layout

### MapViewPanel
- `add_location(location_id, name, pos, **style)`: Add a location
- `add_connection(loc1_id, loc2_id, **style)`: Add a connection
- `set_view_mode(mode)`: Change view mode (map/graph/hybrid)
- `arrange_map()`: Auto-arrange locations

## Customization

### Styling
All components support styling through keyword arguments:

```python
# Example: Styling a node in the character web
web.add_node("gandalf", "Gandalf", 
    node_type="character",
    color="#f39c12",
    size=30,
    border_color="#d35400",
    border_width=2,
    font_size=12,
    shape="circle"  # or 'rectangle', 'diamond', etc.
)
```

### Custom Event Handlers
Connect to component signals for custom interactions:

```python
# Timeline event selection
timeline.event_selected.connect(self.on_timeline_event_selected)

# Character web node selection
character_web.node_selected.connect(self.on_character_selected)

# Map location click
map_view.location_clicked.connect(self.on_location_clicked)
```

### Extending Components
Create custom subclasses to extend functionality:

```python
class CustomTimeline(TimelinePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Custom initialization
        
    def add_custom_event(self, event_data):
        # Custom event handling
        self.add_event(event_data)
```

## Performance Considerations

- For large datasets, use batch operations when possible
- Enable/disable animations for better performance
- Use filtering to show only relevant data
- Consider using background threads for data loading

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   - Ensure all required packages are installed:
     ```
     pip install PySide6 networkx
     ```

2. **Performance Problems**
   - For large graphs, try reducing the number of visible elements
   - Disable animations if not needed
   - Use simpler node/edge styles

3. **Rendering Artifacts**
   - Try enabling/disabling OpenGL rendering
   - Check for updates to PySide6 and graphics drivers

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
