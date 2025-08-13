#!/usr/bin/env python3
"""
Quality Assurance check script for Mermaid Render.

This script runs comprehensive quality checks including:
- Code formatting and linting
- Type checking
- Security scanning
- Dependency vulnerability checks
- Test coverage analysis
- Documentation validation
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, cast

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class QAChecker:
    """Quality assurance checker for the project."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: Dict[str, Dict] = {}
        self.project_root = project_root
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with optional verbosity control."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            prefix = {
                "INFO": "ℹ️",
                "SUCCESS": "✅",
                "WARNING": "⚠️",
                "ERROR": "❌"
            }.get(level, "📝")
            print(f"{prefix} {message}")
    
    def run_command(self, cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        self.log(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                cwd=self.project_root
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            self.log(f"Command failed: {e}", "ERROR")
            return 1, "", str(e)
    
    def check_code_formatting(self) -> Dict:
        """Check code formatting with black."""
        self.log("Checking code formatting with black...")
        
        exit_code, stdout, stderr = self.run_command([
            sys.executable, "-m", "black", "--check", "--diff", 
            "mermaid_render/", "tests/"
        ])
        
        result = {
            "passed": exit_code == 0,
            "exit_code": exit_code,
            "output": stdout,
            "errors": stderr
        }
        
        if result["passed"]:
            self.log("Code formatting check passed", "SUCCESS")
        else:
            self.log("Code formatting check failed", "ERROR")
        
        return result
    
    def check_linting(self) -> Dict:
        """Check code linting with ruff."""
        self.log("Checking code linting with ruff...")
        
        exit_code, stdout, stderr = self.run_command([
            sys.executable, "-m", "ruff", "check", 
            "mermaid_render/", "tests/"
        ])
        
        result = {
            "passed": exit_code == 0,
            "exit_code": exit_code,
            "output": stdout,
            "errors": stderr
        }
        
        if result["passed"]:
            self.log("Linting check passed", "SUCCESS")
        else:
            self.log("Linting check failed", "ERROR")
        
        return result
    
    def check_type_hints(self) -> Dict:
        """Check type hints with mypy."""
        self.log("Checking type hints with mypy...")
        
        exit_code, stdout, stderr = self.run_command([
            sys.executable, "-m", "mypy", "mermaid_render/"
        ])
        
        result = {
            "passed": exit_code == 0,
            "exit_code": exit_code,
            "output": stdout,
            "errors": stderr
        }
        
        if result["passed"]:
            self.log("Type checking passed", "SUCCESS")
        else:
            self.log("Type checking failed", "ERROR")
        
        return result
    
    def check_security(self) -> Dict:
        """Check security with bandit."""
        self.log("Checking security with bandit...")
        
        exit_code, stdout, stderr = self.run_command([
            sys.executable, "-m", "bandit", "-r", "mermaid_render/",
            "-f", "json", "-o", "bandit-report.json"
        ])
        
        # Parse bandit results
        bandit_report = {}
        try:
            if Path("bandit-report.json").exists():
                with open("bandit-report.json") as f:
                    bandit_report = json.load(f)
        except Exception as e:
            self.log(f"Failed to parse bandit report: {e}", "WARNING")
        
        result = {
            "passed": exit_code == 0,
            "exit_code": exit_code,
            "output": stdout,
            "errors": stderr,
            "report": bandit_report
        }
        
        if result["passed"]:
            self.log("Security check passed", "SUCCESS")
        else:
            self.log("Security check found issues", "WARNING")
        
        return result
    
    def check_dependencies(self) -> Dict:
        """Check dependency vulnerabilities with safety."""
        self.log("Checking dependency vulnerabilities with safety...")
        
        exit_code, stdout, stderr = self.run_command([
            sys.executable, "-m", "safety", "check", "--json"
        ])
        
        # Parse safety results
        safety_report = {}
        try:
            if stdout:
                safety_report = json.loads(stdout)
        except Exception as e:
            self.log(f"Failed to parse safety report: {e}", "WARNING")
        
        result = {
            "passed": exit_code == 0,
            "exit_code": exit_code,
            "output": stdout,
            "errors": stderr,
            "report": safety_report
        }
        
        if result["passed"]:
            self.log("Dependency security check passed", "SUCCESS")
        else:
            self.log("Dependency security check found vulnerabilities", "WARNING")
        
        return result
    
    def check_tests(self) -> Dict:
        """Run tests with coverage."""
        self.log("Running tests with coverage...")
        
        exit_code, stdout, stderr = self.run_command([
            sys.executable, "-m", "pytest", "tests/",
            "--cov=mermaid_render",
            "--cov-report=json",
            "--cov-report=term-missing",
            "-v"
        ])
        
        # Parse coverage results
        coverage_report = {}
        try:
            if Path("coverage.json").exists():
                with open("coverage.json") as f:
                    coverage_report = json.load(f)
        except Exception as e:
            self.log(f"Failed to parse coverage report: {e}", "WARNING")
        
        result = {
            "passed": exit_code == 0,
            "exit_code": exit_code,
            "output": stdout,
            "errors": stderr,
            "coverage": coverage_report
        }
        
        if result["passed"]:
            self.log("Tests passed", "SUCCESS")
        else:
            self.log("Tests failed", "ERROR")
        
        return result
    
    def check_package_structure(self) -> Dict:
        """Validate package structure."""
        self.log("Validating package structure...")
        
        # Run our package validation script
        exit_code, stdout, stderr = self.run_command([
            sys.executable, "scripts/validate-package.py"
        ])
        
        result = {
            "passed": exit_code == 0,
            "exit_code": exit_code,
            "output": stdout,
            "errors": stderr
        }
        
        if result["passed"]:
            self.log("Package structure validation passed", "SUCCESS")
        else:
            self.log("Package structure validation failed", "ERROR")
        
        return result
    
    def run_all_checks(self) -> Dict:
        """Run all quality assurance checks."""
        self.log("Starting comprehensive QA checks...")
        
        checks = {
            "formatting": self.check_code_formatting,
            "linting": self.check_linting,
            "type_hints": self.check_type_hints,
            "security": self.check_security,
            "dependencies": self.check_dependencies,
            "tests": self.check_tests,
            "package_structure": self.check_package_structure,
        }
        
        results = {}
        passed_count = 0
        
        for check_name, check_func in checks.items():
            self.log(f"\n{'='*50}")
            self.log(f"Running {check_name} check...")
            
            try:
                result = check_func()
                results[check_name] = result
                if result["passed"]:
                    passed_count += 1
            except Exception as e:
                self.log(f"Check {check_name} failed with exception: {e}", "ERROR")
                results[check_name] = {
                    "passed": False,
                    "error": str(e)
                }
        
        # Summary
        total_checks = len(checks)
        self.log(f"\n{'='*50}")
        self.log(f"QA Summary: {passed_count}/{total_checks} checks passed")
        
        if passed_count == total_checks:
            self.log("All QA checks passed! 🎉", "SUCCESS")
        else:
            failed_count = total_checks - passed_count
            self.log(f"{failed_count} QA checks failed", "ERROR")
        
        return {
            "summary": {
                "total": total_checks,
                "passed": passed_count,
                "failed": total_checks - passed_count,
                "success_rate": (passed_count / total_checks) * 100
            },
            "results": results
        }
    
    def generate_report(self, results: Dict, output_file: Optional[str] = None) -> Dict:
        """Generate a detailed QA report."""
        report = {
            "timestamp": subprocess.check_output(["date", "-u"]).decode().strip(),
            "project": "mermaid-render",
            "qa_results": results
        }
        
        if output_file:
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2)
            self.log(f"QA report saved to {output_file}")
        
        return report


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run QA checks for Mermaid Render")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--report", "-r", help="Save report to file")
    parser.add_argument("--check", choices=[
        "formatting", "linting", "type_hints", "security", 
        "dependencies", "tests", "package_structure"
    ], help="Run specific check only")
    
    args = parser.parse_args()
    
    checker = QAChecker(verbose=args.verbose)
    
    if args.check:
        # Run specific check
        check_methods = {
            "formatting": checker.check_code_formatting,
            "linting": checker.check_linting,
            "type_hints": checker.check_type_hints,
            "security": checker.check_security,
            "dependencies": checker.check_dependencies,
            "tests": checker.check_tests,
            "package_structure": checker.check_package_structure,
        }
        
        result = check_methods[args.check]()
        results = {"results": {args.check: result}}
    else:
        # Run all checks
        results = checker.run_all_checks()
    
    # Generate report if requested
    if args.report:
        checker.generate_report(results, args.report)
    
    # Exit with appropriate code
    if args.check:
        sys.exit(0 if result["passed"] else 1)
    else:
        failed_count = cast(int, results["summary"]["failed"])
        sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()
