#!/usr/bin/env python3
"""
Integration examples for Mermaid Render.

This script demonstrates integration patterns with web frameworks,
CLI applications, and CI/CD pipelines.
"""

from pathlib import Path


def create_output_dir() -> Path:
    """Create output directory for examples."""
    output_dir = Path("output/integration")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def flask_integration_example(output_dir: Path) -> None:
    """Demonstrate Flask web framework integration."""
    print("Flask integration example...")

    # Create a Flask app example (as a string since we're demonstrating)
    flask_app_code = '''
from flask import Flask, request, jsonify, render_template_string
from mermaid_render import quick_render, ValidationError, RenderingError
import base64

app = Flask(__name__)

# HTML template for the diagram editor
EDITOR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mermaid Diagram Editor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .editor { display: flex; gap: 20px; }
        .input-panel, .output-panel { flex: 1; }
        textarea { width: 100%; height: 400px; font-family: monospace; }
        .controls { margin: 10px 0; }
        button { padding: 10px 20px; margin-right: 10px; }
        .error { color: red; margin: 10px 0; }
        .success { color: green; margin: 10px 0; }
        #output { border: 1px solid #ccc; min-height: 400px; padding: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Mermaid Diagram Editor</h1>
        <div class="editor">
            <div class="input-panel">
                <h3>Mermaid Code</h3>
                <textarea id="diagram-code" placeholder="Enter your Mermaid diagram code here...">
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
                </textarea>
                <div class="controls">
                    <button onclick="renderDiagram()">Render Diagram</button>
                    <button onclick="downloadSVG()">Download SVG</button>
                    <select id="theme">
                        <option value="default">Default</option>
                        <option value="dark">Dark</option>
                        <option value="forest">Forest</option>
                        <option value="neutral">Neutral</option>
                    </select>
                </div>
                <div id="message"></div>
            </div>
            <div class="output-panel">
                <h3>Preview</h3>
                <div id="output"></div>
            </div>
        </div>
    </div>

    <script>
        async function renderDiagram() {
            const code = document.getElementById('diagram-code').value;
            const theme = document.getElementById('theme').value;
            const messageDiv = document.getElementById('message');
            const outputDiv = document.getElementById('output');

            try {
                const response = await fetch('/api/render', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        diagram: code,
                        format: 'svg',
                        theme: theme
                    })
                });

                const result = await response.json();

                if (result.success) {
                    outputDiv.innerHTML = result.content;
                    messageDiv.innerHTML = '<div class="success">Diagram rendered successfully!</div>';
                } else {
                    messageDiv.innerHTML = `<div class="error">Error: ${result.error}</div>`;
                    if (result.details) {
                        messageDiv.innerHTML += `<div class="error">Details: ${result.details}</div>`;
                    }
                }
            } catch (error) {
                messageDiv.innerHTML = `<div class="error">Network error: ${error.message}</div>`;
            }
        }

        async function downloadSVG() {
            const code = document.getElementById('diagram-code').value;
            const theme = document.getElementById('theme').value;

            try {
                const response = await fetch('/api/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        diagram: code,
                        format: 'svg',
                        theme: theme
                    })
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'diagram.svg';
                    a.click();
                    window.URL.revokeObjectURL(url);
                }
            } catch (error) {
                console.error('Download error:', error);
            }
        }

        // Auto-render on page load
        window.onload = function() {
            renderDiagram();
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(EDITOR_TEMPLATE)

@app.route('/api/render', methods=['POST'])
def render_diagram():
    try:
        data = request.get_json()
        diagram_code = data.get('diagram', '')
        format_type = data.get('format', 'svg')
        theme = data.get('theme', 'default')

        if not diagram_code.strip():
            return jsonify({
                'success': False,
                'error': 'No diagram code provided'
            }), 400

        # Render the diagram
        result = quick_render(
            diagram_code,
            format=format_type,
            theme=theme
        )

        return jsonify({
            'success': True,
            'content': result,
            'format': format_type
        })

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation failed',
            'details': str(e)
        }), 400

    except RenderingError as e:
        return jsonify({
            'success': False,
            'error': 'Rendering failed',
            'details': str(e)
        }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/api/download', methods=['POST'])
def download_diagram():
    try:
        data = request.get_json()
        diagram_code = data.get('diagram', '')
        format_type = data.get('format', 'svg')
        theme = data.get('theme', 'default')

        # Render the diagram
        result = quick_render(
            diagram_code,
            format=format_type,
            theme=theme
        )

        # Return as downloadable file
        from flask import Response
        return Response(
            result,
            mimetype='image/svg+xml' if format_type == 'svg' else 'application/octet-stream',
            headers={
                'Content-Disposition': f'attachment; filename=diagram.{format_type}'
            }
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
'''

    # Save the Flask app example
    flask_file = output_dir / "flask_app.py"
    with open(flask_file, "w") as f:
        f.write(flask_app_code)

    print("✅ Flask integration example created")
    print(f"📁 Saved to {flask_file}")
    print("🚀 Run with: python flask_app.py")
    print("🌐 Open: http://localhost:5000")


