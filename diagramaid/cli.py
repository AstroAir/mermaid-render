#!/usr/bin/env python3
"""
Command-line interface for Mermaid Render.

This module provides a CLI for rendering Mermaid diagrams from the command line.
"""

import argparse
import sys
from pathlib import Path

from . import __version__, quick_render
from .exceptions import RenderingError, ValidationError


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Render Mermaid diagrams from the command line",
        prog="diagramaid",
    )

    parser.add_argument(
        "--version", action="version", version=f"diagramaid {__version__}"
    )

    parser.add_argument(
        "input", help="Input file containing Mermaid diagram code (use '-' for stdin)"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: stdout for SVG, required for other formats)",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["svg", "png", "pdf"],
        default="svg",
        help="Output format (default: svg)",
    )

    parser.add_argument(
        "-t",
        "--theme",
        help="Theme to use for rendering (default, dark, forest, neutral)",
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate the diagram, don't render",
    )

    parser.add_argument("--quiet", action="store_true", help="Suppress output messages")

    args = parser.parse_args()

    try:
        # Read input
        if args.input == "-":
            diagram_code = sys.stdin.read()
        else:
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
                return 1
            diagram_code = input_path.read_text(encoding="utf-8")

        if not diagram_code.strip():
            print("Error: No diagram code provided", file=sys.stderr)
            return 1

        # Validate only mode
        if args.validate_only:
            from .utils import validate_mermaid_syntax

            result = validate_mermaid_syntax(diagram_code)
            if result.is_valid:
                if not args.quiet:
                    print("✅ Diagram is valid")
                return 0
            else:
                print("❌ Validation failed:", file=sys.stderr)
                for error in result.errors:
                    print(f"  - {error}", file=sys.stderr)
                return 1

        # Determine output path
        output_path: str | None = args.output
        if args.format != "svg" and not output_path:
            print(
                f"Error: Output file required for {args.format} format", file=sys.stderr
            )
            return 1

        # Render diagram
        rendered_content = quick_render(
            diagram_code, output_path=output_path, format=args.format, theme=args.theme
        )

        # Output result
        if args.format == "svg" and not output_path:
            print(rendered_content)
        elif not args.quiet:
            if output_path:
                print(f"✅ Diagram rendered to {output_path}")
            else:
                print("✅ Diagram rendered successfully")

        return 0

    except ValidationError as e:
        print(f"❌ Validation error: {e}", file=sys.stderr)
        return 1
    except RenderingError as e:
        print(f"❌ Rendering error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"❌ File error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if not args.quiet:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
