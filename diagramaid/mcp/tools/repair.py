"""
Mermaid diagram auto-repair workflow tools.

This module provides comprehensive auto-repair functionality for Mermaid diagrams,
leveraging FastMCP's Context for logging, progress reporting, and LLM sampling.
The repair workflow validates diagrams, identifies issues, and applies fixes
either automatically or with AI assistance.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Any

try:
    from fastmcp import Context
    from pydantic import BaseModel, Field

    _FASTMCP_AVAILABLE = True
except ImportError:
    Context = None  # type: ignore
    _FASTMCP_AVAILABLE = False

    class BaseModel:  # type: ignore[no-redef]
        """Fallback BaseModel when pydantic is not available."""

        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def Field(**kwargs: Any) -> Any:
        """Fallback Field when pydantic is not available."""
        return kwargs.get("default")


from ...validators import MermaidValidator, ValidationResult
from .base import (
    ErrorCategory,
    create_error_response,
    create_success_response,
)
from .helpers import _detect_diagram_type

logger = logging.getLogger(__name__)


class RepairStrategy(str, Enum):
    """Strategy for repairing diagrams."""

    AUTO = "auto"  # Apply automatic fixes only
    AI_ASSISTED = "ai_assisted"  # Use LLM sampling for complex fixes
    SUGGEST_ONLY = "suggest_only"  # Only suggest fixes, don't apply


class RepairSeverity(str, Enum):
    """Severity level of issues found."""

    CRITICAL = "critical"  # Diagram won't render
    ERROR = "error"  # Syntax errors
    WARNING = "warning"  # Best practice violations
    INFO = "info"  # Suggestions for improvement


@dataclass
class RepairAction:
    """Represents a single repair action."""

    line_number: int | None
    original: str
    replacement: str
    description: str
    severity: RepairSeverity
    auto_fixable: bool


@dataclass
class RepairResult:
    """Result of a repair operation."""

    success: bool
    original_code: str
    repaired_code: str
    actions_applied: list[RepairAction]
    actions_suggested: list[RepairAction]
    validation_before: ValidationResult
    validation_after: ValidationResult | None
    ai_suggestions: list[str] | None = None


class DiagramRepairer:
    """
    Comprehensive Mermaid diagram repairer.

    Provides automatic and AI-assisted repair capabilities for Mermaid diagrams.
    """

    # Common syntax fixes patterns
    SYNTAX_FIXES = [
        # Fix common arrow typos
        (r"--\s*>", "-->", "Fixed arrow syntax: -- > to -->"),
        (r"-\s+>", "-->", "Fixed arrow syntax: - > to -->"),
        (r"<\s*--", "<--", "Fixed arrow syntax: < -- to <--"),
        # Fix bracket issues
        (r"\[\s+", "[", "Removed extra space after opening bracket"),
        (r"\s+\]", "]", "Removed extra space before closing bracket"),
        (r"\(\s+", "(", "Removed extra space after opening parenthesis"),
        (r"\s+\)", ")", "Removed extra space before closing parenthesis"),
        # Fix common diagram type typos
        (r"^flowChart", "flowchart", "Fixed diagram type: flowChart to flowchart"),
        (r"^sequencediagram", "sequenceDiagram", "Fixed diagram type case"),
        (r"^classdiagram", "classDiagram", "Fixed diagram type case"),
        (r"^statediagram", "stateDiagram", "Fixed diagram type case"),
        (r"^erdiagram", "erDiagram", "Fixed diagram type case"),
        # Fix direction typos
        (r"flowchart\s+td", "flowchart TD", "Fixed direction case: td to TD"),
        (r"flowchart\s+lr", "flowchart LR", "Fixed direction case: lr to LR"),
        (r"flowchart\s+tb", "flowchart TB", "Fixed direction case: tb to TB"),
        (r"flowchart\s+rl", "flowchart RL", "Fixed direction case: rl to RL"),
        (r"flowchart\s+bt", "flowchart BT", "Fixed direction case: bt to BT"),
    ]

    # Bracket matching patterns
    BRACKET_PAIRS = {"[": "]", "(": ")", "{": "}"}

    def __init__(self) -> None:
        """Initialize the repairer."""
        self.validator = MermaidValidator()

    def analyze(self, mermaid_code: str) -> tuple[ValidationResult, list[RepairAction]]:
        """
        Analyze diagram and identify potential repairs.

        Args:
            mermaid_code: The Mermaid diagram code to analyze

        Returns:
            Tuple of (validation_result, list of repair actions)
        """
        validation = self.validator.validate(mermaid_code)
        actions: list[RepairAction] = []

        lines = mermaid_code.split("\n")

        # Check for syntax pattern fixes
        for i, line in enumerate(lines, 1):
            for pattern, replacement, description in self.SYNTAX_FIXES:
                if re.search(pattern, line, re.IGNORECASE if "diagram" in pattern.lower() else 0):
                    actions.append(
                        RepairAction(
                            line_number=i,
                            original=line,
                            replacement=re.sub(
                                pattern,
                                replacement,
                                line,
                                flags=re.IGNORECASE if "diagram" in pattern.lower() else 0,
                            ),
                            description=description,
                            severity=RepairSeverity.ERROR,
                            auto_fixable=True,
                        )
                    )

        # Check for bracket issues
        for i, line in enumerate(lines, 1):
            bracket_actions = self._check_brackets(line, i)
            actions.extend(bracket_actions)

        # Check for empty diagram
        if not mermaid_code.strip():
            actions.append(
                RepairAction(
                    line_number=None,
                    original="",
                    replacement="flowchart TD\n    A[Start] --> B[End]",
                    description="Added basic flowchart template for empty diagram",
                    severity=RepairSeverity.CRITICAL,
                    auto_fixable=True,
                )
            )

        # Check for missing diagram type
        if lines and not self._has_valid_diagram_type(lines[0]):
            actions.append(
                RepairAction(
                    line_number=1,
                    original=lines[0] if lines else "",
                    replacement=f"flowchart TD\n{lines[0]}" if lines else "flowchart TD",
                    description="Added missing diagram type declaration",
                    severity=RepairSeverity.CRITICAL,
                    auto_fixable=False,  # Needs user confirmation
                )
            )

        return validation, actions

    def _check_brackets(self, line: str, line_number: int) -> list[RepairAction]:
        """Check for bracket issues in a line."""
        actions: list[RepairAction] = []
        stack: list[str] = []

        for char in line:
            if char in self.BRACKET_PAIRS:
                stack.append(self.BRACKET_PAIRS[char])
            elif char in self.BRACKET_PAIRS.values():
                if not stack or stack.pop() != char:
                    # Unmatched closing bracket
                    actions.append(
                        RepairAction(
                            line_number=line_number,
                            original=line,
                            replacement=line,  # Can't auto-fix without context
                            description=f"Unmatched bracket '{char}' detected",
                            severity=RepairSeverity.ERROR,
                            auto_fixable=False,
                        )
                    )
                    return actions

        if stack:
            # Unclosed brackets
            missing = "".join(reversed(stack))
            actions.append(
                RepairAction(
                    line_number=line_number,
                    original=line,
                    replacement=line + missing,
                    description=f"Added missing closing bracket(s): {missing}",
                    severity=RepairSeverity.ERROR,
                    auto_fixable=True,
                )
            )

        return actions

    def _has_valid_diagram_type(self, first_line: str) -> bool:
        """Check if the first line has a valid diagram type."""
        first_line = first_line.strip().lower()
        valid_types = [
            "flowchart",
            "graph",
            "sequencediagram",
            "classdiagram",
            "statediagram",
            "erdiagram",
            "journey",
            "gantt",
            "pie",
            "gitgraph",
            "mindmap",
            "timeline",
        ]
        return any(first_line.startswith(t) for t in valid_types)

    def apply_auto_fixes(
        self, mermaid_code: str, actions: list[RepairAction]
    ) -> tuple[str, list[RepairAction]]:
        """
        Apply automatic fixes to the diagram.

        Args:
            mermaid_code: Original diagram code
            actions: List of repair actions to consider

        Returns:
            Tuple of (repaired_code, applied_actions)
        """
        applied: list[RepairAction] = []
        lines = mermaid_code.split("\n")

        # Sort actions by line number (None last)
        sorted_actions = sorted(
            [a for a in actions if a.auto_fixable],
            key=lambda x: (x.line_number is None, x.line_number or 0),
        )

        for action in sorted_actions:
            if action.line_number is not None:
                idx = action.line_number - 1
                if 0 <= idx < len(lines) and lines[idx] == action.original:
                    lines[idx] = action.replacement
                    applied.append(action)
            elif action.original == "" and not mermaid_code.strip():
                # Empty diagram case
                return action.replacement, [action]

        return "\n".join(lines), applied

    def repair(
        self,
        mermaid_code: str,
        strategy: RepairStrategy = RepairStrategy.AUTO,
    ) -> RepairResult:
        """
        Repair a Mermaid diagram.

        Args:
            mermaid_code: The diagram code to repair
            strategy: Repair strategy to use

        Returns:
            RepairResult with details of the repair operation
        """
        # Analyze the diagram
        validation_before, actions = self.analyze(mermaid_code)

        if strategy == RepairStrategy.SUGGEST_ONLY:
            return RepairResult(
                success=True,
                original_code=mermaid_code,
                repaired_code=mermaid_code,
                actions_applied=[],
                actions_suggested=actions,
                validation_before=validation_before,
                validation_after=None,
            )

        # Apply automatic fixes
        repaired_code, applied_actions = self.apply_auto_fixes(mermaid_code, actions)

        # Validate the repaired code
        validation_after = self.validator.validate(repaired_code)

        # Determine suggested (non-applied) actions
        suggested_actions = [a for a in actions if a not in applied_actions]

        return RepairResult(
            success=validation_after.is_valid,
            original_code=mermaid_code,
            repaired_code=repaired_code,
            actions_applied=applied_actions,
            actions_suggested=suggested_actions,
            validation_before=validation_before,
            validation_after=validation_after,
        )


# ============================================================================
# MCP Tool Functions with FastMCP Context Support
# ============================================================================


async def repair_diagram(
    diagram_code: Annotated[str, "The Mermaid diagram code to repair"],
    strategy: Annotated[
        str, "Repair strategy: 'auto', 'ai_assisted', or 'suggest_only'"
    ] = "auto",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Automatically repair a Mermaid diagram with comprehensive error fixing.

    This tool analyzes a Mermaid diagram for syntax errors, structural issues,
    and best practice violations, then applies automatic fixes where possible.
    It uses FastMCP's Context for progress reporting and logging.

    The repair workflow:
    1. Validates the original diagram
    2. Identifies fixable issues (syntax, brackets, formatting)
    3. Applies automatic fixes for safe corrections
    4. Suggests manual fixes for complex issues
    5. Validates the repaired diagram

    Args:
        diagram_code: The Mermaid diagram code to repair
        strategy: Repair strategy - 'auto' (default), 'ai_assisted', or 'suggest_only'
        ctx: FastMCP Context for logging and progress (injected automatically)

    Returns:
        Dictionary containing repair results, applied fixes, and suggestions

    Example:
        >>> result = await repair_diagram(
        ...     "flowchart td\\n    A[Start -- > B[End",
        ...     strategy="auto"
        ... )
        >>> print(result["data"]["repaired_code"])
        >>> print(result["data"]["fixes_applied"])
    """
    try:
        # Log start of repair process
        if ctx:
            await ctx.info(f"Starting diagram repair with strategy: {strategy}")
            await ctx.report_progress(progress=0, total=100)

        # Parse strategy
        try:
            repair_strategy = RepairStrategy(strategy.lower())
        except ValueError:
            repair_strategy = RepairStrategy.AUTO
            if ctx:
                await ctx.warning(f"Unknown strategy '{strategy}', using 'auto'")

        # Initialize repairer
        repairer = DiagramRepairer()

        if ctx:
            await ctx.debug("Analyzing diagram for issues...")
            await ctx.report_progress(progress=20, total=100)

        # Perform repair
        result = repairer.repair(diagram_code, repair_strategy)

        if ctx:
            await ctx.report_progress(progress=60, total=100)

        # Handle AI-assisted repair if requested and available
        ai_suggestions: list[str] = []
        if repair_strategy == RepairStrategy.AI_ASSISTED and ctx:
            await ctx.info("Requesting AI assistance for complex fixes...")
            try:
                # Use LLM sampling for AI-assisted repair
                prompt = f"""Analyze this Mermaid diagram and suggest fixes for any remaining issues:

Original diagram:
```mermaid
{diagram_code}
```

Current validation errors: {result.validation_before.errors}
Current warnings: {result.validation_before.warnings}

Please provide specific, actionable suggestions to fix these issues.
Format each suggestion as a numbered list."""

                sampling_result = await ctx.sample(
                    messages=prompt,
                    system_prompt="You are an expert in Mermaid diagram syntax. Provide concise, specific fixes.",
                    temperature=0.3,
                    max_tokens=500,
                )
                ai_suggestions = [sampling_result.text]
                result.ai_suggestions = ai_suggestions
                await ctx.info("AI suggestions received successfully")
            except Exception as e:
                await ctx.warning(f"AI assistance unavailable: {e}")

        if ctx:
            await ctx.report_progress(progress=90, total=100)

        # Prepare response data
        response_data = {
            "original_code": result.original_code,
            "repaired_code": result.repaired_code,
            "is_repaired": result.repaired_code != result.original_code,
            "is_valid_after_repair": (
                result.validation_after.is_valid if result.validation_after else None
            ),
            "fixes_applied": [
                {
                    "line": a.line_number,
                    "description": a.description,
                    "severity": a.severity.value,
                    "original": a.original[:50] + "..." if len(a.original) > 50 else a.original,
                    "replacement": a.replacement[:50] + "..."
                    if len(a.replacement) > 50
                    else a.replacement,
                }
                for a in result.actions_applied
            ],
            "suggestions": [
                {
                    "line": a.line_number,
                    "description": a.description,
                    "severity": a.severity.value,
                    "auto_fixable": a.auto_fixable,
                }
                for a in result.actions_suggested
            ],
            "ai_suggestions": ai_suggestions if ai_suggestions else None,
            "validation_before": {
                "valid": result.validation_before.is_valid,
                "errors": result.validation_before.errors,
                "warnings": result.validation_before.warnings,
            },
            "validation_after": (
                {
                    "valid": result.validation_after.is_valid,
                    "errors": result.validation_after.errors,
                    "warnings": result.validation_after.warnings,
                }
                if result.validation_after
                else None
            ),
        }

        # Prepare metadata
        metadata = {
            "strategy": repair_strategy.value,
            "diagram_type": _detect_diagram_type(diagram_code),
            "fixes_applied_count": len(result.actions_applied),
            "suggestions_count": len(result.actions_suggested),
            "original_line_count": len(diagram_code.splitlines()),
            "repaired_line_count": len(result.repaired_code.splitlines()),
        }

        if ctx:
            await ctx.report_progress(progress=100, total=100)
            if result.actions_applied:
                await ctx.info(
                    f"Repair complete: {len(result.actions_applied)} fixes applied"
                )
            else:
                await ctx.info("Repair complete: No automatic fixes needed")

        return create_success_response(data=response_data, metadata=metadata)

    except Exception as e:
        logger.error(f"Error in repair_diagram: {e}")
        if ctx:
            await ctx.error(f"Repair failed: {e}")
        return create_error_response(
            e,
            ErrorCategory.VALIDATION,
            context={"diagram_code_length": len(diagram_code) if diagram_code else 0},
            suggestions=[
                "Check that the diagram code is valid UTF-8",
                "Ensure the diagram has basic structure",
            ],
        )