def fastapi_integration_example(output_dir: Path) -> None:
    """Demonstrate FastAPI integration."""
    print("FastAPI integration example...")

    fastapi_app_code = '''
from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

from mermaid_render import quick_render, ValidationError, RenderingError

app = FastAPI(title="Mermaid Render API", version="1.0.0")

class DiagramRequest(BaseModel):
    diagram: str
    format: str = "svg"
    theme: Optional[str] = "default"
    width: Optional[int] = None
    height: Optional[int] = None

class DiagramResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    details: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve a simple API documentation page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mermaid Render API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .endpoint { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
            code { background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
            pre { background: #f0f0f0; padding: 15px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Mermaid Render API</h1>
            <p>A FastAPI service for rendering Mermaid diagrams.</p>

            <div class="endpoint">
                <h3>POST /render</h3>
                <p>Render a Mermaid diagram and return the result.</p>
                <pre>{
  "diagram": "flowchart TD\\n    A[Start] --> B[End]",
  "format": "svg",
  "theme": "default"
}</pre>
            </div>

            <div class="endpoint">
                <h3>POST /render/file</h3>
                <p>Render a Mermaid diagram and return as downloadable file.</p>
            </div>

            <div class="endpoint">
                <h3>GET /docs</h3>
                <p>Interactive API documentation (Swagger UI).</p>
            </div>

            <p><a href="/docs">📖 View Interactive API Documentation</a></p>
        </div>
    </body>
    </html>
    """

@app.post("/render", response_model=DiagramResponse)
async def render_diagram(request: DiagramRequest):
    """Render a Mermaid diagram and return the content."""
    try:
        if not request.diagram.strip():
            raise HTTPException(status_code=400, detail="No diagram code provided")

        # Render the diagram
        result = quick_render(
            request.diagram,
            format=request.format,
            theme=request.theme
        )

        return DiagramResponse(
            success=True,
            content=result
        )

    except ValidationError as e:
        return DiagramResponse(
            success=False,
            error="Validation failed",
            details=str(e)
        )

    except RenderingError as e:
        return DiagramResponse(
            success=False,
            error="Rendering failed",
            details=str(e)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/render/file")
async def render_diagram_file(request: DiagramRequest):
    """Render a Mermaid diagram and return as downloadable file."""
    try:
        result = quick_render(
            request.diagram,
            format=request.format,
            theme=request.theme
        )

        # Determine content type
        content_type = {
            'svg': 'image/svg+xml',
            'png': 'image/png',
            'pdf': 'application/pdf'
        }.get(request.format, 'application/octet-stream')

        return Response(
            content=result,
            media_type=content_type,
            headers={
                'Content-Disposition': f'attachment; filename=diagram.{request.format}'
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mermaid-render"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

    # Save the FastAPI app example
    fastapi_file = output_dir / "fastapi_app.py"
    with open(fastapi_file, "w") as f:
        f.write(fastapi_app_code)

    print("✅ FastAPI integration example created")
    print(f"📁 Saved to {fastapi_file}")
    print("🚀 Run with: python fastapi_app.py")
    print("🌐 Open: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")


def cli_integration_example(output_dir: Path) -> None:
    """Demonstrate CLI application integration."""
    print("CLI integration example...")

    cli_script_code = '''#!/usr/bin/env python3
