"""
Sequence diagram model for the Mermaid Render library.

This module provides an object-oriented interface for creating sequence diagrams
with support for participants, messages, activations, notes, and loops.
"""

from ..core import MermaidDiagram
from ..exceptions import DiagramError


class SequenceParticipant:
    """
    Represents a participant in a sequence diagram.

    A participant is an entity (actor, system, service, etc.) that can send and
    receive messages in a sequence diagram. Participants are displayed as vertical
    lifelines with the participant name at the top.

    Participants can represent:
    - Human actors (users, administrators)
    - Software systems (services, APIs, databases)
    - External systems (third-party services)
    - Internal components (modules, classes)

    Attributes:
        id (str): Unique identifier used in message definitions
        name (str): Display name shown in the diagram

    Example:
        >>> # Simple participant
        >>> user = SequenceParticipant("user", "User")
        >>>
        >>> # System participant
        >>> api = SequenceParticipant("api", "REST API")
        >>>
        >>> # Participant with same ID and name
        >>> db = SequenceParticipant("database")
    """

    def __init__(self, id: str, name: str | None = None) -> None:
        """
        Initialize a sequence participant.

        Args:
            id: Unique identifier for the participant. Used in message definitions
                and must be unique within the diagram. Should follow Mermaid naming
                conventions (alphanumeric, no spaces)
            name: Display name shown in the diagram. If not provided, the id will
                be used as the display name. Can contain spaces and special characters

        Example:
            >>> # Participant with custom display name
            >>> participant = SequenceParticipant("auth_svc", "Authentication Service")
            >>>
            >>> # Participant using ID as display name
            >>> user = SequenceParticipant("User")
        """
        self.id = id
        self.name = name or id

    def to_mermaid(self) -> str:
        """
        Generate Mermaid syntax for this participant.

        Returns:
            Mermaid syntax string for participant declaration

        Example:
            >>> participant = SequenceParticipant("user", "End User")
            >>> print(participant.to_mermaid())
            participant user as End User

            >>> simple = SequenceParticipant("API")
            >>> print(simple.to_mermaid())
            participant API
        """
        if self.name != self.id:
            return f"participant {self.id} as {self.name}"
        return f"participant {self.id}"


class SequenceMessage:
    """
    Represents a message between participants in a sequence diagram.

    A message represents communication between two participants in a sequence.
    Messages can be synchronous (blocking), asynchronous (non-blocking), or
    return messages. They can also trigger activation/deactivation of participants.

    Message types and their meanings:
    - sync (->): Synchronous call, sender waits for response
    - async (->>): Asynchronous call, sender doesn't wait
    - return (-->>): Return message from a previous call
    - sync_open (-): Open synchronous arrow (no arrowhead)
    - async_open (--): Open asynchronous arrow (no arrowhead)
    - activate (+): Activation message
    - deactivate (-): Deactivation message
    - destroy (-x): Destroy participant message

    Attributes:
        MESSAGE_TYPES (Dict[str, str]): Available message types with Mermaid syntax
        from_participant (str): Source participant identifier
        to_participant (str): Target participant identifier
        message (str): Message text/label
        message_type (str): Type of message
        activate (bool): Whether to activate target participant
        deactivate (bool): Whether to deactivate target participant

    Example:
        >>> # Simple synchronous message
        >>> msg = SequenceMessage("user", "api", "Login request")
        >>>
        >>> # Asynchronous message with activation
        >>> async_msg = SequenceMessage("api", "db", "Store data",
        ...                            message_type="async", activate=True)
        >>>
        >>> # Return message with deactivation
        >>> return_msg = SequenceMessage("db", "api", "Success",
        ...                             message_type="return", deactivate=True)
    """

    MESSAGE_TYPES = {
        "sync": "->",  # Synchronous message
        "async": "->>",  # Asynchronous message
        "return": "-->>",  # Return message
        "sync_open": "-)",  # Open synchronous message
        "async_open": "--)",  # Open asynchronous message
        "activate": "+",  # Activation message
        "deactivate": "-",  # Deactivation message
        "destroy": "-x",  # Destroy message
    }

    def __init__(
        self,
        from_participant: str,
        to_participant: str,
        message: str,
        message_type: str = "sync",
        activate: bool = False,
        deactivate: bool = False,
    ) -> None:
        """
        Initialize a sequence message.

        Args:
            from_participant: Source participant ID. Must match an existing participant
            to_participant: Target participant ID. Must match an existing participant
            message: Message text displayed on the arrow. Describes the communication
            message_type: Type of message arrow. Must be one of the keys in MESSAGE_TYPES
            activate: Whether to activate (highlight) the target participant after this message
            deactivate: Whether to deactivate the target participant after this message

        Raises:
            DiagramError: If the specified message_type is not supported

        Example:
            >>> # API call
            >>> call = SequenceMessage("client", "server", "GET /users", "sync")
            >>>
            >>> # Database query with activation
            >>> query = SequenceMessage("server", "db", "SELECT * FROM users",
            ...                        message_type="async", activate=True)
            >>>
            >>> # Response with deactivation
            >>> response = SequenceMessage("db", "server", "User data",
            ...                           message_type="return", deactivate=True)
        """
        self.from_participant = from_participant
        self.to_participant = to_participant
        self.message = message
        self.message_type = message_type
        self.activate = activate
        self.deactivate = deactivate

        if message_type not in self.MESSAGE_TYPES:
            raise DiagramError(f"Unknown message type: {message_type}")

    def to_mermaid(self) -> list[str]:
        """Generate Mermaid syntax for this message."""
        lines = []
        arrow = self.MESSAGE_TYPES[self.message_type]

        # Add activation if needed
        if self.activate:
            lines.append(f"activate {self.to_participant}")

        # Add the message
        lines.append(
            f"{self.from_participant}{arrow}{self.to_participant}: {self.message}"
        )

        # Add deactivation if needed
        if self.deactivate:
            lines.append(f"deactivate {self.to_participant}")

        return lines