async def validate_and_repair(
    diagram_code: Annotated[str, "The Mermaid diagram code to validate and repair"],
    auto_repair: Annotated[bool, "Whether to automatically apply safe fixes"] = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Validate a Mermaid diagram and optionally repair it in one step.

    This is a convenience tool that combines validation and repair into a single
    workflow. It first validates the diagram, then optionally applies automatic
    fixes if issues are found.

    Args:
        diagram_code: The Mermaid diagram code to validate and repair
        auto_repair: Whether to automatically apply safe fixes (default: True)
        ctx: FastMCP Context for logging and progress (injected automatically)

    Returns:
        Dictionary containing validation results and optional repair information

    Example:
        >>> result = await validate_and_repair(
        ...     "flowchart TD\\n    A[Start] --> B[End]",
        ...     auto_repair=True
        ... )
        >>> if result["data"]["needs_repair"]:
        ...     print(result["data"]["repaired_code"])
    """
    try:
        if ctx:
            await ctx.info("Starting validate-and-repair workflow")
            await ctx.report_progress(progress=0, total=100)

        # Initialize validator and repairer
        validator = MermaidValidator()
        repairer = DiagramRepairer()

        if ctx:
            await ctx.debug("Validating diagram...")
            await ctx.report_progress(progress=25, total=100)

        # Validate
        validation = validator.validate(diagram_code)

        if ctx:
            await ctx.report_progress(progress=50, total=100)

        # Check if repair is needed
        needs_repair = not validation.is_valid or len(validation.warnings) > 0

        repaired_code = diagram_code
        repair_info = None

        if needs_repair and auto_repair:
            if ctx:
                await ctx.info("Issues found, applying automatic repairs...")
                await ctx.report_progress(progress=75, total=100)

            # Perform repair
            repair_result = repairer.repair(diagram_code, RepairStrategy.AUTO)
            repaired_code = repair_result.repaired_code

            repair_info = {
                "fixes_applied": len(repair_result.actions_applied),
                "suggestions_remaining": len(repair_result.actions_suggested),
                "is_valid_after": (
                    repair_result.validation_after.is_valid
                    if repair_result.validation_after
                    else None
                ),
            }
        elif needs_repair:
            if ctx:
                await ctx.warning("Issues found but auto_repair is disabled")

        if ctx:
            await ctx.report_progress(progress=100, total=100)

        response_data = {
            "original_valid": validation.is_valid,
            "needs_repair": needs_repair,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "line_errors": validation.line_errors,
            "diagram_type": _detect_diagram_type(diagram_code),
            "repaired_code": repaired_code if needs_repair and auto_repair else None,
            "repair_info": repair_info,
        }

        metadata = {
            "auto_repair_enabled": auto_repair,
            "line_count": len(diagram_code.splitlines()),
            "error_count": len(validation.errors),
            "warning_count": len(validation.warnings),
        }

        if ctx:
            if validation.is_valid:
                await ctx.info("Diagram is valid, no repairs needed")
            elif repair_info and repair_info.get("is_valid_after"):
                await ctx.info("Diagram repaired successfully")
            else:
                await ctx.warning("Some issues could not be automatically fixed")

        return create_success_response(data=response_data, metadata=metadata)

    except Exception as e:
        logger.error(f"Error in validate_and_repair: {e}")
        if ctx:
            await ctx.error(f"Validation/repair failed: {e}")
        return create_error_response(
            e,
            ErrorCategory.VALIDATION,
            context={"diagram_code_length": len(diagram_code) if diagram_code else 0},
        )


async def get_repair_suggestions(
    diagram_code: Annotated[str, "The Mermaid diagram code to analyze"],
    include_ai_suggestions: Annotated[
        bool, "Whether to include AI-powered suggestions"
    ] = False,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Get detailed repair suggestions for a Mermaid diagram without applying fixes.

    This tool analyzes a diagram and provides comprehensive suggestions for
    improvement, including syntax fixes, best practices, and optionally
    AI-powered recommendations.

    Args:
        diagram_code: The Mermaid diagram code to analyze
        include_ai_suggestions: Whether to include AI-powered suggestions
        ctx: FastMCP Context for logging and progress (injected automatically)

    Returns:
        Dictionary containing detailed repair suggestions

    Example:
        >>> result = await get_repair_suggestions(
        ...     "flowchart TD\\n    A --> B",
        ...     include_ai_suggestions=True
        ... )
        >>> for suggestion in result["data"]["suggestions"]:
        ...     print(f"Line {suggestion['line']}: {suggestion['description']}")
    """
    try:
        if ctx:
            await ctx.info("Analyzing diagram for repair suggestions")
            await ctx.report_progress(progress=0, total=100)

        repairer = DiagramRepairer()

        if ctx:
            await ctx.report_progress(progress=30, total=100)

        # Analyze without applying fixes
        validation, actions = repairer.analyze(diagram_code)

        if ctx:
            await ctx.report_progress(progress=60, total=100)

        # Categorize suggestions
        auto_fixable = [a for a in actions if a.auto_fixable]
        manual_required = [a for a in actions if not a.auto_fixable]

        # Get AI suggestions if requested
        ai_suggestions: list[str] = []
        if include_ai_suggestions and ctx:
            try:
                await ctx.info("Requesting AI-powered suggestions...")
                prompt = f"""Analyze this Mermaid diagram and provide improvement suggestions:

```mermaid
{diagram_code}
```

Focus on:
1. Syntax correctness
2. Best practices
3. Readability improvements
4. Structural organization

Provide 3-5 specific, actionable suggestions."""

                result = await ctx.sample(
                    messages=prompt,
                    system_prompt="You are a Mermaid diagram expert. Be concise and specific.",
                    temperature=0.3,
                    max_tokens=400,
                )
                ai_suggestions = [result.text]
            except Exception as e:
                if ctx:
                    await ctx.warning(f"AI suggestions unavailable: {e}")

        if ctx:
            await ctx.report_progress(progress=100, total=100)

        response_data = {
            "is_valid": validation.is_valid,
            "total_issues": len(actions),
            "auto_fixable_count": len(auto_fixable),
            "manual_required_count": len(manual_required),
            "suggestions": [
                {
                    "line": a.line_number,
                    "description": a.description,
                    "severity": a.severity.value,
                    "auto_fixable": a.auto_fixable,
                    "original": a.original[:100] if a.original else None,
                    "suggested_fix": a.replacement[:100] if a.replacement else None,
                }
                for a in actions
            ],
            "validation_errors": validation.errors,
            "validation_warnings": validation.warnings,
            "ai_suggestions": ai_suggestions if ai_suggestions else None,
        }

        metadata = {
            "diagram_type": _detect_diagram_type(diagram_code),
            "line_count": len(diagram_code.splitlines()),
            "ai_suggestions_included": include_ai_suggestions and bool(ai_suggestions),
        }

        if ctx:
            await ctx.info(
                f"Analysis complete: {len(actions)} suggestions, "
                f"{len(auto_fixable)} auto-fixable"
            )

        return create_success_response(data=response_data, metadata=metadata)

    except Exception as e:
        logger.error(f"Error in get_repair_suggestions: {e}")
        if ctx:
            await ctx.error(f"Analysis failed: {e}")
        return create_error_response(
            e,
            ErrorCategory.VALIDATION,
            context={"diagram_code_length": len(diagram_code) if diagram_code else 0},
        )
