#!/usr/bin/env python3
"""
Development utility script for Mermaid Render project.

This script provides common development tasks like running tests,
linting, formatting, and building the project.

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
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str], check: bool = True, cwd: Optional[Path] = None) -> int:
    """Run a command and return the exit code."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check, cwd=cwd)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        return e.returncode


def setup_dev_environment() -> None:
    """Set up the development environment."""
    print("Setting up development environment...")
    
    # Install development dependencies
    run_command([sys.executable, "-m", "pip", "install", "-e", ".[dev,test,all]"])
    
    # Install pre-commit hooks
    run_command([sys.executable, "-m", "pre_commit", "install"])
    run_command([sys.executable, "-m", "pre_commit", "install", "--hook-type", "commit-msg"])
    
    print("Development environment setup complete!")


def run_tests() -> int:
    """Run tests with coverage."""
    print("Running tests with coverage...")
    return run_command([
        sys.executable, "-m", "pytest",
        "--cov=mermaid_render",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "-v"
    ])


def run_lint() -> int:
    """Run linting checks."""
    print("Running linting checks...")
    exit_code = 0
    
    # Run ruff
    exit_code |= run_command([sys.executable, "-m", "ruff", "check", "mermaid_render/", "tests/"], check=False)
    
    # Run black check
    exit_code |= run_command([sys.executable, "-m", "black", "--check", "mermaid_render/", "tests/"], check=False)
    
    return exit_code


def format_code() -> None:
    """Format code with black and ruff."""
    print("Formatting code...")
    
    # Run ruff fix
    run_command([sys.executable, "-m", "ruff", "check", "--fix", "mermaid_render/", "tests/"])
    
    # Run black
    run_command([sys.executable, "-m", "black", "mermaid_render/", "tests/"])
    
    print("Code formatting complete!")


def run_type_check() -> int:
    """Run type checking with mypy."""
    print("Running type checks...")
    return run_command([sys.executable, "-m", "mypy", "mermaid_render/"], check=False)


def run_security_checks() -> int:
    """Run security checks."""
    print("Running security checks...")
    exit_code = 0
    
    # Run bandit
    exit_code |= run_command([
        sys.executable, "-m", "bandit", "-r", "mermaid_render/",
        "-f", "json", "-o", "bandit-report.json"
    ], check=False)
    
    # Run safety
    exit_code |= run_command([sys.executable, "-m", "safety", "check"], check=False)
    
    return exit_code


def build_package() -> int:
    """Build the package."""
    print("Building package...")
    return run_command([sys.executable, "-m", "build"])


def clean_artifacts() -> None:
    """Clean build artifacts."""
    print("Cleaning build artifacts...")
    import shutil
    
    artifacts = [
        "build/", "dist/", "*.egg-info/",
        ".coverage", "coverage.xml", "htmlcov/",
        ".pytest_cache/", ".mypy_cache/",
        "bandit-report.json"
    ]
    
    for pattern in artifacts:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed directory: {path}")
            elif path.is_file():
                path.unlink()
                print(f"Removed file: {path}")


def build_docs() -> int:
    """Build documentation."""
    print("Building documentation...")
    docs_dir = Path("docs")
    if docs_dir.exists():
        return run_command([sys.executable, "-m", "sphinx", "-b", "html", "docs/", "docs/_build/html/"])
    else:
        print("No docs directory found. Skipping documentation build.")
        return 0


def run_all_checks() -> int:
    """Run all checks."""
    print("Running all checks...")
    exit_code = 0
    
    exit_code |= run_lint()
    exit_code |= run_type_check()
    exit_code |= run_tests()
    exit_code |= run_security_checks()
    
    if exit_code == 0:
        print("All checks passed!")
    else:
        print("Some checks failed!")
    
    return exit_code


def run_pre_commit() -> int:
    """Install and run pre-commit hooks."""
    print("Running pre-commit hooks...")
    
    # Install hooks if not already installed
    run_command([sys.executable, "-m", "pre_commit", "install"], check=False)
    
    # Run on all files
    return run_command([sys.executable, "-m", "pre_commit", "run", "--all-files"], check=False)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Development utility for Mermaid Render")
    parser.add_argument("command", choices=[
        "setup", "test", "lint", "format", "type-check", "security",
        "build", "clean", "docs", "all", "pre-commit"
    ], help="Command to run")
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    
    commands = {
        "setup": setup_dev_environment,
        "test": run_tests,
        "lint": run_lint,
        "format": format_code,
        "type-check": run_type_check,
        "security": run_security_checks,
        "build": build_package,
        "clean": clean_artifacts,
        "docs": build_docs,
        "all": run_all_checks,
        "pre-commit": run_pre_commit,
    }
    
    exit_code = commands[args.command]()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
