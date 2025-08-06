#!/usr/bin/env python3
"""
Interactive and collaboration showcase for Mermaid Render.

This script demonstrates interactive diagram building, collaborative editing,
and version control features.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from mermaid_render import (
    MermaidRenderer,
    FlowchartDiagram,
    SequenceDiagram,
)

# Interactive and collaboration features (optional imports with fallbacks)
INTERACTIVE_AVAILABLE = False
COLLABORATION_AVAILABLE = False

# --- Shims and type-safe fallbacks to avoid "possibly unbound" and unknown attributes ---

class _InteractiveSession:
    def __init__(self, session_id: str, diagram_type: str, title: str):
        self.session_id = session_id
        self.diagram_type = diagram_type
        self.title = title
        self.created_at = datetime.now()
        self.last_modified = self.created_at

class _ApplyResult:
    def __init__(self, success: bool, error: Optional[str] = None):
        self.success = success
        self.error = error

class _CollabChangeResult:
    def __init__(self, success: bool, conflict_reason: Optional[str] = None):
        self.success = success
        self.conflict_reason = conflict_reason

class _HistoryItem:
    def __init__(self, timestamp: datetime, user: str, action: str, description: str):
        self.timestamp = timestamp
        self.user = user
        self.action = action
        self.description = description

class _Commit:
    def __init__(self, commit_id: str, message: str, author: str, timestamp: datetime, parent_id: Optional[str]):
        self.commit_id = commit_id
        self.message = message
        self.author = author
        self.timestamp = timestamp
        self.parent_id = parent_id

# Defaults (will be overwritten if real modules are available)
class DiagramBuilder:
    def __init__(self):
        self._diagrams: Dict[str, FlowchartDiagram] = {}

    def apply_action(self, session_id: str, action: str, params: Dict[str, Any]) -> _ApplyResult:
        dg = self._diagrams.setdefault(session_id, FlowchartDiagram(title="Interactive Diagram"))
        try:
            if action == "add_node":
                dg.add_node(params["id"], params["label"], shape=params.get("shape", "rectangle"))
            elif action == "add_edge":
                dg.add_edge(params["from"], params["to"], label=params.get("label"))
            else:
                return _ApplyResult(False, f"Unknown action: {action}")
            return _ApplyResult(True)
        except Exception as e:
            return _ApplyResult(False, str(e))

    def get_diagram(self, session_id: str) -> Optional[FlowchartDiagram]:
        return self._diagrams.get(session_id)

def create_interactive_session(diagram_type: str, title: str) -> _InteractiveSession:
    # Simple ID generation
    sid = f"interactive-{int(time.time()*1000)}"
    return _InteractiveSession(sid, diagram_type, title)

class CollaborationManager:
    def __init__(self):
        self._histories: Dict[str, List[_HistoryItem]] = {}

    def apply_change(self, session_id: str, user: str, action: str, params: Dict[str, Any]) -> _CollabChangeResult:
        # For demo: accept all changes
        hist = self._histories.setdefault(session_id, [])
        hist.append(_HistoryItem(datetime.now(), user, action, f"{user} performed {action}"))
        return _CollabChangeResult(True)

    def get_change_history(self, session_id: str) -> List[_HistoryItem]:
        return self._histories.get(session_id, [])

class VersionControl:
    def __init__(self, repository_path: Path):
        self.repository_path = Path(repository_path)
        self._commits: List[_Commit] = []
        self._branches: Dict[str, str] = {}  # branch -> commit_id
        self._current_branch: str = "main"

    def init_repository(self) -> None:
        self.repository_path.mkdir(parents=True, exist_ok=True)
        # Initialize main branch without commit
        self._branches[self._current_branch] = ""

    def _next_commit_id(self) -> str:
        return f"{len(self._commits)+1:08d}"

    def get_commit_history(self) -> List[_Commit]:
        return list(self._commits)

    def create_branch(self, name: str, from_commit: Optional[str] = None) -> None:
        base = from_commit or (self._branches.get(self._current_branch) or "")
        self._branches[name] = base

    def checkout_branch(self, name: str) -> None:
        if name not in self._branches:
            # Auto-create from current head if missing
            self.create_branch(name, self._branches.get(self._current_branch))
        self._current_branch = name

    def list_branches(self) -> List[str]:
        return list(self._branches.keys())

    def get_current_branch(self) -> str:
        return self._current_branch

def commit_diagram_changes(vc: VersionControl, diagram: FlowchartDiagram, message: str, author: str) -> _Commit:
    commit_id = vc._next_commit_id()
    parent = vc._branches.get(vc._current_branch, "") or None
    commit = _Commit(commit_id=commit_id, message=message, author=author, timestamp=datetime.now(), parent_id=parent)
    vc._commits.append(commit)
    vc._branches[vc._current_branch] = commit_id
    # Persist a simple snapshot
    snap_path = vc.repository_path / f"{commit_id}.mmd"
    snap_path.write_text(diagram.to_mermaid())
    meta_path = vc.repository_path / f"{commit_id}.json"
    meta_path.write_text(json.dumps({"message": message, "author": author, "timestamp": commit.timestamp.isoformat(), "parent": parent}, indent=2))
    return commit

# Try to load real modules; if available, override the shims above
try:
    from mermaid_render.interactive import (  # type: ignore
        DiagramBuilder as _DiagramBuilder,
        InteractiveServer as _InteractiveServer,  # noqa: F401 (intentionally unused in this script)
        create_interactive_session as _create_interactive_session,
        start_server as _start_server,  # noqa: F401 (intentionally unused)
    )
    DiagramBuilder = _DiagramBuilder
    create_interactive_session = _create_interactive_session
    INTERACTIVE_AVAILABLE = True
except ImportError:
    print("⚠️  Interactive features not available. Install with: pip install mermaid-render[interactive]")

try:
    from mermaid_render.collaboration import (  # type: ignore
        CollaborationManager as _CollaborationManager,
        VersionControl as _VersionControl,
        create_collaborative_session as _create_collaborative_session,
        commit_diagram_changes as _commit_diagram_changes,
    )
    CollaborationManager = _CollaborationManager
    VersionControl = _VersionControl
    create_collaborative_session = _create_collaborative_session
    commit_diagram_changes = _commit_diagram_changes
    COLLABORATION_AVAILABLE = True
except ImportError:
    print("⚠️  Collaboration features not available. Install with: pip install mermaid-render[collaboration]")

def create_output_dir():
    """Create output directory for examples."""
    output_dir = Path("output/interactive")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def interactive_builder_example(output_dir: Path):
    """Demonstrate interactive diagram building."""
    # Even if real interactive not available, our shims will run
    print("Interactive diagram builder example...")
    
    try:
        # Create interactive builder
        builder = DiagramBuilder()
        
        # Start with a basic flowchart
        session = create_interactive_session(
            diagram_type="flowchart",
            title="Interactive Process Flow"
        )
        
        print(f"✅ Created interactive session: {getattr(session, 'session_id', 'unknown')}")
        
        # Simulate interactive building steps
        steps = [
            {"action": "add_node", "params": {"id": "start", "label": "Start Process", "shape": "circle"}},
            {"action": "add_node", "params": {"id": "input", "label": "Get Input", "shape": "rectangle"}},
            {"action": "add_node", "params": {"id": "validate", "label": "Validate?", "shape": "rhombus"}},
            {"action": "add_node", "params": {"id": "process", "label": "Process Data", "shape": "rectangle"}},
            {"action": "add_node", "params": {"id": "error", "label": "Show Error", "shape": "rectangle"}},
            {"action": "add_node", "params": {"id": "end", "label": "End", "shape": "circle"}},
            {"action": "add_edge", "params": {"from": "start", "to": "input"}},
            {"action": "add_edge", "params": {"from": "input", "to": "validate"}},
            {"action": "add_edge", "params": {"from": "validate", "to": "process", "label": "Valid"}},
            {"action": "add_edge", "params": {"from": "validate", "to": "error", "label": "Invalid"}},
            {"action": "add_edge", "params": {"from": "process", "to": "end"}},
            {"action": "add_edge", "params": {"from": "error", "to": "end"}},
        ]
        
        print("Building diagram interactively...")
        for i, step in enumerate(steps):
            print(f"  Step {i+1}: {step['action']} - {step['params']}")
            
            # Apply the step to the builder
            result = builder.apply_action(
                session.session_id,
                step['action'],
                step['params']
            )
            
            if getattr(result, "success", False):
                print(f"    ✅ Applied successfully")
            else:
                print(f"    ❌ Failed: {getattr(result, 'error', 'Unknown error')}")
        
        # Get the final diagram
        final_diagram = builder.get_diagram(session.session_id)
        
        # Save the interactive session
        session_data = {
            "session_id": getattr(session, "session_id", ""),
            "diagram_type": getattr(session, "diagram_type", "flowchart"),
            "title": getattr(session, "title", ""),
            "steps": steps,
            "final_diagram": final_diagram.to_mermaid() if final_diagram else None,
            "created_at": getattr(session, "created_at", datetime.now()).isoformat(),
            "last_modified": getattr(session, "last_modified", datetime.now()).isoformat()
        }
        
        session_path = output_dir / "interactive_session.json"
        with open(session_path, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"📁 Interactive session saved to {session_path}")
        
        # Render the final diagram
        if final_diagram:
            renderer = MermaidRenderer()
            diagram_path = output_dir / "interactive_diagram.svg"
            renderer.save(final_diagram, diagram_path)
            print(f"📁 Final diagram saved to {diagram_path}")
        
    except Exception as e:
        print(f"❌ Error in interactive builder: {e}")


def collaborative_editing_example(output_dir: Path):
    """Demonstrate collaborative editing features."""
    print("Collaborative editing example...")
    
    try:
        # Create collaboration manager
        collab_manager = CollaborationManager()
        
        # Create a collaborative session
        if COLLABORATION_AVAILABLE:
            # Real API
            session = create_collaborative_session(
                diagram_type="flowchart",
                title="Team Architecture Diagram",
                participants=["alice@example.com", "bob@example.com", "charlie@example.com"]
            )
        else:
            # Fallback simple session object
            class _CollabSession:
                def __init__(self):
                    self.session_id = f"collab-{int(time.time()*1000)}"
                    self.project_name = "Team Architecture Diagram"
                    self.participants = ["alice@example.com", "bob@example.com", "charlie@example.com"]
                    self.created_at = datetime.now()
            session = _CollabSession()
        
        print(f"✅ Created collaborative session: {session.session_id}")
        participants = getattr(session, "participants", [])
        if participants:
            print(f"   Participants: {', '.join(participants)}")
        
        # Simulate collaborative editing
        alice_changes = [
            {"user": "alice@example.com", "action": "add_node", "params": {"id": "frontend", "label": "Frontend App"}},
            {"user": "alice@example.com", "action": "add_node", "params": {"id": "backend", "label": "Backend API"}},
            {"user": "alice@example.com", "action": "add_edge", "params": {"from": "frontend", "to": "backend"}},
        ]
        bob_changes = [
            {"user": "bob@example.com", "action": "add_node", "params": {"id": "database", "label": "Database"}},
            {"user": "bob@example.com", "action": "add_edge", "params": {"from": "backend", "to": "database"}},
        ]
        charlie_changes = [
            {"user": "charlie@example.com", "action": "add_node", "params": {"id": "cache", "label": "Redis Cache"}},
            {"user": "charlie@example.com", "action": "add_edge", "params": {"from": "backend", "to": "cache"}},
        ]
        all_changes = alice_changes + bob_changes + charlie_changes
        
        print("Applying collaborative changes...")
        for i, change in enumerate(all_changes):
            print(f"  Change {i+1}: {change['user']} - {change['action']}")
            result = collab_manager.apply_change(
                session.session_id,
                change['user'],
                change['action'],
                change['params']
            )
            if getattr(result, "success", False):
                print(f"    ✅ Applied successfully")
            else:
                print(f"    ❌ Conflict detected: {getattr(result, 'conflict_reason', 'Unknown conflict')}")
        
        # Get collaboration history
        history = collab_manager.get_change_history(session.session_id)
        
        # Save collaboration data
        collab_data = {
            "session_id": session.session_id,
            "project_name": getattr(session, "project_name", getattr(session, "title", "Untitled Project")),
            "participants": participants,
            "changes": all_changes,
            "history": [
                {
                    "timestamp": h.timestamp.isoformat(),
                    "user": h.user,
                    "action": h.action,
                    "description": h.description
                }
                for h in history
            ],
            "created_at": getattr(session, "created_at", datetime.now()).isoformat()
        }
        
        collab_path = output_dir / "collaborative_session.json"
        with open(collab_path, 'w') as f:
            json.dump(collab_data, f, indent=2)
        
        print(f"📁 Collaborative session saved to {collab_path}")
        
    except Exception as e:
        print(f"❌ Error in collaborative editing: {e}")


def version_control_example(output_dir: Path):
    """Demonstrate version control features."""
    print("Version control example...")
    
    try:
        # Create version control system
        vc = VersionControl(repository_path=output_dir / "diagram_repo")
        
        # Initialize repository
        vc.init_repository()
        print("✅ Initialized diagram repository")
        
        # Create initial diagram
        initial_diagram = FlowchartDiagram(title="System Architecture v1.0")
        initial_diagram.add_node("web", "Web Server", shape="rectangle")
        initial_diagram.add_node("db", "Database", shape="cylinder")
        initial_diagram.add_edge("web", "db")
        
        # Commit initial version
        commit1 = commit_diagram_changes(
            vc,
            diagram=initial_diagram,
            message="Initial system architecture",
            author="alice@example.com"
        )
        print(f"📝 Committed version 1: {commit1.commit_id[:8]}")
        
        # Create second version with API layer
        v2_diagram = FlowchartDiagram(title="System Architecture v2.0")
        v2_diagram.add_node("web", "Web Server", shape="rectangle")
        v2_diagram.add_node("api", "API Gateway", shape="rectangle")
        v2_diagram.add_node("db", "Database", shape="cylinder")
        v2_diagram.add_edge("web", "api")
        v2_diagram.add_edge("api", "db")
        
        # Commit second version
        commit2 = commit_diagram_changes(
            vc,
            diagram=v2_diagram,
            message="Add API Gateway layer",
            author="bob@example.com"
        )
        print(f"📝 Committed version 2: {commit2.commit_id[:8]}")
        
        # Create third version with microservices
        v3_diagram = FlowchartDiagram(title="System Architecture v3.0")
        v3_diagram.add_node("web", "Web Server", shape="rectangle")
        v3_diagram.add_node("api", "API Gateway", shape="rectangle")
        v3_diagram.add_node("auth", "Auth Service", shape="rectangle")
        v3_diagram.add_node("user", "User Service", shape="rectangle")
        v3_diagram.add_node("db", "Database", shape="cylinder")
        v3_diagram.add_edge("web", "api")
        v3_diagram.add_edge("api", "auth")
        v3_diagram.add_edge("api", "user")
        v3_diagram.add_edge("auth", "db")
        v3_diagram.add_edge("user", "db")
        
        # Commit third version
        commit3 = commit_diagram_changes(
            vc,
            diagram=v3_diagram,
            message="Refactor to microservices architecture",
            author="charlie@example.com"
        )
        print(f"📝 Committed version 3: {commit3.commit_id[:8]}")
        
        # Get commit history
        history = vc.get_commit_history()
        
        print(f"📚 Version history ({len(history)} commits):")
        for commit in history:
            print(f"   {commit.commit_id[:8]} - {commit.message} ({commit.author})")
        
        # Create branch for experimental features
        branch_name = "feature/caching-layer"
        vc.create_branch(branch_name, from_commit=commit3.commit_id)
        print(f"🌿 Created branch: {branch_name}")
        
        # Switch to branch and add caching
        vc.checkout_branch(branch_name)
        
        branch_diagram = FlowchartDiagram(title="System Architecture v3.1 (with Cache)")
        branch_diagram.add_node("web", "Web Server", shape="rectangle")
        branch_diagram.add_node("api", "API Gateway", shape="rectangle")
        branch_diagram.add_node("auth", "Auth Service", shape="rectangle")
        branch_diagram.add_node("user", "User Service", shape="rectangle")
        branch_diagram.add_node("cache", "Redis Cache", shape="cylinder")
        branch_diagram.add_node("db", "Database", shape="cylinder")
        branch_diagram.add_edge("web", "api")
        branch_diagram.add_edge("api", "auth")
        branch_diagram.add_edge("api", "user")
        branch_diagram.add_edge("auth", "cache")
        branch_diagram.add_edge("user", "cache")
        branch_diagram.add_edge("auth", "db")
        branch_diagram.add_edge("user", "db")
        
        # Commit to branch
        branch_commit = commit_diagram_changes(
            vc,
            diagram=branch_diagram,
            message="Add Redis caching layer",
            author="alice@example.com"
        )
        print(f"📝 Committed to branch: {branch_commit.commit_id[:8]}")
        
        # Save version control data
        vc_data = {
            "repository_path": str(vc.repository_path),
            "commits": [
                {
                    "commit_id": c.commit_id,
                    "message": c.message,
                    "author": c.author,
                    "timestamp": c.timestamp.isoformat(),
                    "parent_id": c.parent_id
                }
                for c in history
            ],
            "branches": vc.list_branches(),
            "current_branch": vc.get_current_branch()
        }
        
        vc_path = output_dir / "version_control_data.json"
        with open(vc_path, 'w') as f:
            json.dump(vc_data, f, indent=2)
        
        print(f"📁 Version control data saved to {vc_path}")
        
        # Render all versions
        renderer = MermaidRenderer()
        versions = [
            ("v1", initial_diagram),
            ("v2", v2_diagram),
            ("v3", v3_diagram),
            ("v3.1-cache", branch_diagram)
        ]
        
        for version_name, diagram in versions:
            version_path = output_dir / f"architecture_{version_name}.svg"
            renderer.save(diagram, version_path)
            print(f"📁 Rendered {version_name} to {version_path}")
        
    except Exception as e:
        print(f"❌ Error in version control: {e}")


def real_time_collaboration_simulation(output_dir: Path):
    """Simulate real-time collaboration features."""
    print("Real-time collaboration simulation...")
    
    # Simulate a real-time collaborative session
    class MockCollaborativeSession:
        def __init__(self, session_id: str):
            self.session_id = session_id
            self.participants = {}
            self.diagram = FlowchartDiagram(title="Collaborative Diagram")
            self.change_log = []
            self.cursors = {}
        
        def add_participant(self, user_id: str, user_name: str):
            self.participants[user_id] = {
                "name": user_name,
                "joined_at": datetime.now(),
                "is_active": True,
                "cursor_position": None
            }
        
        def apply_change(self, user_id: str, change_type: str, data: Dict[str, Any]):
            timestamp = datetime.now()
            
            change = {
                "id": len(self.change_log) + 1,
                "user_id": user_id,
                "user_name": self.participants[user_id]["name"],
                "type": change_type,
                "data": data,
                "timestamp": timestamp.isoformat()
            }
            
            # Apply change to diagram
            try:
                if change_type == "add_node":
                    self.diagram.add_node(
                        data["id"],
                        data["label"],
                        shape=data.get("shape", "rectangle")
                    )
                elif change_type == "add_edge":
                    self.diagram.add_edge(
                        data["from"],
                        data["to"],
                        label=data.get("label")
                    )
                elif change_type == "update_node":
                    # Update node properties
                    if data["id"] in self.diagram.nodes:
                        node = self.diagram.nodes[data["id"]]
                        if "label" in data:
                            node.label = data["label"]
                
                change["success"] = True
                
            except Exception as e:
                change["success"] = False
                change["error"] = str(e)
            
            self.change_log.append(change)
            return change
        
        def update_cursor(self, user_id: str, position: Dict[str, Any]):
            self.cursors[user_id] = {
                "position": position,
                "timestamp": datetime.now().isoformat()
            }
        
        def get_state(self):
            return {
                "session_id": self.session_id,
                "participants": self.participants,
                "diagram_code": self.diagram.to_mermaid(),
                "change_log": self.change_log,
                "cursors": self.cursors
            }
    
    # Create collaborative session
    session = MockCollaborativeSession("collab-session-123")
    
    # Add participants
    session.add_participant("alice", "Alice (Frontend Dev)")
    session.add_participant("bob", "Bob (Backend Dev)")
    session.add_participant("charlie", "Charlie (DevOps)")
    
    print(f"✅ Created collaborative session with {len(session.participants)} participants")
    
    # Simulate real-time changes
    collaborative_changes = [
        {"user": "alice", "type": "add_node", "data": {"id": "frontend", "label": "React Frontend"}},
        {"user": "bob", "type": "add_node", "data": {"id": "api", "label": "REST API"}},
        {"user": "alice", "type": "add_edge", "data": {"from": "frontend", "to": "api", "label": "HTTP"}},
        {"user": "charlie", "type": "add_node", "data": {"id": "lb", "label": "Load Balancer"}},
        {"user": "bob", "type": "add_node", "data": {"id": "db", "label": "PostgreSQL", "shape": "cylinder"}},
        {"user": "charlie", "type": "add_edge", "data": {"from": "lb", "to": "api"}},
        {"user": "bob", "type": "add_edge", "data": {"from": "api", "to": "db"}},
        {"user": "alice", "type": "update_node", "data": {"id": "frontend", "label": "React Frontend (v18)"}},
    ]
    
    print("Simulating real-time collaborative changes...")
    for i, change in enumerate(collaborative_changes):
        print(f"  Change {i+1}: {change['user']} - {change['type']}")
        
        result = session.apply_change(
            change['user'],
            change['type'],
            change['data']
        )
        
        if result['success']:
            print(f"    ✅ Applied successfully")
        else:
            print(f"    ❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Simulate cursor updates
        session.update_cursor(change['user'], {
            "x": 100 + (i * 50),
            "y": 200 + (i * 30),
            "element": change['data'].get('id', 'canvas')
        })
        
        # Small delay to simulate real-time
        time.sleep(0.1)
    
    # Get final session state
    final_state = session.get_state()
    
    # Save collaboration simulation
    collab_sim_path = output_dir / "realtime_collaboration_simulation.json"
    with open(collab_sim_path, 'w') as f:
        json.dump(final_state, f, indent=2, default=str)
    
    print(f"📁 Collaboration simulation saved to {collab_sim_path}")
    
    # Render final collaborative diagram
    renderer = MermaidRenderer()
    final_diagram_path = output_dir / "collaborative_final_diagram.svg"
    renderer.save(session.diagram, final_diagram_path)
    print(f"📁 Final collaborative diagram saved to {final_diagram_path}")


def create_output_dir():
    """Create output directory for examples."""
    output_dir = Path("output/interactive")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def main():
    """Run all interactive and collaboration examples."""
    print("=== Mermaid Render Interactive & Collaboration Showcase ===\n")
    
    if not INTERACTIVE_AVAILABLE:
        print("⚠️  Interactive features require additional dependencies.")
        print("Install with: pip install mermaid-render[interactive]\n")
    
    if not COLLABORATION_AVAILABLE:
        print("⚠️  Collaboration features require additional dependencies.")
        print("Install with: pip install mermaid-render[collaboration]\n")
    
    # Create output directory
    output_dir = create_output_dir()
    print(f"Output directory: {output_dir.absolute()}\n")
    
    # Run examples
    try:
        interactive_builder_example(output_dir)
        print()
        
        collaborative_editing_example(output_dir)
        print()
        
        version_control_example(output_dir)
        print()
        
        real_time_collaboration_simulation(output_dir)
        print()
        
        print("✅ Interactive and collaboration examples completed!")
        print(f"Check the {output_dir} directory for generated files.")
        
    except Exception as e:
        print(f"❌ Error running interactive/collaboration examples: {e}")
        raise


if __name__ == "__main__":
    main()
