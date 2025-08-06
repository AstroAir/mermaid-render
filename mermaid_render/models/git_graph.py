"""Git graph diagram model for the Mermaid Render library."""

from typing import List, Optional

from ..core import MermaidDiagram


class GitGraphDiagram(MermaidDiagram):
    """Git graph diagram model for version control visualization."""

    def __init__(self, title: Optional[str] = None) -> None:
        super().__init__(title)
        self.commits: List[tuple] = []
        self.branches: List[str] = []
        self.merges: List[tuple] = []

    def get_diagram_type(self) -> str:
        return "gitgraph"

    def add_commit(self, message: str, branch: str = "main") -> None:
        """Add a commit to the git graph."""
        self.commits.append(("commit", message, branch))

    def add_branch(self, name: str) -> None:
        """Add a new branch."""
        self.branches.append(name)

    def add_merge(self, from_branch: str, to_branch: str) -> None:
        """Add a merge between branches."""
        self.merges.append((from_branch, to_branch))

    def _generate_mermaid(self) -> str:
        """Generate Mermaid syntax for the git graph."""
        lines = ["gitgraph"]

        if self.title:
            lines.append(f"    title: {self.title}")

        for branch in self.branches:
            lines.append(f"    branch {branch}")

        for commit_type, message, branch in self.commits:
            lines.append(f'    commit id: "{message}"')

        for from_branch, to_branch in self.merges:
            lines.append(f"    merge {from_branch}")

        return "\n".join(lines)
