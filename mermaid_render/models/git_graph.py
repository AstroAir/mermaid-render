"""Git graph diagram model for the Mermaid Render library."""

from typing import List, Optional

from ..core import MermaidDiagram


class GitGraphDiagram(MermaidDiagram):
    """Git graph diagram model for version control visualization.

    Supports defining branches, commits, and merges and emits Mermaid gitgraph syntax.
    """

    def __init__(self, title: Optional[str] = None) -> None:
        """Initialize an empty git graph.

        Args:
            title: Optional diagram title.
        """
        super().__init__(title)
        self.commits: List[tuple] = []
        self.branches: List[str] = []
        self.merges: List[tuple] = []

    def get_diagram_type(self) -> str:
        """Return the Mermaid diagram type identifier."""
        return "gitgraph"

    def add_commit(self, message: str, branch: str = "main") -> None:
        """Add a commit to the git graph.

        Args:
            message: Commit message or identifier.
            branch: Target branch name (defaults to 'main').
        """
        self.commits.append(("commit", message, branch))

    def add_branch(self, name: str) -> None:
        """Add a new branch.

        Args:
            name: Branch name to create.
        """
        self.branches.append(name)

    def add_merge(self, from_branch: str, to_branch: str) -> None:
        """Add a merge between branches.

        Args:
            from_branch: Source branch being merged.
            to_branch: Destination branch receiving the merge.
        """
        self.merges.append((from_branch, to_branch))

    def _generate_mermaid(self) -> str:
        """Generate Mermaid syntax for the git graph.

        Returns:
            Mermaid gitgraph diagram text including branches, commits, and merges.
        """
        lines = ["gitgraph"]

        if self.title:
            lines.append(f"    title: {self.title}")

        # Declare branches first
        for branch in self.branches:
            lines.append(f"    branch {branch}")

        # Emit commits. Mermaid gitgraph commonly uses `commit id: "<msg>"`.
        for _commit_type, message, _branch in self.commits:
            lines.append(f'    commit id: "{message}"')

        # Emit merges. Mermaid expects `merge <branch>`. Directionality is limited.
        for from_branch, _to_branch in self.merges:
            lines.append(f"    merge {from_branch}")

        return "\n".join(lines)
