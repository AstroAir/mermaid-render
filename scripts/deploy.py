#!/usr/bin/env python3
"""
Deployment Automation Script for Mermaid Render

This script automates the deployment process for different environments
including staging, production, and development deployments.

Usage:
    python scripts/deploy.py <environment> [options]

Environments:
    staging     - Deploy to staging environment
    production  - Deploy to production environment
    dev         - Deploy development build
    docker      - Deploy using Docker

Options:
    --dry-run       Show what would be deployed without executing
    --skip-tests    Skip running tests before deployment
    --skip-build    Skip building the package
    --force         Force deployment even if checks fail
    --version       Specify version to deploy
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DeploymentManager:
    """Manages deployment operations for the project."""
    
    def __init__(self, project_root: Optional[Path] = None, verbose: bool = False):
        self.project_root = project_root or Path(__file__).parent.parent
        self.verbose = verbose
        self.deployment_config = self.load_deployment_config()
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message."""
        if self.verbose or level in ["ERROR", "WARNING", "SUCCESS"]:
            prefix = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
            print(f"{prefix.get(level, '📝')} {message}")
    
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
    
    def load_deployment_config(self) -> Dict:
        """Load deployment configuration."""
        config_file = self.project_root / "deployment.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.log(f"Failed to load deployment config: {e}", "WARNING")
        
        # Default configuration
        return {
            "environments": {
                "staging": {
                    "url": "https://staging.mermaid-render.com",
                    "registry": "staging-registry.example.com",
                    "branch": "develop",
                    "auto_migrate": True
                },
                "production": {
                    "url": "https://mermaid-render.com",
                    "registry": "registry.example.com",
                    "branch": "main",
                    "auto_migrate": False
                },
                "dev": {
                    "url": "http://localhost:8000",
                    "registry": None,
                    "branch": "current",
                    "auto_migrate": True
                }
            },
            "checks": {
                "run_tests": True,
                "run_linting": True,
                "run_security": True,
                "build_package": True
            }
        }
    
    def get_current_version(self) -> str:
        """Get current version from git or package."""
        # Try to get version from git tag
        exit_code, stdout, _ = self.run_command([
            "git", "describe", "--tags", "--abbrev=0"
        ], check=False, capture_output=True)
        
        if exit_code == 0 and stdout.strip():
            return stdout.strip().lstrip('v')
        
        # Try to get version from package
        try:
            import mermaid_render
            return getattr(mermaid_render, '__version__', '0.0.0')
        except ImportError:
            return '0.0.0'
    
    def run_pre_deployment_checks(self, skip_tests: bool = False) -> bool:
        """Run pre-deployment checks."""
        self.log("Running pre-deployment checks...")
        
        checks_config = self.deployment_config.get("checks", {})
        all_passed = True
        
        # Check git status
        exit_code, stdout, _ = self.run_command([
            "git", "status", "--porcelain"
        ], check=False, capture_output=True)
        
        if stdout.strip():
            self.log("Working directory is not clean", "WARNING")
            self.log("Uncommitted changes detected", "WARNING")
        
        # Run linting
        if checks_config.get("run_linting", True):
            self.log("Running linting checks...")
            exit_code, _, _ = self.run_command([
                sys.executable, "scripts/dev.py", "lint"
            ], check=False)
            
            if exit_code != 0:
                self.log("Linting checks failed", "ERROR")
                all_passed = False
            else:
                self.log("Linting checks passed", "SUCCESS")
        
        # Run tests
        if checks_config.get("run_tests", True) and not skip_tests:
            self.log("Running tests...")
            exit_code, _, _ = self.run_command([
                sys.executable, "scripts/dev.py", "test"
            ], check=False)
            
            if exit_code != 0:
                self.log("Tests failed", "ERROR")
                all_passed = False
            else:
                self.log("Tests passed", "SUCCESS")
        
        # Run security checks
        if checks_config.get("run_security", True):
            self.log("Running security checks...")
            exit_code, _, _ = self.run_command([
                sys.executable, "scripts/dev.py", "security"
            ], check=False)
            
            if exit_code != 0:
                self.log("Security checks failed", "WARNING")
                # Don't fail deployment for security warnings
        
        return all_passed
    
    def build_package(self, skip_build: bool = False) -> bool:
        """Build the package for deployment."""
        if skip_build:
            self.log("Skipping package build")
            return True
        
        self.log("Building package...")
        
        # Clean previous builds
        exit_code, _, _ = self.run_command([
            sys.executable, "scripts/dev.py", "clean"
        ])
        
        # Build package
        exit_code, _, _ = self.run_command([
            sys.executable, "scripts/dev.py", "build"
        ])
        
        if exit_code == 0:
            self.log("Package built successfully", "SUCCESS")
            return True
        else:
            self.log("Package build failed", "ERROR")
            return False
    
    def deploy_to_pypi(self, repository: str = "pypi") -> bool:
        """Deploy package to PyPI."""
        self.log(f"Deploying to {repository}...")
        
        # Check if twine is available
        exit_code, _, _ = self.run_command([
            sys.executable, "-c", "import twine"
        ], check=False, capture_output=True)
        
        if exit_code != 0:
            self.log("Twine not available, installing...", "WARNING")
            exit_code, _, _ = self.run_command([
                sys.executable, "-m", "pip", "install", "twine"
            ])
            
            if exit_code != 0:
                self.log("Failed to install twine", "ERROR")
                return False
        
        # Upload to PyPI
        cmd = [sys.executable, "-m", "twine", "upload"]
        
        if repository != "pypi":
            cmd.extend(["--repository", repository])
        
        cmd.append("dist/*")
        
        exit_code, _, _ = self.run_command(cmd)
        
        if exit_code == 0:
            self.log(f"Successfully deployed to {repository}", "SUCCESS")
            return True
        else:
            self.log(f"Failed to deploy to {repository}", "ERROR")
            return False
    
    def deploy_docker(self, environment: str, registry: Optional[str] = None) -> bool:
        """Deploy using Docker."""
        self.log(f"Deploying Docker image for {environment}...")
        
        # Build Docker image
        exit_code, _, _ = self.run_command([
            sys.executable, "scripts/docker-manager.py", "build", 
            "--target", "production"
        ])
        
        if exit_code != 0:
            self.log("Docker build failed", "ERROR")
            return False
        
        # Push to registry if specified
        if registry:
            self.log(f"Pushing to registry: {registry}")
            
            # Tag for registry
            exit_code, _, _ = self.run_command([
                "docker", "tag", "mermaid-render:production",
                f"{registry}/mermaid-render:latest"
            ])
            
            if exit_code != 0:
                self.log("Failed to tag image", "ERROR")
                return False
            
            # Push to registry
            exit_code, _, _ = self.run_command([
                "docker", "push", f"{registry}/mermaid-render:latest"
            ])
            
            if exit_code != 0:
                self.log("Failed to push to registry", "ERROR")
                return False
            
            self.log("Successfully pushed to registry", "SUCCESS")
        
        return True
    
    def run_database_migrations(self, environment: str) -> bool:
        """Run database migrations for the environment."""
        env_config = self.deployment_config["environments"].get(environment, {})
        
        if not env_config.get("auto_migrate", False):
            self.log("Auto-migration disabled for this environment", "INFO")
            return True
        
        self.log("Running database migrations...")
        
        exit_code, _, _ = self.run_command([
            sys.executable, "scripts/db-migrate.py", "migrate"
        ])
        
        if exit_code == 0:
            self.log("Database migrations completed", "SUCCESS")
            return True
        else:
            self.log("Database migrations failed", "ERROR")
            return False
    
    def deploy_environment(self, environment: str, dry_run: bool = False,
                          skip_tests: bool = False, skip_build: bool = False,
                          force: bool = False, version: Optional[str] = None) -> bool:
        """Deploy to a specific environment."""
        if environment not in self.deployment_config["environments"]:
            self.log(f"Unknown environment: {environment}", "ERROR")
            return False
        
        env_config = self.deployment_config["environments"][environment]
        
        self.log(f"Starting deployment to {environment}...")
        
        if dry_run:
            self.log("DRY RUN MODE - No actual deployment will occur", "WARNING")
        
        # Get version
        deploy_version = version or self.get_current_version()
        self.log(f"Deploying version: {deploy_version}")
        
        # Run pre-deployment checks
        if not force:
            checks_passed = self.run_pre_deployment_checks(skip_tests)
            if not checks_passed:
                self.log("Pre-deployment checks failed", "ERROR")
                if not force:
                    return False
        
        if dry_run:
            self.log("Would build package...", "INFO")
            self.log("Would run migrations...", "INFO")
            self.log("Would deploy to environment...", "INFO")
            return True
        
        # Build package
        if not self.build_package(skip_build):
            return False
        
        # Run migrations
        if not self.run_database_migrations(environment):
            if not force:
                return False
        
        # Deploy based on environment
        if environment == "docker":
            success = self.deploy_docker(environment, env_config.get("registry"))
        elif environment in ["staging", "production"]:
            # For staging/production, deploy to PyPI
            repository = "testpypi" if environment == "staging" else "pypi"
            success = self.deploy_to_pypi(repository)
        else:
            # Development deployment
            self.log("Development deployment completed", "SUCCESS")
            success = True
        
        if success:
            self.log(f"Deployment to {environment} completed successfully!", "SUCCESS")
            
            # Log deployment info
            deployment_info = {
                "environment": environment,
                "version": deploy_version,
                "timestamp": time.time(),
                "url": env_config.get("url")
            }
            
            self.log(f"Deployment info: {json.dumps(deployment_info, indent=2)}")
        else:
            self.log(f"Deployment to {environment} failed", "ERROR")
        
        return success


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deployment automation for Mermaid Render",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("environment", choices=[
        "staging", "production", "dev", "docker"
    ], help="Deployment environment")
    
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be deployed without executing")
    
    parser.add_argument("--skip-tests", action="store_true",
                       help="Skip running tests before deployment")
    
    parser.add_argument("--skip-build", action="store_true",
                       help="Skip building the package")
    
    parser.add_argument("--force", action="store_true",
                       help="Force deployment even if checks fail")
    
    parser.add_argument("--version", "-v",
                       help="Specify version to deploy")
    
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    manager = DeploymentManager(verbose=args.verbose)
    
    success = manager.deploy_environment(
        environment=args.environment,
        dry_run=args.dry_run,
        skip_tests=args.skip_tests,
        skip_build=args.skip_build,
        force=args.force,
        version=args.version
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
