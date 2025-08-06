"""State diagram model for the Mermaid Render library."""

from typing import Dict, List, Optional

from ..core import MermaidDiagram


class StateDiagram(MermaidDiagram):
    """State diagram model with support for states and transitions."""

    def __init__(self, title: Optional[str] = None) -> None:
        super().__init__(title)
        self.states: Dict[str, str] = {}
        self.transitions: List[tuple] = []

    def get_diagram_type(self) -> str:
        return "stateDiagram-v2"

    def add_state(self, id: str, label: Optional[str] = None) -> None:
        """Add a state to the diagram."""
        self.states[id] = label or id

    def add_transition(
        self, from_state: str, to_state: str, label: Optional[str] = None
    ) -> None:
        """Add a transition between states."""
        self.transitions.append((from_state, to_state, label))

    def _generate_mermaid(self) -> str:
        """Generate Mermaid syntax for the state diagram."""
        lines = ["stateDiagram-v2"]

        if self.title:
            lines.append(f"    title: {self.title}")

        # Add states
        for state_id, label in self.states.items():
            if label != state_id:
                lines.append(f"    {state_id} : {label}")

        # Add transitions
        for from_state, to_state, label in self.transitions:
            if label:
                lines.append(f"    {from_state} --> {to_state} : {label}")
            else:
                lines.append(f"    {from_state} --> {to_state}")

        return "\n".join(lines)
