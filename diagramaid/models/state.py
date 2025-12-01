"""State diagram model for the Mermaid Render library."""

from ..core import MermaidDiagram


class StateDiagram(MermaidDiagram):
    """State diagram model with support for states and transitions.

    Stores named states and directional transitions, and renders Mermaid stateDiagram-v2.
    """

    def __init__(self, title: str | None = None) -> None:
        """Initialize an empty state diagram.

        Args:
            title: Optional diagram title.
        """
        super().__init__(title)
        self.states: dict[str, str] = {}
        self.transitions: list[tuple[str, str, str | None]] = []

    def get_diagram_type(self) -> str:
        """Return the Mermaid diagram type identifier."""
        return "stateDiagram-v2"

    def add_state(self, id: str, label: str | None = None) -> None:
        """Add a state to the diagram.

        Args:
            id: Unique state identifier used in transitions.
            label: Optional display label (defaults to id if not provided).
        """
        self.states[id] = label or id

    def add_transition(
        self, from_state: str, to_state: str, label: str | None = None
    ) -> None:
        """Add a transition between states.

        Args:
            from_state: Source state identifier.
            to_state: Destination state identifier.
            label: Optional transition label.
        """
        self.transitions.append((from_state, to_state, label))

    def _generate_mermaid(self) -> str:
        """Generate Mermaid syntax for the state diagram.

        Returns:
            Mermaid stateDiagram-v2 text including states and transitions.
        """
        lines = ["stateDiagram-v2"]

        if self.title:
            lines.append(f"    title: {self.title}")

        # Add states (only emit mapping if label differs from id)
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
