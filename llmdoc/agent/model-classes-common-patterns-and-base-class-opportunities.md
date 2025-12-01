# Model Classes Common Patterns and Base Class Opportunities

## Evidence

### Code Section: FlowchartNode Validation and Escaping

**File:** `diagramaid/models/flowchart.py`
**Lines:** 65-134
**Purpose:** Initialize node and generate Mermaid syntax with HTML escaping

```python
def __init__(
    self,
    id: str,
    label: str,
    shape: str = "rectangle",
    style: Optional[Dict[str, str]] = None,
) -> None:
    self.id = id
    self.label = label
    self.shape = shape
    self.style = style or {}

    if shape not in self.SHAPES:
        raise DiagramError(f"Unknown node shape: {shape}")

def to_mermaid(self) -> str:
    start, end = self.SHAPES[self.shape]
    # Escape HTML entities in label for proper Mermaid rendering
    escaped_label = (self.label
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace('"', "&quot;"))
    return f"{self.id}{start}{escaped_label}{end}"
```

**Key Details:**
- HTML entity escaping logic
- Shape validation in constructor
- to_mermaid() pattern

### Code Section: SequenceParticipant Mermaid Generation

**File:** `diagramaid/models/sequence.py`
**Lines:** 43-82
**Purpose:** Initialize participant and generate Mermaid syntax

```python
def __init__(self, id: str, name: Optional[str] = None) -> None:
    self.id = id
    self.name = name or id

def to_mermaid(self) -> str:
    if self.name != self.id:
        return f"participant {self.id} as {self.name}"
    return f"participant {self.id}"
```

**Key Details:**
- Simple id/name pattern
- No HTML escaping
- Conditional syntax generation

### Code Section: ClassMethod Mermaid Generation

**File:** `diagramaid/models/class_diagram.py`
**Lines:** 43-64
**Purpose:** Generate Mermaid syntax for class methods

```python
def to_mermaid(self) -> str:
    visibility_map = {
        "public": "+",
        "private": "-",
        "protected": "#",
        "package": "~",
    }
    vis_symbol = visibility_map.get(self.visibility, "+")

    params_str = ", ".join(self.parameters)
    method_str = f"{vis_symbol}{self.name}({params_str})"

    if self.return_type:
        method_str += f" {self.return_type}"

    if self.is_static:
        method_str += "$"
    if self.is_abstract:
        method_str += "*"

    return method_str
```

**Key Details:**
- Visibility mapping pattern
- String concatenation for modifiers
- No HTML escaping

### Code Section: ClassAttribute Mermaid Generation

**File:** `diagramaid/models/class_diagram.py`
**Lines:** 90-106
**Purpose:** Generate Mermaid syntax for class attributes

```python
def to_mermaid(self) -> str:
    visibility_map = {
        "public": "+",
        "private": "-",
        "protected": "#",
        "package": "~",
    }
    vis_symbol = visibility_map.get(self.visibility, "+")

    attr_str = f"{vis_symbol}{self.name}"
    if self.type:
        attr_str += f" {self.type}"
    if self.is_static:
        attr_str += "$"

    return attr_str
```

**Key Details:**
- Identical visibility_map to ClassMethod
- Similar modifier handling pattern
- Code duplication with ClassMethod

### Code Section: FlowchartDiagram Base Structure

**File:** `diagramaid/models/flowchart.py`
**Lines:** 347-383
**Purpose:** Initialize diagram with validation

```python
def __init__(
    self,
    direction: str = "TB",
    title: Optional[str] = None,
) -> None:
    super().__init__(title)

    if direction not in self.DIRECTIONS:
        raise DiagramError(f"Invalid direction: {direction}")

    self.direction = direction
    self.nodes: Dict[str, FlowchartNode] = {}
    self.edges: List[FlowchartEdge] = []
    self.subgraphs: Dict[str, FlowchartSubgraph] = {}
    self.styles: Dict[str, Dict[str, str]] = {}
```

**Key Details:**
- Direction validation pattern
- Collection initialization (nodes, edges)
- Inherits from MermaidDiagram

### Code Section: SequenceDiagram Base Structure

**File:** `diagramaid/models/sequence.py`
**Lines:** 291-305
**Purpose:** Initialize diagram with collections

