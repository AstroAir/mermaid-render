"""
Timeline diagram model for the Mermaid Render library.

This module provides an object-oriented interface for creating timeline diagrams
with support for time periods, events, sections, and styling.
"""

from typing import List, Optional

from ..core import MermaidDiagram


class TimelineEvent:
    """
    Represents an event in a timeline.

    An event is associated with a specific time period and contains
    descriptive text about what happened.
    """

    def __init__(self, text: str) -> None:
        """
        Initialize timeline event.

        Args:
            text: Event description text
        """
        self.text = text

    def to_mermaid(self) -> str:
        """Generate Mermaid syntax for this event."""
        # Handle line breaks and long text
        if len(self.text) > 50 or "\n" in self.text:
            # Use <br> for line breaks in long text
            formatted_text = self.text.replace("\n", "<br>")
            return f": {formatted_text}"
        return f": {self.text}"


class TimelinePeriod:
    """
    Represents a time period in a timeline.

    A time period can contain one or more events and represents
    a specific point or duration in time.
    """

    def __init__(self, period: str) -> None:
        """
        Initialize timeline period.

        Args:
            period: Time period identifier (e.g., "2021", "Q1 2022", "January")
        """
        self.period = period
        self.events: List[TimelineEvent] = []

    def add_event(self, text: str) -> TimelineEvent:
        """
        Add an event to this time period.

        Args:
            text: Event description text

        Returns:
            The created TimelineEvent
        """
        event = TimelineEvent(text)
        self.events.append(event)
        return event

    def to_mermaid(self) -> List[str]:
        """
        Generate Mermaid syntax for this time period.

        Returns:
            A list of lines for this period and its events.
        """
        lines = []

        if not self.events:
            # Time period with no events
            lines.append(f"{self.period} : ")
        elif len(self.events) == 1:
            # Single event on same line
            lines.append(f"{self.period} : {self.events[0].text}")
        else:
            # Multiple events - first on same line, rest on separate lines
            lines.append(f"{self.period} : {self.events[0].text}")
            for event in self.events[1:]:
                lines.append(f"          {event.to_mermaid()}")

        return lines


class TimelineSection:
    """
    Represents a section in a timeline.

    Sections group related time periods together and provide
    visual organization and color coding.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize timeline section.

        Args:
            name: Section name/title
        """
        self.name = name
        self.periods: List[TimelinePeriod] = []

    def add_period(self, period: str) -> TimelinePeriod:
        """
        Add a time period to this section.

        Args:
            period: Time period identifier

        Returns:
            The created TimelinePeriod
        """
        timeline_period = TimelinePeriod(period)
        self.periods.append(timeline_period)
        return timeline_period

    def to_mermaid(self) -> List[str]:
        """
        Generate Mermaid syntax for this section.

        Returns:
            Lines including the section header and contained periods.
        """
        lines = [f"section {self.name}"]

        for period in self.periods:
            lines.extend(period.to_mermaid())

        return lines


class TimelineDiagram(MermaidDiagram):
    """
    Timeline diagram model with support for time periods, events, and sections.

    Timeline diagrams are used to illustrate chronological sequences of events,
    dates, or periods of time. They can be organized into sections for better
    visual grouping.

    Example:
        >>> timeline = TimelineDiagram(title="Project Timeline")
        >>>
        >>> # Add a section
        >>> planning = timeline.add_section("Planning Phase")
        >>> q1 = planning.add_period("Q1 2024")
        >>> q1.add_event("Requirements gathering")
        >>> q1.add_event("Initial design")
        >>>
        >>> # Add periods without sections
        >>> timeline.add_period("Q2 2024").add_event("Development starts")
        >>>
        >>> print(timeline.to_mermaid())
    """

    def __init__(
        self, title: Optional[str] = None, disable_multicolor: bool = False
    ) -> None:
        """
        Initialize timeline diagram.

        Args:
            title: Optional diagram title
            disable_multicolor: Whether to disable multi-color styling
        """
        super().__init__(title)
        self.disable_multicolor = disable_multicolor
        self.sections: List[TimelineSection] = []
        self.periods: List[TimelinePeriod] = []  # Periods not in sections

    def get_diagram_type(self) -> str:
        """Return the Mermaid diagram type identifier."""
        return "timeline"

    def add_section(self, name: str) -> TimelineSection:
        """
        Add a section to group time periods.

        Args:
            name: Section name/title

        Returns:
            The created TimelineSection
        """
        self._check_disposed()
        section = TimelineSection(name)
        self.sections.append(section)
        self.clear_cache()
        return section

    def add_period(self, period: str) -> TimelinePeriod:
        """
        Add a time period directly to the timeline (not in a section).

        Args:
            period: Time period identifier

        Returns:
            The created TimelinePeriod
        """
        self._check_disposed()
        timeline_period = TimelinePeriod(period)
        self.periods.append(timeline_period)
        self.clear_cache()
        return timeline_period

    def add_event(self, period: str, event_text: str) -> TimelineEvent:
        """
        Convenience method to add an event to a specific period.

        If the period doesn't exist as a standalone period, it will be created.
        This method only looks for periods in the standalone periods list,
        not in sections, to avoid conflicts.

        Args:
            period: Time period identifier
            event_text: Event description text

        Returns:
            The created TimelineEvent
        """
        self._check_disposed()

        # Look for existing period in standalone periods only
        for timeline_period in self.periods:
            if timeline_period.period == period:
                event = timeline_period.add_event(event_text)
                self.clear_cache()
                return event

        # Create new standalone period if not found
        new_period = self.add_period(period)
        return new_period.add_event(event_text)

    def _generate_mermaid(self) -> str:
        """
        Generate complete Mermaid syntax for the timeline diagram.

        Returns:
            Mermaid timeline text including title, sections, and periods.
        """
        lines = ["timeline"]

        # Add title if present
        if self.title:
            lines.append(f"    title {self.title}")

        # Add sections
        for section in self.sections:
            section_lines = section.to_mermaid()
            for line in section_lines:
                lines.append(f"    {line}")

        # Add standalone periods (not in sections)
        for period in self.periods:
            period_lines = period.to_mermaid()
            for line in period_lines:
                lines.append(f"    {line}")

        return "\n".join(lines)