class SequenceNote:
    """Represents a note in a sequence diagram."""

    POSITIONS = ["left of", "right of", "over"]

    def __init__(
        self,
        text: str,
        participant: str,
        position: str = "right of",
        participants: list[str] | None = None,
    ) -> None:
        """
        Initialize a sequence note.

        Args:
            text: Note text
            participant: Participant to attach note to
            position: Position relative to participant
            participants: For "over" position, list of participants to span
        """
        self.text = text
        self.participant = participant
        self.position = position
        self.participants = participants or []

        if position not in self.POSITIONS:
            raise DiagramError(f"Unknown note position: {position}")

    def to_mermaid(self) -> str:
        """Generate Mermaid syntax for this note."""
        if self.position == "over" and self.participants:
            participants_str = ",".join(self.participants)
            return f"note over {participants_str}: {self.text}"
        else:
            return f"note {self.position} {self.participant}: {self.text}"


class SequenceLoop:
    """Represents a loop block in a sequence diagram."""

    def __init__(self, condition: str) -> None:
        """
        Initialize a sequence loop.

        Args:
            condition: Loop condition text
        """
        self.condition = condition
        self.messages: list[SequenceMessage] = []
        self.notes: list[SequenceNote] = []

    def add_message(self, message: SequenceMessage) -> None:
        """Add a message to this loop."""
        self.messages.append(message)

    def add_note(self, note: SequenceNote) -> None:
        """Add a note to this loop."""
        self.notes.append(note)

    def to_mermaid(self) -> list[str]:
        """Generate Mermaid syntax for this loop."""
        lines = [f"loop {self.condition}"]

        # Add messages and notes
        for message in self.messages:
            for line in message.to_mermaid():
                lines.append(f"    {line}")

        for note in self.notes:
            lines.append(f"    {note.to_mermaid()}")

        lines.append("end")
        return lines


