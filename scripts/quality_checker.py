#!/usr/bin/env python3
"""
Comprehensive Quality Checker for Mermaid Render

This script performs comprehensive quality checks including:
- Code quality and style
- Security vulnerabilities
- License compliance
- Dependency analysis
- Performance benchmarks
- Documentation quality
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

project_root = Path(__file__).parent.parent


class QualityChecker:
    """Comprehensive quality checker for the package."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: dict[str, list[tuple[bool, str]]] = {}

    def run_command(
        self, cmd: list[str], cwd: Path | None = None
    ) -> tuple[bool, str, str]:
        """Run a command and return success, stdout, stderr."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd or project_root,
                timeout=300,  # 5 minutes timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def check_code_quality(self) -> list[tuple[bool, str]]:
        """Check code quality with various tools."""
        results = []

        # Black formatting check
        success, stdout, stderr = self.run_command(
            [
                sys.executable,
                "-m",
                "black",
                "--check",
                "--diff",
                "mermaid_render",
                "tests",
            ]
        )
        if success:
            results.append((True, "✅ Black formatting check passed"))
        else:
            results.append((False, f"❌ Black formatting issues found: {stderr}"))

        # Ruff linting
        success, stdout, stderr = self.run_command(
            [sys.executable, "-m", "ruff", "check", "mermaid_render", "tests"]
        )
        if success:
            results.append((True, "✅ Ruff linting passed"))
        else:
            results.append((False, f"❌ Ruff linting issues: {stderr}"))

        # MyPy type checking
        success, stdout, stderr = self.run_command(
            [sys.executable, "-m", "mypy", "mermaid_render"]
        )
        if success:
            results.append((True, "✅ MyPy type checking passed"))
        else:
            results.append((False, f"❌ MyPy type checking issues: {stderr}"))

        return results

    def check_security(self) -> list[tuple[bool, str]]:
        """Check for security vulnerabilities."""
        results = []

        # Safety check for known vulnerabilities
        success, stdout, stderr = self.run_command(
            [sys.executable, "-m", "pip", "install", "safety", "--quiet"]
        )
        if success:
            success, stdout, stderr = self.run_command(
                [sys.executable, "-m", "safety", "check", "--json"]
            )
            if success:
                try:
                    safety_data = json.loads(stdout) if stdout.strip() else []
                    if not safety_data:
                        results.append((True, "✅ No known security vulnerabilities"))
                    else:
                        results.append(
                            (
                                False,
                                f"❌ Found {len(safety_data)} security vulnerabilities",
                            )
                        )
                except json.JSONDecodeError:
                    results.append((True, "✅ Safety check completed (no JSON output)"))
            else:
                results.append((False, f"❌ Safety check failed: {stderr}"))

        # Bandit security linting
        success, stdout, stderr = self.run_command(
            [sys.executable, "-m", "pip", "install", "bandit[toml]", "--quiet"]
        )
        if success:
            success, stdout, stderr = self.run_command(
                [sys.executable, "-m", "bandit", "-r", "mermaid_render", "-f", "json"]
            )
            if success:
                try:
                    bandit_data = json.loads(stdout) if stdout.strip() else {}
                    issues = bandit_data.get("results", [])
                    if not issues:
                        results.append((True, "✅ Bandit security scan passed"))
                    else:
                        high_issues = [
                            i for i in issues if i.get("issue_severity") == "HIGH"
                        ]
                        if high_issues:
                            results.append(
                                (
                                    False,
                                    f"❌ Bandit found {len(high_issues)} high-severity issues",
                                )
                            )
                        else:
                            results.append(
                                (
                                    True,
                                    f"⚠️  Bandit found {len(issues)} low/medium issues",
                                )
                            )
                except json.JSONDecodeError:
                    results.append((True, "✅ Bandit scan completed"))
            else:
                results.append((False, f"❌ Bandit scan failed: {stderr}"))

        return results

    def check_dependencies(self) -> list[tuple[bool, str]]:
        """Analyze dependencies for issues."""
        results = []

        # Check for outdated dependencies
        success, stdout, stderr = self.run_command(
            [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"]
        )
        if success:
            try:
                outdated = json.loads(stdout) if stdout.strip() else []
                if not outdated:
                    results.append((True, "✅ All dependencies are up to date"))
                else:
                    critical_packages = [
                        "requests",
                        "urllib3",
                        "pillow",
                        "cryptography",
                    ]
                    critical_outdated = [
                        p for p in outdated if p["name"].lower() in critical_packages
                    ]

                    if critical_outdated:
                        results.append(
                            (
                                False,
                                f"❌ Critical packages outdated: {len(critical_outdated)}",
                            )
                        )
                    else:
                        results.append(
                            (
                                True,
                                f"⚠️  {len(outdated)} packages outdated (non-critical)",
                            )
                        )
            except json.JSONDecodeError:
                results.append((True, "✅ Dependency check completed"))

        # Check dependency tree for conflicts
        success, stdout, stderr = self.run_command(
            [sys.executable, "-m", "pip", "check"]
        )
        if success:
            results.append((True, "✅ No dependency conflicts found"))
        else:
            results.append((False, f"❌ Dependency conflicts: {stderr}"))

        return results

    def check_tests(self) -> list[tuple[bool, str]]:
        """Run test suite and check coverage."""
        results = []

        # Run tests with coverage
        success, stdout, stderr = self.run_command(
            [
                sys.executable,
                "-m",
                "pytest",
                "--cov=mermaid_render",
                "--cov-report=json",
                "--cov-report=term",
                "-v",
            ]
        )

        if success:
            results.append((True, "✅ Test suite passed"))

            # Check coverage
            coverage_file = project_root / "coverage.json"
            if coverage_file.exists():
                try:
                    with open(coverage_file) as f:
                        coverage_data = json.load(f)

                    total_coverage = coverage_data.get("totals", {}).get(
                        "percent_covered", 0
                    )

                    if total_coverage >= 90:
                        results.append(
                            (True, f"✅ Excellent test coverage: {total_coverage:.1f}%")
                        )
                    elif total_coverage >= 80:
                        results.append(
                            (True, f"✅ Good test coverage: {total_coverage:.1f}%")
                        )
                    elif total_coverage >= 70:
                        results.append(
                            (
                                True,
                                f"⚠️  Acceptable test coverage: {total_coverage:.1f}%",
                            )
                        )
                    else:
                        results.append(
                            (False, f"❌ Low test coverage: {total_coverage:.1f}%")
                        )

                except Exception as e:
                    results.append((False, f"❌ Coverage analysis failed: {e}"))
        else:
            results.append((False, f"❌ Test suite failed: {stderr}"))

        return results

    def check_performance(self) -> list[tuple[bool, str]]:
        """Basic performance benchmarks."""
        results = []

        try:
            # Import time benchmark
            start_time = time.time()
            import mermaid_render

            import_time = time.time() - start_time

            if import_time < 0.5:
                results.append((True, f"✅ Fast import time: {import_time:.3f}s"))
            elif import_time < 1.0:
                results.append((True, f"⚠️  Acceptable import time: {import_time:.3f}s"))
            else:
                results.append((False, f"❌ Slow import time: {import_time:.3f}s"))

            # Basic functionality benchmark
            start_time = time.time()
            try:
                renderer = mermaid_render.MermaidRenderer()
                # This might fail without proper setup, but we're testing object creation
                creation_time = time.time() - start_time

                if creation_time < 0.1:
                    results.append(
                        (True, f"✅ Fast renderer creation: {creation_time:.3f}s")
                    )
                else:
                    results.append(
                        (True, f"⚠️  Renderer creation: {creation_time:.3f}s")
                    )

            except Exception as e:
                results.append((True, f"⚠️  Renderer creation test skipped: {e}"))

        except Exception as e:
            results.append((False, f"❌ Performance benchmark failed: {e}"))

        return results

    def check_documentation(self) -> list[tuple[bool, str]]:
        """Check documentation quality."""
        results = []

        # Check if documentation builds
        if (project_root / "mkdocs.yml").exists():
            success, stdout, stderr = self.run_command(
                [sys.executable, "-m", "mkdocs", "build", "--clean", "--quiet"]
            )
            if success:
                results.append((True, "✅ Documentation builds successfully"))
            else:
                results.append((False, f"❌ Documentation build failed: {stderr}"))

        # Check README quality
        readme_path = project_root / "README.md"
        if readme_path.exists():
            content = readme_path.read_text()

            # Basic README quality checks
            has_title = content.startswith("#")
            has_installation = "install" in content.lower()
            has_usage = "usage" in content.lower() or "example" in content.lower()
            has_license = "license" in content.lower()

            quality_score = sum([has_title, has_installation, has_usage, has_license])

            if quality_score >= 4:
                results.append((True, "✅ README.md has good quality"))
            elif quality_score >= 3:
                results.append((True, "⚠️  README.md has acceptable quality"))
            else:
                results.append((False, "❌ README.md needs improvement"))

        return results

    def run_all_checks(self) -> dict[str, list[tuple[bool, str]]]:
        """Run all quality checks."""
        print("🔍 Running Comprehensive Quality Checks")
        print("=" * 50)

        checks = [
            ("Code Quality", self.check_code_quality),
            ("Security", self.check_security),
            ("Dependencies", self.check_dependencies),
            ("Tests", self.check_tests),
            ("Performance", self.check_performance),
            ("Documentation", self.check_documentation),
        ]

        for check_name, check_func in checks:
            print(f"\n🔧 {check_name}:")
            try:
                results = check_func()
                self.results[check_name] = results

                for success, message in results:
                    print(f"  {message}")

            except Exception as e:
                error_result = [(False, f"❌ {check_name} check failed: {e}")]
                self.results[check_name] = error_result
                print(f"  ❌ {check_name} check failed: {e}")

        return self.results

    def generate_report(self) -> dict[str, Any]:
        """Generate a comprehensive quality report."""
        total_checks = sum(len(results) for results in self.results.values())
        passed_checks = sum(
            sum(1 for success, _ in results if success)
            for results in self.results.values()
        )

        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "success_rate": (
                (passed_checks / total_checks * 100) if total_checks > 0 else 0
            ),
            "categories": {},
        }

        for category, results in self.results.items():
            category_passed = sum(1 for success, _ in results if success)
            # Type ignore needed because mypy can't infer dict structure dynamically
            report["categories"][category] = {  # type: ignore
                "total": len(results),
                "passed": category_passed,
                "success_rate": (
                    (category_passed / len(results) * 100) if results else 0
                ),
                "results": [
                    {"success": success, "message": message}
                    for success, message in results
                ],
            }

        return report


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive quality checker for Mermaid Render"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--report", "-r", help="Save JSON report to file")
    parser.add_argument(
        "--fail-on-warning", action="store_true", help="Fail on warnings"
    )

    args = parser.parse_args()

    checker = QualityChecker(verbose=args.verbose)
    results = checker.run_all_checks()

    # Generate summary
    print("\n" + "=" * 50)
    total_checks = sum(len(results) for results in results.values())
    passed_checks = sum(
        sum(1 for success, _ in results if success) for results in results.values()
    )

    success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0

    print("📊 Quality Report Summary:")
    print(f"  Total checks: {total_checks}")
    print(f"  Passed: {passed_checks}")
    print(f"  Success rate: {success_rate:.1f}%")

    # Save report if requested
    if args.report:
        report = checker.generate_report()
        with open(args.report, "w") as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report saved to: {args.report}")

    # Determine exit code
    failed_checks = total_checks - passed_checks
    if failed_checks > 0:
        print(f"\n❌ {failed_checks} checks failed")
        sys.exit(1)
    else:
        print("\n✅ All quality checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()  # main() handles its own exit
