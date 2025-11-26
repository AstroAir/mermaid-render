#!/usr/bin/env python3
"""
Version Management Script for Mermaid Render

This script provides automated version management with semantic versioning,
changelog generation, and release preparation.

Usage:
    python scripts/version_manager.py --help
    python scripts/version_manager.py bump patch
    python scripts/version_manager.py bump minor --dry-run
    python scripts/version_manager.py prepare-release
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class VersionManager:
    """Manages version bumping, changelog generation, and release preparation."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.pyproject_path = self.project_root / "pyproject.toml"
        self.changelog_path = self.project_root / "CHANGELOG.md"
        self.init_path = self.project_root / "mermaid_render" / "__init__.py"

    def get_current_version(self) -> str:
        """Get the current version from git tags."""
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.project_root,
            )
            version = result.stdout.strip()
            # Remove 'v' prefix if present
            return version.lstrip("v")
        except subprocess.CalledProcessError:
            # No tags found, start with 0.1.0
            return "0.1.0"

    def parse_version(self, version: str) -> tuple[int, int, int, str | None]:
        """Parse a semantic version string."""
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$"
        match = re.match(pattern, version)
        if not match:
            raise ValueError(f"Invalid version format: {version}")

        major, minor, patch, prerelease = match.groups()
        return int(major), int(minor), int(patch), prerelease

    def bump_version(self, current: str, bump_type: str) -> str:
        """Bump version according to semantic versioning rules."""
        major, minor, patch, prerelease = self.parse_version(current)

        if bump_type == "major":
            return f"{major + 1}.0.0"
        elif bump_type == "minor":
            return f"{major}.{minor + 1}.0"
        elif bump_type == "patch":
            return f"{major}.{minor}.{patch + 1}"
        elif bump_type == "prerelease":
            if prerelease:
                # Increment prerelease number
                parts = prerelease.split(".")
                if parts[-1].isdigit():
                    parts[-1] = str(int(parts[-1]) + 1)
                else:
                    parts.append("1")
                return f"{major}.{minor}.{patch}-{'.'.join(parts)}"
            else:
                return f"{major}.{minor}.{patch}-rc.1"
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

    def get_commits_since_tag(self, tag: str | None = None) -> list[dict[str, str]]:
        """Get commits since the last tag."""
        if tag:
            cmd = [
                "git",
                "log",
                f"{tag}..HEAD",
                "--pretty=format:%H|%s|%an|%ad",
                "--date=short",
            ]
        else:
            cmd = ["git", "log", "--pretty=format:%H|%s|%an|%ad", "--date=short"]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, cwd=self.project_root
            )
            commits = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    hash_val, subject, author, date = line.split("|", 3)
                    commits.append(
                        {
                            "hash": hash_val,
                            "subject": subject,
                            "author": author,
                            "date": date,
                        }
                    )
            return commits
        except subprocess.CalledProcessError:
            return []

    def categorize_commits(
        self, commits: list[dict[str, str]]
    ) -> dict[str, list[dict[str, str]]]:
        """Categorize commits by type for changelog generation."""
        categories: dict[str, list[dict[str, str]]] = {
            "breaking": [],
            "features": [],
            "fixes": [],
            "improvements": [],
            "docs": [],
            "chore": [],
            "other": [],
        }

        patterns = {
            "breaking": [r"^BREAKING CHANGE:", r"^feat!:", r"^fix!:"],
            "features": [r"^feat:", r"^feature:"],
            "fixes": [r"^fix:", r"^bugfix:"],
            "improvements": [r"^perf:", r"^refactor:", r"^style:"],
            "docs": [r"^docs?:", r"^documentation:"],
            "chore": [r"^chore:", r"^ci:", r"^build:", r"^test:"],
        }

        for commit in commits:
            subject = commit["subject"].lower()
            categorized = False

            for category, category_patterns in patterns.items():
                for pattern in category_patterns:
                    if re.match(pattern, subject):
                        categories[category].append(commit)
                        categorized = True
                        break
                if categorized:
                    break

            if not categorized:
                categories["other"].append(commit)

        return categories

    def generate_changelog_entry(
        self, version: str, commits: list[dict[str, str]]
    ) -> str:
        """Generate a changelog entry for the new version."""
        categories = self.categorize_commits(commits)
        date = datetime.now().strftime("%Y-%m-%d")

        entry = f"## [{version}] - {date}\n\n"

        if categories["breaking"]:
            entry += "### ⚠ BREAKING CHANGES\n\n"
            for commit in categories["breaking"]:
                entry += f"- {commit['subject']} ({commit['hash'][:8]})\n"
            entry += "\n"

        if categories["features"]:
            entry += "### ✨ Features\n\n"
            for commit in categories["features"]:
                entry += f"- {commit['subject']} ({commit['hash'][:8]})\n"
            entry += "\n"

        if categories["fixes"]:
            entry += "### 🐛 Bug Fixes\n\n"
            for commit in categories["fixes"]:
                entry += f"- {commit['subject']} ({commit['hash'][:8]})\n"
            entry += "\n"

        if categories["improvements"]:
            entry += "### 🚀 Improvements\n\n"
            for commit in categories["improvements"]:
                entry += f"- {commit['subject']} ({commit['hash'][:8]})\n"
            entry += "\n"

        if categories["docs"]:
            entry += "### 📚 Documentation\n\n"
            for commit in categories["docs"]:
                entry += f"- {commit['subject']} ({commit['hash'][:8]})\n"
            entry += "\n"

        if categories["other"]:
            entry += "### 🔧 Other Changes\n\n"
            for commit in categories["other"]:
                entry += f"- {commit['subject']} ({commit['hash'][:8]})\n"
            entry += "\n"

        return entry

    def update_changelog(
        self, version: str, commits: list[dict[str, str]], dry_run: bool = False
    ) -> None:
        """Update the changelog with the new version entry."""
        new_entry = self.generate_changelog_entry(version, commits)

        if not self.changelog_path.exists():
            content = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
        else:
            content = self.changelog_path.read_text()

        # Insert new entry after the header
        lines = content.split("\n")
        header_end = 0
        for i, line in enumerate(lines):
            if line.startswith("## [") or (i > 0 and line.strip() == ""):
                header_end = i
                break

        lines.insert(header_end, new_entry)
        new_content = "\n".join(lines)

        if dry_run:
            print("Changelog entry (dry run):")
            print(new_entry)
        else:
            self.changelog_path.write_text(new_content)
            print(f"Updated {self.changelog_path}")

    def create_git_tag(self, version: str, dry_run: bool = False) -> None:
        """Create a git tag for the new version."""
        tag_name = f"v{version}"
        message = f"Release version {version}"

        if dry_run:
            print(f"Would create tag: {tag_name}")
            return

        try:
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", message],
                check=True,
                cwd=self.project_root,
            )
            print(f"Created tag: {tag_name}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create tag: {e}")
            sys.exit(1)

    def validate_working_directory(self) -> None:
        """Validate that the working directory is clean."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.project_root,
            )
            if result.stdout.strip():
                print(
                    "Error: Working directory is not clean. Please commit or stash changes."
                )
                sys.exit(1)
        except subprocess.CalledProcessError:
            print("Error: Not in a git repository.")
            sys.exit(1)

    def bump_and_tag(self, bump_type: str, dry_run: bool = False) -> str:
        """Bump version and create tag."""
        if not dry_run:
            self.validate_working_directory()

        current_version = self.get_current_version()
        new_version = self.bump_version(current_version, bump_type)

        print(f"Current version: {current_version}")
        print(f"New version: {new_version}")

        # Get commits since last tag
        last_tag = f"v{current_version}" if current_version != "0.1.0" else None
        commits = self.get_commits_since_tag(last_tag)

        if not commits:
            print("No commits found since last tag.")
            return new_version

        print(f"Found {len(commits)} commits since last tag")

        # Update changelog
        self.update_changelog(new_version, commits, dry_run)

        # Create git tag
        self.create_git_tag(new_version, dry_run)

        return new_version

    def prepare_release(self, dry_run: bool = False) -> None:
        """Prepare a release by running all necessary checks and updates."""
        print("Preparing release...")

        if not dry_run:
            self.validate_working_directory()

        # Run tests
        print("Running tests...")
        if not dry_run:
            try:
                subprocess.run(
                    ["python", "-m", "pytest"], check=True, cwd=self.project_root
                )
                print("✓ Tests passed")
            except subprocess.CalledProcessError:
                print("✗ Tests failed")
                sys.exit(1)

        # Run linting
        print("Running linting...")
        if not dry_run:
            try:
                subprocess.run(
                    ["python", "-m", "ruff", "check", "mermaid_render"],
                    check=True,
                    cwd=self.project_root,
                )
                subprocess.run(
                    ["python", "-m", "black", "--check", "mermaid_render"],
                    check=True,
                    cwd=self.project_root,
                )
                print("✓ Linting passed")
            except subprocess.CalledProcessError:
                print("✗ Linting failed")
                sys.exit(1)

        # Build package
        print("Building package...")
        if not dry_run:
            try:
                subprocess.run(
                    ["python", "-m", "build"], check=True, cwd=self.project_root
                )
                print("✓ Package built successfully")
            except subprocess.CalledProcessError:
                print("✗ Package build failed")
                sys.exit(1)

        print("Release preparation complete!")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Version management for Mermaid Render"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Bump command
    bump_parser = subparsers.add_parser("bump", help="Bump version")
    bump_parser.add_argument(
        "type",
        choices=["major", "minor", "patch", "prerelease"],
        help="Version bump type",
    )
    bump_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    # Prepare release command
    release_parser = subparsers.add_parser("prepare-release", help="Prepare a release")
    release_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    # Current version command
    subparsers.add_parser("current", help="Show current version")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = VersionManager()

    if args.command == "bump":
        manager.bump_and_tag(args.type, args.dry_run)
    elif args.command == "prepare-release":
        manager.prepare_release(args.dry_run)
    elif args.command == "current":
        print(manager.get_current_version())


if __name__ == "__main__":
    main()
