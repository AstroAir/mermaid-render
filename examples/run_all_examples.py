#!/usr/bin/env python3
"""
Comprehensive example runner for Mermaid Render.

This script runs all available examples and generates a complete showcase
of the library's capabilities.
"""

import sys
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Any


def create_output_dir():
    """Create main output directory for all examples."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def run_example_script(script_path: Path, description: str) -> Dict[str, Any]:
    """Run an example script and return results."""
    print(f"🚀 Running: {description}")
    print(f"   Script: {script_path}")
    
    start_time = time.time()
    
    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"   ✅ Completed successfully in {execution_time:.2f}s")
            return {
                "script": str(script_path),
                "description": description,
                "success": True,
                "execution_time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        else:
            print(f"   ❌ Failed with exit code {result.returncode}")
            print(f"   Error: {result.stderr}")
            return {
                "script": str(script_path),
                "description": description,
                "success": False,
                "execution_time": execution_time,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
    
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timed out after 5 minutes")
        return {
            "script": str(script_path),
            "description": description,
            "success": False,
            "execution_time": 300,
            "error": "Timeout"
        }
    
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"   💥 Exception: {e}")
        return {
            "script": str(script_path),
            "description": description,
            "success": False,
            "execution_time": execution_time,
            "error": str(e)
        }


def generate_summary_report(results: List[Dict[str, Any]], output_dir: Path):
    """Generate a comprehensive summary report."""
    print("\n📊 Generating summary report...")
    
    # Calculate statistics
    total_examples = len(results)
    successful_examples = sum(1 for r in results if r['success'])
    failed_examples = total_examples - successful_examples
    total_time = sum(r['execution_time'] for r in results)
    
    # Create summary
    summary = {
        "execution_summary": {
            "total_examples": total_examples,
            "successful": successful_examples,
            "failed": failed_examples,
            "success_rate": f"{(successful_examples / total_examples * 100):.1f}%" if total_examples > 0 else "0%",
            "total_execution_time": f"{total_time:.2f}s",
            "average_execution_time": f"{(total_time / total_examples):.2f}s" if total_examples > 0 else "0s"
        },
        "example_results": results,
        "generated_files": {
            "basic_usage": list((output_dir / "basic").glob("*")) if (output_dir / "basic").exists() else [],
            "advanced_usage": list((output_dir / "advanced").glob("*")) if (output_dir / "advanced").exists() else [],
            "diagram_types": list((output_dir / "diagram_types").glob("*")) if (output_dir / "diagram_types").exists() else [],
            "ai_features": list((output_dir / "ai_features").glob("*")) if (output_dir / "ai_features").exists() else [],
            "templates": list((output_dir / "templates").glob("*")) if (output_dir / "templates").exists() else [],
            "integration": list((output_dir / "integration").glob("*")) if (output_dir / "integration").exists() else [],
            "real_world": list((output_dir / "real_world").glob("*")) if (output_dir / "real_world").exists() else [],
            "performance": list((output_dir / "performance").glob("*")) if (output_dir / "performance").exists() else [],
            "testing": list((output_dir / "testing").glob("*")) if (output_dir / "testing").exists() else [],
            "interactive": list((output_dir / "interactive").glob("*")) if (output_dir / "interactive").exists() else []
        }
    }
    
    # Convert Path objects to strings for JSON serialization
    for category in summary["generated_files"]:
        summary["generated_files"][category] = [str(p) for p in summary["generated_files"][category]]
    
    # Save summary report
    import json
    summary_path = output_dir / "example_execution_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"📁 Summary report saved to {summary_path}")
    
    # Create HTML report
    html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mermaid Render Examples - Execution Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat {{ background: white; padding: 15px; border-radius: 5px; text-align: center; flex: 1; }}
        .stat h3 {{ margin: 0; color: #333; }}
        .stat p {{ margin: 5px 0 0 0; font-size: 24px; font-weight: bold; }}
        .success {{ color: #28a745; }}
        .failure {{ color: #dc3545; }}
        .example {{ background: white; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }}
        .example.success {{ border-left-color: #28a745; }}
        .example.failure {{ border-left-color: #dc3545; }}
        .example h4 {{ margin: 0 0 10px 0; }}
        .example p {{ margin: 5px 0; color: #666; }}
        .files {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; }}
        .file-category {{ margin: 10px 0; }}
        .file-list {{ margin-left: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Mermaid Render Examples - Execution Report</h1>
        
        <div class="summary">
            <h2>Execution Summary</h2>
            <div class="stats">
                <div class="stat">
                    <h3>Total Examples</h3>
                    <p>{summary['execution_summary']['total_examples']}</p>
                </div>
                <div class="stat">
                    <h3>Successful</h3>
                    <p class="success">{summary['execution_summary']['successful']}</p>
                </div>
                <div class="stat">
                    <h3>Failed</h3>
                    <p class="failure">{summary['execution_summary']['failed']}</p>
                </div>
                <div class="stat">
                    <h3>Success Rate</h3>
                    <p>{summary['execution_summary']['success_rate']}</p>
                </div>
                <div class="stat">
                    <h3>Total Time</h3>
                    <p>{summary['execution_summary']['total_execution_time']}</p>
                </div>
            </div>
        </div>
        
        <h2>Example Results</h2>
        <div class="examples">
"""
    
    for result in results:
        status_class = "success" if result['success'] else "failure"
        status_icon = "✅" if result['success'] else "❌"
        
        html_report += f"""
            <div class="example {status_class}">
                <h4>{status_icon} {result['description']}</h4>
                <p><strong>Script:</strong> {result['script']}</p>
                <p><strong>Execution Time:</strong> {result['execution_time']:.2f}s</p>
"""
        
        if not result['success']:
            error_info = result.get('error', result.get('stderr', 'Unknown error'))
            html_report += f"<p><strong>Error:</strong> {error_info}</p>"
        
        html_report += "</div>"
    
    html_report += """
        </div>
        
        <div class="files">
            <h2>Generated Files</h2>
"""
    
    for category, files in summary["generated_files"].items():
        if files:
            html_report += f"""
            <div class="file-category">
                <h3>{category.replace('_', ' ').title()}</h3>
                <div class="file-list">
"""
            for file_path in files:
                html_report += f"<p>📁 {file_path}</p>"
            
            html_report += "</div></div>"
    
    html_report += """
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML report
    html_path = output_dir / "example_execution_report.html"
    with open(html_path, 'w') as f:
        f.write(html_report)
    
    print(f"📁 HTML report saved to {html_path}")
    
    return summary


def main():
    """Run all examples and generate comprehensive report."""
    print("=== Mermaid Render Complete Examples Showcase ===\n")
    
    # Create output directory
    output_dir = create_output_dir()
    print(f"Output directory: {output_dir.absolute()}\n")
    
    # Define all example scripts
    examples_dir = Path(__file__).parent
    example_scripts = [
        {
            "script": examples_dir / "basic_usage.py",
            "description": "Basic Usage Examples - Fundamental features and simple diagrams"
        },
        {
            "script": examples_dir / "advanced_usage.py",
            "description": "Advanced Usage Examples - Complex features and configurations"
        },
        {
            "script": examples_dir / "diagram_types_showcase.py",
            "description": "Diagram Types Showcase - All supported diagram types with practical examples"
        },
        {
            "script": examples_dir / "ai_features_showcase.py",
            "description": "AI Features Showcase - Natural language generation and optimization"
        },
        {
            "script": examples_dir / "template_system_showcase.py",
            "description": "Template System Showcase - Template usage and custom generators"
        },
        {
            "script": examples_dir / "integration_examples.py",
            "description": "Integration Examples - Web frameworks, CLI, and CI/CD patterns"
        },
        {
            "script": examples_dir / "real_world_use_cases.py",
            "description": "Real-World Use Cases - Practical applications and documentation"
        },
        {
            "script": examples_dir / "performance_caching_showcase.py",
            "description": "Performance & Caching - Optimization strategies and monitoring"
        },
        {
            "script": examples_dir / "testing_validation_showcase.py",
            "description": "Testing & Validation - Testing patterns and error handling"
        },
        {
            "script": examples_dir / "interactive_collaboration_showcase.py",
            "description": "Interactive & Collaboration - Real-time editing and version control"
        }
    ]
    
    # Filter to only existing scripts
    available_scripts = []
    for example in example_scripts:
        if example["script"].exists():
            available_scripts.append(example)
        else:
            print(f"⚠️  Script not found: {example['script']}")
    
    print(f"Found {len(available_scripts)} example scripts to run\n")
    
    # Run all examples
    results = []
    start_time = time.time()
    
    for i, example in enumerate(available_scripts, 1):
        print(f"[{i}/{len(available_scripts)}] ", end="")
        result = run_example_script(example["script"], example["description"])
        results.append(result)
        print()  # Add spacing between examples
    
    total_time = time.time() - start_time
    
    # Generate summary report
    summary = generate_summary_report(results, output_dir)
    
    # Print final summary
    print(f"\n🎉 All examples completed!")
    print(f"📊 Summary:")
    print(f"   Total examples: {summary['execution_summary']['total_examples']}")
    print(f"   Successful: {summary['execution_summary']['successful']}")
    print(f"   Failed: {summary['execution_summary']['failed']}")
    print(f"   Success rate: {summary['execution_summary']['success_rate']}")
    print(f"   Total time: {total_time:.2f}s")
    print(f"\n📁 Check the {output_dir} directory for all generated files and reports.")
    print(f"🌐 Open {output_dir}/example_execution_report.html for a detailed report.")
    
    # Return appropriate exit code
    failed_count = summary['execution_summary']['failed']
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