```python
def __init__(self, title: Optional[str] = None, autonumber: bool = False) -> None:
    super().__init__(title)
    self.autonumber = autonumber
    self.participants: Dict[str, SequenceParticipant] = {}
    self.messages: List[SequenceMessage] = []
    self.notes: List[SequenceNote] = []
    self.loops: List[SequenceLoop] = []
    self.activations: Dict[str, bool] = {}
```

**Key Details:**
- Similar collection initialization pattern
- Additional feature flags (autonumber)
- Inherits from MermaidDiagram

### Code Section: ClassDiagram Base Structure

**File:** `diagramaid/models/class_diagram.py`
**Lines:** 253-257
**Purpose:** Initialize diagram with collections

```python
def __init__(self, title: Optional[str] = None) -> None:
    super().__init__(title)
    self.classes: Dict[str, ClassDefinition] = {}
    self.relationships: List[ClassRelationship] = []
```

**Key Details:**
- Simplest initialization pattern
- Two collections: classes and relationships
- Same inheritance pattern

### Code Section: FlowchartDiagram Element Addition

**File:** `diagramaid/models/flowchart.py`
**Lines:** 388-461
**Purpose:** Add node with validation

```python
def add_node(
    self,
    id: str,
    label: str,
    shape: str = "rectangle",
    style: Optional[Dict[str, str]] = None,
) -> FlowchartNode:
    if id in self.nodes:
        raise DiagramError(f"Node with ID '{id}' already exists")

    node = FlowchartNode(id, label, shape, style)
    self.nodes[id] = node
    return node
```

**Key Details:**
- Duplicate ID check pattern
- Create and store element
- Return created element

### Code Section: SequenceDiagram Element Addition

**File:** `diagramaid/models/sequence.py`
**Lines:** 311-329
**Purpose:** Add participant with validation

```python
def add_participant(
    self, id: str, name: Optional[str] = None
) -> SequenceParticipant:
    if id in self.participants:
        raise DiagramError(f"Participant with ID '{id}' already exists")

    participant = SequenceParticipant(id, name)
    self.participants[id] = participant
    return participant
```

**Key Details:**
- Identical duplicate check pattern
- Same create-store-return pattern
- Different error message but same logic

### Code Section: ClassDiagram Element Addition

**File:** `diagramaid/models/class_diagram.py`
**Lines:** 263-276
**Purpose:** Add class with validation

```python
def add_class(
    self,
    name: str,
    is_abstract: bool = False,
    is_interface: bool = False,
    stereotype: Optional[str] = None,
) -> ClassDefinition:
    if name in self.classes:
        raise DiagramError(f"Class '{name}' already exists")

    class_def = ClassDefinition(name, is_abstract, is_interface, stereotype)
    self.classes[name] = class_def
    return class_def
```

**Key Details:**
- Identical validation pattern
- Same three-step process
- Consistent error handling

### Code Section: FlowchartDiagram Relationship Validation

**File:** `diagramaid/models/flowchart.py`
**Lines:** 463-551
**Purpose:** Add edge with node existence validation

```python
def add_edge(
    self,
    from_node: str,
    to_node: str,
    label: Optional[str] = None,
    arrow_type: str = "arrow",
    style: Optional[Dict[str, str]] = None,
) -> FlowchartEdge:
    if from_node not in self.nodes:
        raise DiagramError(f"Source node '{from_node}' does not exist")
    if to_node not in self.nodes:
        raise DiagramError(f"Target node '{to_node}' does not exist")

    edge = FlowchartEdge(from_node, to_node, label, arrow_type, style=style)
    self.edges.append(edge)
    return edge
```

**Key Details:**
- Validates both endpoints exist
- Creates relationship object
- Appends to list (not dict)

### Code Section: ClassDiagram Relationship Validation

**File:** `diagramaid/models/class_diagram.py`
**Lines:** 278-302
**Purpose:** Add relationship with class existence validation

```python
def add_relationship(
    self,
    from_class: str,
    to_class: str,
    relationship_type: str,
    label: Optional[str] = None,
    from_cardinality: Optional[str] = None,
    to_cardinality: Optional[str] = None,
) -> ClassRelationship:
    if from_class not in self.classes:
        raise DiagramError(f"Class '{from_class}' does not exist")
    if to_class not in self.classes:
        raise DiagramError(f"Class '{to_class}' does not exist")

    relationship = ClassRelationship(
        from_class,
        to_class,
        relationship_type,
        label,
        from_cardinality,
        to_cardinality,
    )
    self.relationships.append(relationship)
    return relationship
```

