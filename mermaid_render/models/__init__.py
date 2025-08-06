"""
Diagram model classes for the Mermaid Render library.

This package contains all the diagram model classes that provide
object-oriented interfaces for creating different types of Mermaid diagrams.

Available diagram types:
- FlowchartDiagram: Flowcharts and process diagrams
- SequenceDiagram: Sequence diagrams for interactions
- ClassDiagram: UML class diagrams
- StateDiagram: State machine diagrams
- ERDiagram: Entity-relationship diagrams
- UserJourneyDiagram: User journey mapping
- GanttDiagram: Project timeline diagrams
- PieChartDiagram: Pie charts for data visualization
- GitGraphDiagram: Git branching diagrams
- MindmapDiagram: Mind maps and hierarchical structures
- TimelineDiagram: Timeline diagrams for chronological events
"""

from .class_diagram import ClassDiagram
from .er_diagram import ERDiagram
from .flowchart import FlowchartDiagram
from .gantt import GanttDiagram
from .git_graph import GitGraphDiagram
from .mindmap import MindmapDiagram
from .pie_chart import PieChartDiagram
from .sequence import SequenceDiagram
from .state import StateDiagram
from .timeline import TimelineDiagram
from .user_journey import UserJourneyDiagram

__all__ = [
    "FlowchartDiagram",
    "SequenceDiagram",
    "ClassDiagram",
    "StateDiagram",
    "ERDiagram",
    "UserJourneyDiagram",
    "GanttDiagram",
    "PieChartDiagram",
    "GitGraphDiagram",
    "MindmapDiagram",
    "TimelineDiagram",
]
