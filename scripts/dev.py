#!/usr/bin/env python3
"""
Development utility script for Mermaid Render project.

This script provides common development tasks like running tests,
linting, formatting, and building the project with cross-platform support.

Usage:
    python scripts/dev.py <command> [options]

Commands:
    setup       - Set up development environment
    test        - Run tests with coverage
    lint        - Run linting checks
    format      - Format code with black and ruff
    type-check  - Run type checking with mypy
    security    - Run security checks
    build       - Build the package
    clean       - Clean build artifacts
    docs        - Build documentation
    all         - Run all checks (lint, type-check, test, security)
    pre-commit  - Install and run pre-commit hooks
    benchmark   - Run performance benchmarks
    docker      - Docker operations (build, run, test)
"""

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path


class DevTools:
    """Development tools with cross-platform support."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.system = platform.system()

        # Determine the correct Python executable
        venv_path = self.project_root / "venv"
        if venv_path.exists():
            if self.system == "Windows":
                self.python_exe = str(venv_path / "Scripts" / "python.exe")
            else:
                self.python_exe = str(venv_path / "bin" / "python")
        else:
            self.python_exe = sys.executable

    def run_command(
        self, cmd: list[str], check: bool = True, capture_output: bool = False
    ) -> tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        print(f"🔧 Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                check=check,
                cwd=self.project_root,
                capture_output=capture_output,
                text=True,
            )
            return result.returncode, result.stdout or "", result.stderr or ""
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed with exit code {e.returncode}")
            return e.returncode, e.stdout or "", e.stderr or ""
        except FileNotFoundError:
            print(f"❌ Command not found: {cmd[0]}")
            return 1, "", f"Command not found: {cmd[0]}"

    def check_tool_available(self, tool: str) -> bool:
        """Check if a tool is available."""
        return (
            shutil.which(tool) is not None
            or self.run_command(
                [self.python_exe, "-c", f"import {tool}"],
                check=False,
                capture_output=True,
            )[0]
            == 0
        )

    def setup_dev_environment(self) -> int:
        """Set up the development environment."""
        print("🚀 Setting up development environment...")

        # Use the cross-platform setup script
        exit_code, _, _ = self.run_command(
            [self.python_exe, "scripts/setup-dev.py", "--verbose"]
        )

        if exit_code == 0:
            print("✅ Development environment setup complete!")
        else:
            print("❌ Development environment setup failed!")

        return exit_code

    def run_tests(self) -> int:
        """Run tests with coverage."""
        print("🧪 Running tests with coverage...")

        # Check if UV is available for faster execution
        if self.check_tool_available("uv"):
            exit_code, _, _ = self.run_command(
                [
                    "uv",
                    "run",
                    "pytest",
                    "--cov=diagramaid",
                    "--cov-report=html",
                    "--cov-report=term-missing",
                    "--cov-report=xml",
                    "-v",
                ]
            )
        else:
            exit_code, _, _ = self.run_command(
                [
                    self.python_exe,
                    "-m",
                    "pytest",
                    "--cov=diagramaid",
                    "--cov-report=html",
                    "--cov-report=term-missing",
                    "--cov-report=xml",
                    "-v",
                ]
            )

        return exit_code

    def run_lint(self) -> int:
        """Run linting checks."""
        print("🔍 Running linting checks...")
        exit_code = 0

        # Run ruff
        ruff_exit, _, _ = self.run_command(
            [self.python_exe, "-m", "ruff", "check", "diagramaid/", "tests/"],
            check=False,
        )
        exit_code |= ruff_exit

        # Run black check
        black_exit, _, _ = self.run_command(
            [self.python_exe, "-m", "black", "--check", "diagramaid/", "tests/"],
            check=False,
        )
        exit_code |= black_exit

        return exit_code

    def format_code(self) -> int:
        """Format code with black and ruff."""
        print("🎨 Formatting code...")

        # Run ruff fix
        ruff_exit, _, _ = self.run_command(
            [
                self.python_exe,
                "-m",
                "ruff",
                "check",
                "--fix",
                "diagramaid/",
                "tests/",
            ]
        )

        # Run black
        black_exit, _, _ = self.run_command(
            [self.python_exe, "-m", "black", "diagramaid/", "tests/"]
        )

        if ruff_exit == 0 and black_exit == 0:
            print("✅ Code formatting complete!")
            return 0
        else:
            print("❌ Code formatting had issues!")
            return 1

    def run_type_check(self) -> int:
        """Run type checking with mypy."""
        print("🔬 Running type checks...")
        exit_code, _, _ = self.run_command(
            [self.python_exe, "-m", "mypy", "diagramaid/"], check=False
        )
        return exit_code

    def run_security_checks(self) -> int:
        """Run security checks."""
        print("🔒 Running security checks...")
        exit_code = 0

        # Run bandit
        bandit_exit, _, _ = self.run_command(
            [
                self.python_exe,
                "-m",
                "bandit",
                "-r",
                "diagramaid/",
                "-f",
                "json",
                "-o",
                "bandit-report.json",
            ],
            check=False,
        )
        exit_code |= bandit_exit

        # Run safety
        safety_exit, _, _ = self.run_command(
            [self.python_exe, "-m", "safety", "check"], check=False
        )
        exit_code |= safety_exit

        return exit_code

    def build_package(self) -> int:
        """Build the package."""
        print("📦 Building package...")
        exit_code, _, _ = self.run_command([self.python_exe, "-m", "build"])
        return exit_code

    def clean_artifacts(self) -> int:
        """Clean build artifacts."""
        print("🧹 Cleaning build artifacts...")

        artifacts = [
            "build/",
            "dist/",
            "*.egg-info/",
            ".coverage",
            "coverage.xml",
            "htmlcov/",
            ".pytest_cache/",
            ".mypy_cache/",
            "bandit-report.json",
            "profile.stats",
        ]

        removed_count = 0
        for pattern in artifacts:
            for path in self.project_root.glob(pattern):
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                        print(f"🗑️  Removed directory: {path}")
                        removed_count += 1
                    elif path.is_file():
                        path.unlink()
                        print(f"🗑️  Removed file: {path}")
                        removed_count += 1
                except Exception as e:
                    print(f"⚠️  Failed to remove {path}: {e}")

        print(f"✅ Cleaned {removed_count} artifacts")
        return 0

    def build_docs(self) -> int:
        """Build documentation."""
        print("📚 Building documentation...")

        # Check for MkDocs first (preferred)
        mkdocs_config = self.project_root / "mkdocs.yml"
        if mkdocs_config.exists():
            exit_code, _, _ = self.run_command(
                [self.python_exe, "-m", "mkdocs", "build", "--clean"]
            )
            return exit_code

        # Fall back to Sphinx
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            exit_code, _, _ = self.run_command(
                [
                    self.python_exe,
                    "-m",
                    "sphinx",
                    "-b",
                    "html",
                    "docs/",
                    "docs/_build/html/",
                ]
            )
            return exit_code
        else:
            print("⚠️  No documentation configuration found")
            return 0

    def run_all_checks(self) -> int:
        """Run all checks."""
        print("🔄 Running all checks...")
        exit_code = 0

        exit_code |= self.run_lint()
        exit_code |= self.run_type_check()
        exit_code |= self.run_tests()
        exit_code |= self.run_security_checks()

        if exit_code == 0:
            print("✅ All checks passed!")
        else:
            print("❌ Some checks failed!")

        return exit_code

    def run_pre_commit(self) -> int:
        """Install and run pre-commit hooks."""
        print("🪝 Running pre-commit hooks...")

        # Install hooks if not already installed
        self.run_command([self.python_exe, "-m", "pre_commit", "install"], check=False)

        # Run on all files
        exit_code, _, _ = self.run_command(
            [self.python_exe, "-m", "pre_commit", "run", "--all-files"], check=False
        )

        return exit_code

    def run_benchmark(self) -> int:
        """Run performance benchmarks."""
        print("⚡ Running performance benchmarks...")

        # Check if benchmark script exists
        benchmark_script = self.project_root / "benchmarks" / "run_benchmarks.py"
        if benchmark_script.exists():
            exit_code, _, _ = self.run_command([self.python_exe, str(benchmark_script)])
        else:
            # Run pytest benchmarks if available
            exit_code, _, _ = self.run_command(
                [self.python_exe, "-m", "pytest", "--benchmark-only", "-v"], check=False
            )

            if exit_code != 0:
                print("⚠️  No benchmark tests found")
                return 0

        return exit_code

    def docker_operations(self, operation: str = "build") -> int:
        """Handle Docker operations."""
        if not self.check_tool_available("docker"):
            print("❌ Docker is not available")
            return 1

        print(f"🐳 Docker {operation}...")

        if operation == "build":
            exit_code, _, _ = self.run_command(
                ["docker", "build", "-t", "diagramaid", "."]
            )
        elif operation == "run":
            exit_code, _, _ = self.run_command(
                ["docker", "run", "--rm", "-it", "diagramaid"]
            )
        elif operation == "test":
            exit_code, _, _ = self.run_command(
                ["docker", "run", "--rm", "diagramaid", "python", "-m", "pytest"]
            )
        else:
            print(f"❌ Unknown Docker operation: {operation}")
            return 1

        return exit_code


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Development utility for Mermaid Render",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/dev.py setup          # Set up development environment
  python scripts/dev.py test           # Run tests with coverage
  python scripts/dev.py all            # Run all quality checks
  python scripts/dev.py docker build   # Build Docker image
        """,
    )

    parser.add_argument(
        "command",
        choices=[
            "setup",
            "test",
            "lint",
            "format",
            "type-check",
            "security",
            "build",
            "clean",
            "docs",
            "all",
            "pre-commit",
            "benchmark",
            "docker",
        ],
        help="Command to run",
    )

    parser.add_argument(
        "subcommand",
        nargs="?",
        help="Subcommand for certain operations (e.g., docker build)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Initialize development tools
    dev_tools = DevTools()

    # Map commands to methods
    command_map = {
        "setup": dev_tools.setup_dev_environment,
        "test": dev_tools.run_tests,
        "lint": dev_tools.run_lint,
        "format": dev_tools.format_code,
        "type-check": dev_tools.run_type_check,
        "security": dev_tools.run_security_checks,
        "build": dev_tools.build_package,
        "clean": dev_tools.clean_artifacts,
        "docs": dev_tools.build_docs,
        "all": dev_tools.run_all_checks,
        "pre-commit": dev_tools.run_pre_commit,
        "benchmark": dev_tools.run_benchmark,
    }

    # Handle special cases
    if args.command == "docker":
        operation = args.subcommand or "build"
        exit_code = dev_tools.docker_operations(operation)
    elif args.command in command_map:
        exit_code = command_map[args.command]()
    else:
        parser.print_help()
        sys.exit(1)

    if exit_code == 0:
        print(f"✅ Command '{args.command}' completed successfully!")
    else:
        print(f"❌ Command '{args.command}' failed with exit code {exit_code}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