class SequenceDiagram(MermaidDiagram):
    """
    Sequence diagram model with support for participants, messages, notes, and control structures.

    Example:
        >>> seq = SequenceDiagram()
        >>> seq.add_participant("A", "Alice")
        >>> seq.add_participant("B", "Bob")
        >>> seq.add_message("A", "B", "Hello Bob!", "sync")
        >>> seq.add_message("B", "A", "Hi Alice!", "return")
        >>> print(seq.to_mermaid())
    """

    def __init__(self, title: str | None = None, autonumber: bool = False) -> None:
        """
        Initialize sequence diagram.

        Args:
            title: Optional diagram title
            autonumber: Whether to automatically number messages
        """
        super().__init__(title)
        self.autonumber = autonumber
        self.participants: dict[str, SequenceParticipant] = {}
        self.messages: list[SequenceMessage] = []
        self.notes: list[SequenceNote] = []
        self.loops: list[SequenceLoop] = []
        self.activations: dict[str, bool] = {}

    def get_diagram_type(self) -> str:
        """Return the Mermaid diagram type identifier."""
        return "sequenceDiagram"

    def add_participant(self, id: str, name: str | None = None) -> SequenceParticipant:
        """
        Add a participant to the sequence diagram.

        Args:
            id: Unique participant identifier
            name: Display name for the participant

        Returns:
            The created SequenceParticipant
        """
        if id in self.participants:
            raise DiagramError(f"Participant with ID '{id}' already exists")

        participant = SequenceParticipant(id, name)
        self.participants[id] = participant
        return participant

    def add_message(
        self,
        from_participant: str,
        to_participant: str,
        message: str,
        message_type: str = "sync",
        activate: bool = False,
        deactivate: bool = False,
    ) -> SequenceMessage:
        """
        Add a message between participants in the sequence diagram.

        Creates a message interaction between two participants, representing
        communication, method calls, or other interactions in a sequence.

        Args:
            from_participant (str): Source participant identifier. Must be an
                existing participant in the diagram.
            to_participant (str): Target participant identifier. Must be an
                existing participant in the diagram.
            message (str): Message text to display on the arrow. Should describe
                the interaction or method call being made.
            message_type (str, optional): Type of message arrow. Supported types:
                - "sync": Synchronous call with solid arrow (->>)
                - "async": Asynchronous call with open arrow (->)
                - "return": Return message with dashed arrow (-->>)
                - "callback": Callback with dotted arrow (-.)
                Defaults to "sync".
            activate (bool, optional): Whether to activate (highlight) the target
                participant after this message. Used to show when a participant
                becomes active in processing. Defaults to False.
            deactivate (bool, optional): Whether to deactivate the target
                participant after this message. Used to show when processing
                ends. Defaults to False.

        Returns:
            SequenceMessage: The created message object representing the
            interaction between participants.

        Raises:
            DiagramError: If either participant doesn't exist in the diagram.

        Examples:
            Basic message:
            >>> seq = SequenceDiagram()
            >>> seq.add_participant("client", "Client")
            >>> seq.add_participant("server", "Server")
            >>> seq.add_message("client", "server", "Login request")

            Different message types:
            >>> seq.add_message("client", "server", "getData()", "sync")
            >>> seq.add_message("server", "client", "data", "return")
            >>> seq.add_message("client", "server", "updateAsync()", "async")

            With activation:
            >>> seq.add_message("client", "server", "process()", activate=True)
            >>> seq.add_message("server", "client", "result", deactivate=True)

            Complete API interaction:
            >>> api_flow = SequenceDiagram(title="User Authentication")
            >>> api_flow.add_participant("user", "User")
            >>> api_flow.add_participant("app", "Mobile App")
            >>> api_flow.add_participant("auth", "Auth Service")
            >>> api_flow.add_participant("db", "Database")
            >>>
            >>> api_flow.add_message("user", "app", "Enter credentials")
            >>> api_flow.add_message("app", "auth", "authenticate(user, pass)", activate=True)
            >>> api_flow.add_message("auth", "db", "validateUser(user)")
            >>> api_flow.add_message("db", "auth", "user_data", "return")
            >>> api_flow.add_message("auth", "app", "auth_token", "return", deactivate=True)
            >>> api_flow.add_message("app", "user", "Login successful")
        """
        # Auto-create participants if they don't exist
        if from_participant not in self.participants:
            self.add_participant(from_participant)
        if to_participant not in self.participants:
            self.add_participant(to_participant)

        msg = SequenceMessage(
            from_participant,
            to_participant,
            message,
            message_type,
            activate,
            deactivate,
        )
        self.messages.append(msg)
        return msg

    def add_note(
        self,
        text: str,
        participant: str,
        position: str = "right of",
        participants: list[str] | None = None,
    ) -> SequenceNote:
        """
        Add a note to the sequence diagram.

        Args:
            text: Note text
            participant: Participant to attach note to
            position: Position relative to participant
            participants: For "over" position, list of participants

        Returns:
            The created SequenceNote
        """
        if participant not in self.participants and position != "over":
            raise DiagramError(f"Participant '{participant}' does not exist")

        note = SequenceNote(text, participant, position, participants)
        self.notes.append(note)
        return note

    def add_loop(self, condition: str) -> SequenceLoop:
        """
        Add a loop block to the sequence diagram.

        Args:
            condition: Loop condition text

        Returns:
            The created SequenceLoop
        """
        loop = SequenceLoop(condition)
        self.loops.append(loop)
        return loop

    def activate_participant(self, participant_id: str) -> None:
        """Activate a participant (show lifeline as active)."""
        if participant_id not in self.participants:
            raise DiagramError(f"Participant '{participant_id}' does not exist")
        self.activations[participant_id] = True

    def deactivate_participant(self, participant_id: str) -> None:
        """Deactivate a participant."""
        if participant_id not in self.participants:
            raise DiagramError(f"Participant '{participant_id}' does not exist")
        self.activations[participant_id] = False

    def _generate_mermaid(self) -> str:
        """Generate complete Mermaid syntax for the sequence diagram."""
        lines = ["sequenceDiagram"]

        # Add title if present
        if self.title:
            lines.append(f"    title: {self.title}")

        # Add autonumber if enabled
        if self.autonumber:
            lines.append("    autonumber")

        # Add participants
        for participant in self.participants.values():
            lines.append(f"    {participant.to_mermaid()}")

        # Add messages
        for message in self.messages:
            for line in message.to_mermaid():
                lines.append(f"    {line}")

        # Add notes
        for note in self.notes:
            lines.append(f"    {note.to_mermaid()}")

        # Add loops
        for loop in self.loops:
            for line in loop.to_mermaid():
                lines.append(f"    {line}")

        return "\n".join(lines)