"""
Advanced CLI tool for Mermaid diagram processing.

This script demonstrates how to build a comprehensive CLI tool
using the Mermaid Render library.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import List, Optional

from mermaid_render import (
    MermaidRenderer,
    quick_render,
    export_to_file,
    export_multiple_formats,
    batch_export,
    validate_mermaid_syntax,
    get_supported_formats,
    get_available_themes,
    ValidationError,
    RenderingError
)

def validate_command(args):
    """Validate Mermaid diagram syntax."""
    try:
        if args.input == '-':
            content = sys.stdin.read()
        else:
            content = Path(args.input).read_text()

        result = validate_mermaid_syntax(content)

        if result.is_valid:
            print("✅ Diagram is valid")
            return 0
        else:
            print("❌ Validation failed:")
            for error in result.errors:
                print(f"  - {error}")
            return 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

def render_command(args):
    """Render a single diagram."""
    try:
        if args.input == '-':
            content = sys.stdin.read()
        else:
            content = Path(args.input).read_text()

        if args.output:
            export_to_file(
                content,
                args.output,
                format=args.format,
                theme=args.theme
            )
            print(f"✅ Rendered to {args.output}")
        else:
            result = quick_render(content, format=args.format, theme=args.theme)
            print(result)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

def batch_command(args):
    """Batch process multiple diagrams."""
    try:
        input_dir = Path(args.input_dir)
        output_dir = Path(args.output_dir)

        # Find all .mmd files
        mmd_files = list(input_dir.glob("*.mmd"))
        if not mmd_files:
            print(f"No .mmd files found in {input_dir}")
            return 1

        # Prepare diagrams dictionary
        diagrams = {}
        for mmd_file in mmd_files:
            name = mmd_file.stem
            content = mmd_file.read_text()
            diagrams[name] = content

        # Batch export
        output_paths = batch_export(
            diagrams,
            output_dir,
            format=args.format,
            theme=args.theme
        )

        print(f"✅ Processed {len(output_paths)} diagrams:")
        for name, path in output_paths.items():
            print(f"  {name} -> {path}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

def multi_format_command(args):
    """Export diagram to multiple formats."""
    try:
        if args.input == '-':
            content = sys.stdin.read()
        else:
            content = Path(args.input).read_text()

        formats = args.formats.split(',')
        base_path = Path(args.output).with_suffix('')

        output_paths = export_multiple_formats(
            content,
            base_path,
            formats,
            theme=args.theme
        )

        print(f"✅ Exported to {len(formats)} formats:")
        for fmt, path in output_paths.items():
            print(f"  {fmt}: {path}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

def info_command(args):
    """Show library information."""
    print("Mermaid Render Library Information")
    print("=" * 40)

    print(f"Supported formats: {', '.join(get_supported_formats())}")
    print(f"Available themes: {', '.join(get_available_themes())}")

    # Show example usage
    print("\\nExample usage:")
    print("  mermaid-cli render input.mmd -o output.svg")
    print("  mermaid-cli batch ./diagrams ./output --format png")
    print("  mermaid-cli multi input.mmd -o diagram --formats svg,png,pdf")

    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Advanced Mermaid diagram processing CLI",
        prog="mermaid-cli"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate diagram syntax')
    validate_parser.add_argument('input', help='Input file (use - for stdin)')

    # Render command
    render_parser = subparsers.add_parser('render', help='Render single diagram')
    render_parser.add_argument('input', help='Input file (use - for stdin)')
    render_parser.add_argument('-o', '--output', help='Output file')
    render_parser.add_argument('-f', '--format', default='svg', choices=get_supported_formats())
    render_parser.add_argument('-t', '--theme', choices=get_available_themes())

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch process diagrams')
    batch_parser.add_argument('input_dir', help='Input directory with .mmd files')
    batch_parser.add_argument('output_dir', help='Output directory')
    batch_parser.add_argument('-f', '--format', default='svg', choices=get_supported_formats())
    batch_parser.add_argument('-t', '--theme', choices=get_available_themes())

    # Multi-format command
    multi_parser = subparsers.add_parser('multi', help='Export to multiple formats')
    multi_parser.add_argument('input', help='Input file (use - for stdin)')
    multi_parser.add_argument('-o', '--output', required=True, help='Output base path')
    multi_parser.add_argument('--formats', default='svg,png', help='Comma-separated formats')
    multi_parser.add_argument('-t', '--theme', choices=get_available_themes())

    # Info command
    info_parser = subparsers.add_parser('info', help='Show library information')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    commands = {
        'validate': validate_command,
        'render': render_command,
        'batch': batch_command,
        'multi': multi_format_command,
        'info': info_command
    }

    return commands[args.command](args)

if __name__ == '__main__':
    sys.exit(main())
'''

    # Save the CLI script
    cli_file = output_dir / "advanced_cli.py"
    with open(cli_file, "w") as f:
        f.write(cli_script_code)

    # Make it executable
    cli_file.chmod(0o755)

    print("✅ Advanced CLI example created")
    print(f"📁 Saved to {cli_file}")
    print("🚀 Usage examples:")
    print("  python advanced_cli.py info")
    print("  python advanced_cli.py validate diagram.mmd")
    print("  python advanced_cli.py render diagram.mmd -o output.svg")


def main() -> None:
    """Run all integration examples."""
    print("=== Mermaid Render Integration Examples ===\n")

    # Create output directory
    output_dir = create_output_dir()
    print(f"Output directory: {output_dir.absolute()}\n")

    # Run examples
    try:
        flask_integration_example(output_dir)
        print()

        fastapi_integration_example(output_dir)
        print()

        cli_integration_example(output_dir)
        print()

        print("✅ All integration examples completed successfully!")
        print(f"Check the {output_dir} directory for integration code.")

    except Exception as e:
        print(f"❌ Error creating integration examples: {e}")
        raise


if __name__ == "__main__":
    main()