**Key Details:**
- Identical validation pattern to FlowchartDiagram
- Same error message structure
- Same create-append-return pattern

## Findings

### 1. Duplicated Visibility Mapping

ClassMethod and ClassAttribute both define identical `visibility_map` dictionaries mapping visibility levels to UML symbols.

**Impact:**
- Code duplication (10 lines duplicated)
- Potential inconsistency if one is updated

**Recommendation:** Extract visibility mapping to a module-level constant or shared utility function within class_diagram.py.

### 2. Inconsistent HTML Escaping

FlowchartNode implements HTML entity escaping in its `to_mermaid()` method. SequenceParticipant, ClassMethod, and ClassAttribute don't escape HTML entities.

**Impact:**
- Inconsistent handling of special characters
- Potential rendering issues if labels contain HTML characters
- Security consideration if diagram content comes from untrusted sources

**Recommendation:** Add a shared utility function for HTML escaping in MermaidDiagram base class. All element classes should use it consistently.

### 3. Common Element Addition Pattern

All three diagram types (Flowchart, Sequence, Class) implement identical pattern for adding primary elements:
1. Check if ID/name already exists
2. Create element object
3. Store in dictionary
4. Return created element

**Impact:** ~15 lines of duplicated logic per diagram type.

**Recommendation:** Extract this pattern to a protected method in MermaidDiagram base class:

```python
def _add_element(self, collection: Dict, key: str, element: Any,
                 element_type: str) -> Any:
    if key in collection:
        raise DiagramError(f"{element_type} with ID '{key}' already exists")
    collection[key] = element
    return element
```

### 4. Common Relationship Validation Pattern

FlowchartDiagram and ClassDiagram both validate that referenced elements exist before creating relationships. The validation logic is identical.

**Impact:**
- Duplicated validation code (~6 lines per diagram type)
- Same error message patterns

**Recommendation:** Extract relationship validation to base class method:

```python
def _validate_relationship_endpoints(self, from_id: str, to_id: str,
                                    collection: Dict, element_type: str) -> None:
    if from_id not in collection:
        raise DiagramError(f"Source {element_type} '{from_id}' does not exist")
    if to_id not in collection:
        raise DiagramError(f"Target {element_type} '{to_id}' does not exist")
```

### 5. Common Collection Initialization Pattern

All diagram classes initialize similar collections:
- Primary elements dictionary (nodes/participants/classes)
- Relationships list (edges/messages/relationships)
- Optional collections (subgraphs, notes, loops)

**Impact:** While not strictly duplication, this represents a common pattern that could benefit from standardization.

**Recommendation:** Document this pattern in base class docstrings or provide base class helper methods for collection management.

### 6. Common Mermaid Generation Pattern

All diagram classes implement `_generate_mermaid()` with similar structure:
1. Start with diagram type declaration
2. Add title if present
3. Add primary elements
4. Add relationships
5. Join lines with newline

**Impact:** Pattern is repeated but structure varies enough that full abstraction may not be beneficial.

**Recommendation:** Document the pattern in MermaidDiagram base class and provide helper methods for common operations (e.g., `_format_title()`, `_indent_lines()`).

### 7. No Shared Element Base Class

FlowchartNode, SequenceParticipant, ClassMethod, ClassAttribute, etc. all implement `to_mermaid()` method but share no common base class.

**Impact:**
- No type polymorphism for elements
- Can't write generic code that works with any element
- No enforcement of to_mermaid() interface

**Recommendation:** Create an abstract base class for diagram elements:

```python
class DiagramElement(ABC):
    @abstractmethod
    def to_mermaid(self) -> Union[str, List[str]]:
        pass

    def _escape_label(self, label: str) -> str:
        # Shared HTML escaping logic
        pass
```

### 8. Validation Logic Not in Base Class

FlowchartDiagram implements `validate_diagram()` method that checks nodes exist and edges reference valid nodes. Other diagram types don't have similar validation.

**Impact:**
- Inconsistent validation across diagram types
- SequenceDiagram and ClassDiagram may accept invalid structures

**Recommendation:** Add abstract `validate_diagram()` method to MermaidDiagram base class. Each subclass should implement appropriate validation for their structure.
