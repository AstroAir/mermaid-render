#!/usr/bin/env python3
"""
Docker Management Script for Mermaid Render

This script provides comprehensive Docker operations for development,
testing, and deployment workflows.

Usage:
    python scripts/docker-manager.py <command> [options]

Commands:
    build       - Build Docker images
    run         - Run containers
    test        - Run tests in containers
    deploy      - Deploy to production
    clean       - Clean up Docker resources
    logs        - View container logs
    shell       - Open shell in container
    compose     - Docker Compose operations
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DockerManager:
    """Manages Docker operations for the project."""
    
    def __init__(self, project_root: Optional[Path] = None, verbose: bool = False):
        self.project_root = project_root or Path(__file__).parent.parent
        self.verbose = verbose
        self.compose_file = self.project_root / "docker-compose.yml"
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with level indicator."""
        if self.verbose or level in ["ERROR", "WARNING"]:
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
    
    def check_docker_available(self) -> bool:
        """Check if Docker is available."""
        exit_code, _, _ = self.run_command(["docker", "--version"], 
                                         check=False, capture_output=True)
        return exit_code == 0
    
    def check_compose_available(self) -> bool:
        """Check if Docker Compose is available."""
        # Try docker compose (new syntax)
        exit_code, _, _ = self.run_command(["docker", "compose", "version"], 
                                         check=False, capture_output=True)
        if exit_code == 0:
            return True
        
        # Try docker-compose (legacy)
        exit_code, _, _ = self.run_command(["docker-compose", "--version"], 
                                         check=False, capture_output=True)
        return exit_code == 0
    
    def get_compose_command(self) -> List[str]:
        """Get the appropriate Docker Compose command."""
        # Try docker compose first (new syntax)
        exit_code, _, _ = self.run_command(["docker", "compose", "version"], 
                                         check=False, capture_output=True)
        if exit_code == 0:
            return ["docker", "compose"]
        else:
            return ["docker-compose"]
    
    def build_images(self, target: str = "development", no_cache: bool = False) -> int:
        """Build Docker images."""
        self.log(f"Building Docker image for target: {target}")
        
        if not self.check_docker_available():
            self.log("Docker is not available", "ERROR")
            return 1
        
        cmd = ["docker", "build"]
        
        if no_cache:
            cmd.append("--no-cache")
        
        cmd.extend([
            "--target", target,
            "-t", f"diagramaid:{target}",
            "."
        ])
        
        exit_code, _, _ = self.run_command(cmd)
        
        if exit_code == 0:
            self.log(f"Successfully built image: diagramaid:{target}", "SUCCESS")
        else:
            self.log("Failed to build Docker image", "ERROR")
        
        return exit_code
    
    def run_container(self, target: str = "development", 
                     interactive: bool = True, ports: Optional[List[str]] = None) -> int:
        """Run a Docker container."""
        self.log(f"Running container: diagramaid:{target}")
        
        cmd = ["docker", "run", "--rm"]
        
        if interactive:
            cmd.extend(["-it"])
        
        # Add port mappings
        if ports:
            for port in ports:
                cmd.extend(["-p", port])
        elif target == "development":
            cmd.extend(["-p", "8000:8000", "-p", "8080:8080"])
        elif target == "webserver":
            cmd.extend(["-p", "80:8000"])
        
        # Mount source code for development
        if target == "development":
            cmd.extend(["-v", f"{self.project_root}:/app"])
        
        cmd.append(f"diagramaid:{target}")
        
        exit_code, _, _ = self.run_command(cmd)
        return exit_code
    
    def run_tests_in_container(self) -> int:
        """Run tests in a Docker container."""
        self.log("Running tests in Docker container")
        
        # Build test image first
        exit_code = self.build_images("testing")
        if exit_code != 0:
            return exit_code
        
        cmd = [
            "docker", "run", "--rm",
            "diagramaid:testing"
        ]
        
        exit_code, _, _ = self.run_command(cmd)
        
        if exit_code == 0:
            self.log("Tests passed in container", "SUCCESS")
        else:
            self.log("Tests failed in container", "ERROR")
        
        return exit_code
    
    def open_shell(self, target: str = "development") -> int:
        """Open a shell in the container."""
        self.log(f"Opening shell in container: diagramaid:{target}")
        
        cmd = [
            "docker", "run", "--rm", "-it",
            "-v", f"{self.project_root}:/app",
            f"diagramaid:{target}",
            "/bin/bash"
        ]
        
        exit_code, _, _ = self.run_command(cmd)
        return exit_code
    
    def view_logs(self, service: str = "dev") -> int:
        """View container logs."""
        if not self.compose_file.exists():
            self.log("docker-compose.yml not found", "ERROR")
            return 1
        
        compose_cmd = self.get_compose_command()
        cmd = compose_cmd + ["logs", "-f", service]
        
        exit_code, _, _ = self.run_command(cmd)
        return exit_code
    
    def compose_operation(self, operation: str, services: Optional[List[str]] = None) -> int:
        """Perform Docker Compose operations."""
        if not self.compose_file.exists():
            self.log("docker-compose.yml not found", "ERROR")
            return 1
        
        if not self.check_compose_available():
            self.log("Docker Compose is not available", "ERROR")
            return 1
        
        compose_cmd = self.get_compose_command()
        cmd = compose_cmd + [operation]
        
        if services:
            cmd.extend(services)
        
        self.log(f"Running Docker Compose {operation}")
        exit_code, _, _ = self.run_command(cmd)
        
        if exit_code == 0:
            self.log(f"Docker Compose {operation} completed successfully", "SUCCESS")
        else:
            self.log(f"Docker Compose {operation} failed", "ERROR")
        
        return exit_code
    
    def clean_resources(self, all_resources: bool = False) -> int:
        """Clean up Docker resources."""
        self.log("Cleaning Docker resources")
        
        commands = [
            ["docker", "container", "prune", "-f"],
            ["docker", "image", "prune", "-f"],
            ["docker", "network", "prune", "-f"],
            ["docker", "volume", "prune", "-f"]
        ]
        
        if all_resources:
            commands.append(["docker", "system", "prune", "-a", "-f"])
        
        total_exit_code = 0
        for cmd in commands:
            exit_code, _, _ = self.run_command(cmd, check=False)
            total_exit_code |= exit_code
        
        if total_exit_code == 0:
            self.log("Docker cleanup completed successfully", "SUCCESS")
        else:
            self.log("Docker cleanup completed with some errors", "WARNING")
        
        return total_exit_code
    
    def deploy_production(self, registry: Optional[str] = None) -> int:
        """Deploy to production."""
        self.log("Deploying to production")
        
        # Build production image
        exit_code = self.build_images("production")
        if exit_code != 0:
            return exit_code
        
        # Tag for registry if provided
        if registry:
            tag_cmd = [
                "docker", "tag", "diagramaid:production",
                f"{registry}/diagramaid:latest"
            ]
            exit_code, _, _ = self.run_command(tag_cmd)
            if exit_code != 0:
                return exit_code
            
            # Push to registry
            push_cmd = ["docker", "push", f"{registry}/diagramaid:latest"]
            exit_code, _, _ = self.run_command(push_cmd)
            if exit_code != 0:
                return exit_code
            
            self.log(f"Successfully pushed to registry: {registry}", "SUCCESS")
        
        self.log("Production deployment completed", "SUCCESS")
        return 0
    
    def get_container_status(self) -> Dict:
        """Get status of running containers."""
        cmd = ["docker", "ps", "--format", "json"]
        exit_code, stdout, _ = self.run_command(cmd, capture_output=True)
        
        if exit_code != 0:
            return {}
        
        containers = []
        for line in stdout.strip().split('\n'):
            if line:
                try:
                    containers.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return {"containers": containers, "count": len(containers)}


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Docker management for Mermaid Render",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("command", choices=[
        "build", "run", "test", "deploy", "clean", "logs", "shell", "compose", "status"
    ], help="Docker command to run")
    
    parser.add_argument("--target", "-t", default="development",
                       choices=["development", "testing", "production", "webserver"],
                       help="Docker build target")
    
    parser.add_argument("--no-cache", action="store_true",
                       help="Build without cache")
    
    parser.add_argument("--registry", "-r",
                       help="Docker registry for deployment")
    
    parser.add_argument("--service", "-s",
                       help="Service name for compose operations")
    
    parser.add_argument("--ports", "-p", nargs="*",
                       help="Port mappings (e.g., 8000:8000)")
    
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    
    parser.add_argument("--all", action="store_true",
                       help="Apply to all resources (for clean command)")
    
    args = parser.parse_args()
    
    manager = DockerManager(verbose=args.verbose)
    
    if args.command == "build":
        exit_code = manager.build_images(args.target, args.no_cache)
    elif args.command == "run":
        exit_code = manager.run_container(args.target, ports=args.ports)
    elif args.command == "test":
        exit_code = manager.run_tests_in_container()
    elif args.command == "deploy":
        exit_code = manager.deploy_production(args.registry)
    elif args.command == "clean":
        exit_code = manager.clean_resources(args.all)
    elif args.command == "logs":
        service = args.service or "dev"
        exit_code = manager.view_logs(service)
    elif args.command == "shell":
        exit_code = manager.open_shell(args.target)
    elif args.command == "compose":
        operation = args.service or "up"
        exit_code = manager.compose_operation(operation)
    elif args.command == "status":
        status = manager.get_container_status()
        print(f"Running containers: {status.get('count', 0)}")
        for container in status.get('containers', []):
            print(f"  - {container.get('Names', 'Unknown')}: {container.get('Status', 'Unknown')}")
        exit_code = 0
    else:
        parser.print_help()
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
