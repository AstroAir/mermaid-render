#!/usr/bin/env python3
"""
Cross-platform development environment setup script for Mermaid Render.

This script provides a comprehensive development environment setup that works
across Windows, macOS, and Linux platforms.

Usage:
    python scripts/setup-dev.py [options]

Options:
    --skip-venv     Skip virtual environment creation
    --skip-deps     Skip dependency installation
    --skip-hooks    Skip pre-commit hooks setup
    --skip-dirs     Skip directory creation
    --verbose       Enable verbose output
    --force         Force overwrite existing configurations
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import venv
from pathlib import Path
from typing import List, Optional, Tuple


class Colors:
    """ANSI color codes for cross-platform colored output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color
    
    @classmethod
    def disable_on_windows(cls):
        """Disable colors on Windows if not supported."""
        if platform.system() == "Windows" and not os.environ.get("ANSICON"):
            cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = cls.NC = ""


class DevSetup:
    """Cross-platform development environment setup."""
    
    def __init__(self, verbose: bool = False, force: bool = False):
        self.verbose = verbose
        self.force = force
        self.project_root = Path(__file__).parent.parent
        self.system = platform.system()
        
        # Disable colors on unsupported Windows terminals
        if self.system == "Windows":
            Colors.disable_on_windows()
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with color coding."""
        color_map = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED
        }
        
        prefix_map = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌"
        }
        
        if self.verbose or level in ["SUCCESS", "WARNING", "ERROR"]:
            color = color_map.get(level, "")
            prefix = prefix_map.get(level, "📝")
            print(f"{color}[{prefix} {level}]{Colors.NC} {message}")
    
    def run_command(self, cmd: List[str], check: bool = True, 
                   capture_output: bool = False) -> Tuple[int, str, str]:
        """Run a command with proper error handling."""
        self.log(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                check=check,
                capture_output=capture_output,
                text=True,
                cwd=self.project_root
            )
            return result.returncode, result.stdout or "", result.stderr or ""
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed with exit code {e.returncode}", "ERROR")
            return e.returncode, e.stdout or "", e.stderr or ""
        except FileNotFoundError:
            self.log(f"Command not found: {cmd[0]}", "ERROR")
            return 1, "", f"Command not found: {cmd[0]}"
    
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements."""
        self.log("Checking Python version...")
        
        version = sys.version_info
        required = (3, 9)
        
        if version >= required:
            self.log(f"Python {version.major}.{version.minor}.{version.micro} is compatible", "SUCCESS")
            return True
        else:
            self.log(f"Python {version.major}.{version.minor} is too old. Requires Python {required[0]}.{required[1]}+", "ERROR")
            return False
    
    def setup_virtual_environment(self) -> bool:
        """Set up virtual environment."""
        self.log("Setting up virtual environment...")
        
        venv_path = self.project_root / "venv"
        
        if venv_path.exists() and not self.force:
            self.log("Virtual environment already exists", "INFO")
            return True
        
        try:
            if venv_path.exists():
                shutil.rmtree(venv_path)
            
            # Create virtual environment
            venv.create(venv_path, with_pip=True)
            self.log("Virtual environment created", "SUCCESS")
            
            # Get the correct Python executable path
            if self.system == "Windows":
                python_exe = venv_path / "Scripts" / "python.exe"
                pip_exe = venv_path / "Scripts" / "pip.exe"
            else:
                python_exe = venv_path / "bin" / "python"
                pip_exe = venv_path / "bin" / "pip"
            
            # Upgrade pip
            self.log("Upgrading pip...")
            exit_code, _, _ = self.run_command([str(pip_exe), "install", "--upgrade", "pip"])
            
            if exit_code == 0:
                self.log("Pip upgraded successfully", "SUCCESS")
                return True
            else:
                self.log("Failed to upgrade pip", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Failed to create virtual environment: {e}", "ERROR")
            return False
    
    def get_python_executable(self) -> str:
        """Get the correct Python executable for the current environment."""
        venv_path = self.project_root / "venv"
        
        if venv_path.exists():
            if self.system == "Windows":
                return str(venv_path / "Scripts" / "python.exe")
            else:
                return str(venv_path / "bin" / "python")
        else:
            return sys.executable
    
    def install_dependencies(self) -> bool:
        """Install project dependencies."""
        self.log("Installing dependencies...")
        
        python_exe = self.get_python_executable()
        
        # Check if UV is available and prefer it
        uv_available = shutil.which("uv") is not None
        
        if uv_available:
            self.log("Using UV for dependency installation...")
            exit_code, _, stderr = self.run_command([
                "uv", "sync", "--all-extras"
            ])
        else:
            self.log("Using pip for dependency installation...")
            exit_code, _, stderr = self.run_command([
                python_exe, "-m", "pip", "install", "-e", 
                ".[dev,test,cache,interactive,ai,collaboration,docs,pdf,performance,all]"
            ])
        
        if exit_code == 0:
            self.log("Dependencies installed successfully", "SUCCESS")
            return True
        else:
            self.log(f"Failed to install dependencies: {stderr}", "ERROR")
            return False
    
    def setup_pre_commit_hooks(self) -> bool:
        """Set up pre-commit hooks."""
        self.log("Setting up pre-commit hooks...")
        
        python_exe = self.get_python_executable()
        
        # Install pre-commit if not available
        exit_code, _, _ = self.run_command([
            python_exe, "-c", "import pre_commit"
        ], check=False)
        
        if exit_code != 0:
            self.log("Installing pre-commit...")
            exit_code, _, _ = self.run_command([
                python_exe, "-m", "pip", "install", "pre-commit"
            ])
            
            if exit_code != 0:
                self.log("Failed to install pre-commit", "ERROR")
                return False
        
        # Install hooks
        exit_code, _, _ = self.run_command([
            python_exe, "-m", "pre_commit", "install"
        ])
        
        if exit_code == 0:
            # Install commit-msg hook
            self.run_command([
                python_exe, "-m", "pre_commit", "install", "--hook-type", "commit-msg"
            ], check=False)
            
            self.log("Pre-commit hooks installed", "SUCCESS")
            return True
        else:
            self.log("Failed to install pre-commit hooks", "ERROR")
            return False
    
    def create_directories(self) -> bool:
        """Create necessary project directories."""
        self.log("Creating necessary directories...")
        
        directories = [
            "output",
            "logs", 
            "profiling",
            "docs/_build",
            ".mermaid_cache",
            "temp",
            "benchmarks",
            "migrations"
        ]
        
        created_count = 0
        for directory in directories:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.log(f"Created directory: {directory}")
                    created_count += 1
                except Exception as e:
                    self.log(f"Failed to create directory {directory}: {e}", "WARNING")
        
        self.log(f"Created {created_count} directories", "SUCCESS")
        return True
    
    def setup_environment_file(self) -> bool:
        """Set up environment configuration file."""
        self.log("Setting up environment configuration...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if env_file.exists() and not self.force:
            self.log("Environment file already exists", "INFO")
            return True
        
        if env_example.exists():
            try:
                shutil.copy2(env_example, env_file)
                self.log("Environment file created from .env.example", "SUCCESS")
                self.log("Please edit .env to configure your environment", "INFO")
                return True
            except Exception as e:
                self.log(f"Failed to copy environment file: {e}", "WARNING")
                return False
        else:
            # Create a basic .env file
            basic_env = """# Mermaid Render Environment Configuration
# Copy this file to .env and customize as needed

# Development settings
MERMAID_RENDER_ENV=development
MERMAID_RENDER_LOG_LEVEL=DEBUG

# Cache settings
MERMAID_RENDER_CACHE_BACKEND=memory
MERMAID_RENDER_CACHE_TTL=3600

# Performance settings
MERMAID_RENDER_TIMEOUT=30
MERMAID_RENDER_MAX_WORKERS=4

# Security settings
MERMAID_RENDER_VALIDATE_INPUT=true
"""
            try:
                env_file.write_text(basic_env)
                self.log("Basic environment file created", "SUCCESS")
                return True
            except Exception as e:
                self.log(f"Failed to create environment file: {e}", "WARNING")
                return False
    
    def check_system_dependencies(self) -> bool:
        """Check for system dependencies."""
        self.log("Checking system dependencies...")
        
        dependencies = {
            "git": "Git version control",
            "node": "Node.js (for some tools)",
        }
        
        missing = []
        for cmd, description in dependencies.items():
            if not shutil.which(cmd):
                missing.append(f"{cmd} ({description})")
        
        if missing:
            self.log("Missing optional system dependencies:", "WARNING")
            for dep in missing:
                self.log(f"  - {dep}", "WARNING")
            
            # Provide installation instructions
            if self.system == "Windows":
                self.log("Install missing dependencies using:", "INFO")
                self.log("  - Git: https://git-scm.com/download/win", "INFO")
                self.log("  - Node.js: https://nodejs.org/", "INFO")
            elif self.system == "Darwin":  # macOS
                self.log("Install missing dependencies using Homebrew:", "INFO")
                self.log("  brew install git node", "INFO")
            else:  # Linux
                self.log("Install missing dependencies using your package manager:", "INFO")
                self.log("  Ubuntu/Debian: sudo apt-get install git nodejs npm", "INFO")
                self.log("  CentOS/RHEL: sudo yum install git nodejs npm", "INFO")
        else:
            self.log("All system dependencies are available", "SUCCESS")
        
        return True
    
    def setup_ide_configuration(self) -> bool:
        """Set up IDE configuration files."""
        self.log("Setting up IDE configuration...")
        
        vscode_dir = self.project_root / ".vscode"
        if not vscode_dir.exists() or self.force:
            try:
                vscode_dir.mkdir(exist_ok=True)
                
                # VS Code settings
                settings = {
                    "python.defaultInterpreterPath": "./venv/bin/python" if self.system != "Windows" else "./venv/Scripts/python.exe",
                    "python.linting.enabled": True,
                    "python.linting.pylintEnabled": False,
                    "python.linting.mypyEnabled": True,
                    "python.formatting.provider": "black",
                    "editor.formatOnSave": True,
                    "editor.codeActionsOnSave": {
                        "source.organizeImports": True
                    },
                    "files.exclude": {
                        "**/__pycache__": True,
                        "**/*.pyc": True,
                        ".pytest_cache": True,
                        ".mypy_cache": True,
                        "htmlcov": True,
                        "dist": True,
                        "build": True,
                        "*.egg-info": True
                    }
                }
                
                import json
                settings_file = vscode_dir / "settings.json"
                with open(settings_file, 'w') as f:
                    json.dump(settings, f, indent=2)
                
                self.log("VS Code settings created", "SUCCESS")
                return True
                
            except Exception as e:
                self.log(f"Failed to create IDE configuration: {e}", "WARNING")
                return False
        else:
            self.log("IDE configuration already exists", "INFO")
            return True
    
    def run_initial_validation(self) -> bool:
        """Run initial validation tests."""
        self.log("Running initial validation...")
        
        python_exe = self.get_python_executable()
        
        # Test package import
        exit_code, _, stderr = self.run_command([
            python_exe, "-c", "import mermaid_render; print('✅ Package import successful')"
        ], check=False)
        
        if exit_code == 0:
            self.log("Package import test passed", "SUCCESS")
        else:
            self.log("Package import test failed - this is expected in fresh setup", "WARNING")
        
        # Run a quick test if pytest is available
        exit_code, _, _ = self.run_command([
            python_exe, "-c", "import pytest"
        ], check=False)
        
        if exit_code == 0:
            self.log("Running basic tests...")
            exit_code, _, _ = self.run_command([
                python_exe, "-m", "pytest", "tests/", "-x", "-q", "--tb=short"
            ], check=False)
            
            if exit_code == 0:
                self.log("Basic tests passed", "SUCCESS")
            else:
                self.log("Some tests failed - this might be expected in fresh setup", "WARNING")
        
        return True
    
    def print_next_steps(self) -> None:
        """Print next steps for the user."""
        self.log("Development environment setup complete!", "SUCCESS")
        print()
        
        # Activation instructions
        if self.system == "Windows":
            activate_cmd = "venv\\Scripts\\activate"
        else:
            activate_cmd = "source venv/bin/activate"
        
        self.log("Next steps:", "INFO")
        self.log(f"1. Activate the virtual environment: {activate_cmd}", "INFO")
        self.log("2. Edit .env file to configure your environment", "INFO")
        self.log("3. Run tests: python scripts/dev.py test", "INFO")
        self.log("4. Start developing!", "INFO")
        print()
        
        self.log("Available commands:", "INFO")
        self.log("  python scripts/dev.py --help     - Show development script help", "INFO")
        self.log("  make help                        - Show Makefile targets", "INFO")
        self.log("  python scripts/qa-check.py       - Run quality checks", "INFO")
        print()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Cross-platform development environment setup")
    parser.add_argument("--skip-venv", action="store_true", help="Skip virtual environment creation")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--skip-hooks", action="store_true", help="Skip pre-commit hooks setup")
    parser.add_argument("--skip-dirs", action="store_true", help="Skip directory creation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--force", "-f", action="store_true", help="Force overwrite existing configurations")
    
    args = parser.parse_args()
    
    setup = DevSetup(verbose=args.verbose, force=args.force)
    
    setup.log("Starting Mermaid Render development environment setup...", "INFO")
    print()
    
    # Check Python version first
    if not setup.check_python_version():
        sys.exit(1)
    
    success = True
    
    # Run setup steps
    if not args.skip_venv:
        success &= setup.setup_virtual_environment()
    
    if not args.skip_deps and success:
        success &= setup.install_dependencies()
    
    if not args.skip_hooks and success:
        success &= setup.setup_pre_commit_hooks()
    
    if not args.skip_dirs:
        success &= setup.create_directories()
    
    success &= setup.setup_environment_file()
    success &= setup.check_system_dependencies()
    success &= setup.setup_ide_configuration()
    
    if success:
        setup.run_initial_validation()
        setup.print_next_steps()
    else:
        setup.log("Setup completed with some issues. Please check the output above.", "WARNING")
        sys.exit(1)


if __name__ == "__main__":
    main()
