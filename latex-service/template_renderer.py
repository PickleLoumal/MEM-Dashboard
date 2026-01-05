"""
Template Renderer Module

Renders Jinja2 LaTeX templates with data and chart references.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from chart_generator import ChartResult
from latex_utils import (
    escape_latex,
    escape_latex_preserve_newlines,
    format_currency,
    format_number,
    format_percentage,
)

logger = logging.getLogger(__name__)

# Default templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"


def _register_filters(env: Environment) -> None:
    """Register custom LaTeX filters on a Jinja2 environment."""
    env.filters["escape"] = escape_latex
    env.filters["escape_para"] = escape_latex_preserve_newlines
    env.filters["number"] = format_number
    env.filters["percentage"] = format_percentage
    env.filters["currency"] = format_currency
    env.filters["date"] = lambda d: _format_date(d)


def create_jinja_env(templates_dir: Path | None = None) -> Environment:
    """
    Create Jinja2 environment with LaTeX-specific configuration.

    Args:
        templates_dir: Optional custom templates directory

    Returns:
        Configured Jinja2 Environment
    """
    loader = FileSystemLoader(str(templates_dir or TEMPLATES_DIR))

    env = Environment(
        loader=loader,
        autoescape=select_autoescape([]),  # No auto-escaping for LaTeX
        block_start_string=r"\BLOCK{",
        block_end_string=r"}",
        variable_start_string=r"\VAR{",
        variable_end_string=r"}",
        comment_start_string=r"\#{",
        comment_end_string=r"}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=True,
        lstrip_blocks=True,
    )

    _register_filters(env)
    return env


@lru_cache(maxsize=1)
def _get_string_jinja_env() -> Environment:
    """
    Get cached Jinja2 environment for string templates.

    This avoids recreating the environment on every render call.
    Uses LaTeX-compatible delimiters to avoid conflicts with LaTeX syntax.
    """
    env = Environment(
        block_start_string=r"\BLOCK{",
        block_end_string=r"}",
        variable_start_string=r"\VAR{",
        variable_end_string=r"}",
        comment_start_string=r"\#{",
        comment_end_string=r"}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=True,
        lstrip_blocks=True,
    )
    _register_filters(env)
    return env


def _format_date(date_value: Any) -> str:
    """Format date for LaTeX display."""
    if date_value is None:
        return "N/A"

    if isinstance(date_value, str):
        try:
            date_value = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        except ValueError:
            return date_value

    if isinstance(date_value, datetime):
        return date_value.strftime("%B %d, %Y")

    return str(date_value)


def render_template(
    template_content: str,
    preamble: str,
    data: dict[str, Any],
    charts: list[ChartResult],
    settings: dict[str, Any] | None = None,
) -> str:
    """
    Render a LaTeX template with data.

    Args:
        template_content: Jinja2 LaTeX template content
        preamble: LaTeX preamble (package imports)
        data: Combined summary and company data
        charts: List of generated charts
        settings: Page settings (margins, headers, etc.)

    Returns:
        Complete LaTeX document ready for compilation
    """
    settings = settings or {}

    # Build chart references for template
    chart_refs = {chart.name: f"{chart.name}.png" for chart in charts}

    # Use timezone-aware UTC datetime for consistency across environments
    now_utc = datetime.now(timezone.utc)

    # Prepare template context
    context = {
        "summary": data.get("summary", {}),
        "company": data.get("company", {}),
        "charts": chart_refs,
        "settings": settings,
        "report_date": now_utc.strftime("%B %d, %Y"),
        "generated_at": now_utc.isoformat(),
    }

    # Use cached Jinja environment for string templates
    env = _get_string_jinja_env()

    try:
        # Render preamble (it may contain Jinja2 variables like \VAR{ company.ticker })
        preamble_template = env.from_string(preamble)
        rendered_preamble = preamble_template.render(**context)

        # Render main content
        template = env.from_string(template_content)
        rendered_body = template.render(**context)

        # Build complete document
        document = build_document(
            preamble=rendered_preamble,
            body=rendered_body,
            settings=settings,
        )

        logger.info("Template rendered successfully")
        return document

    except Exception as e:
        logger.exception("Failed to render template")
        raise TemplateRenderError(f"Template rendering failed: {e}") from e


def build_document(
    preamble: str,
    body: str,
    settings: dict[str, Any],
) -> str:
    """
    Build a complete LaTeX document.

    The preamble from the database already contains:
    - \\documentclass
    - All package imports (geometry, fancyhdr, colors, etc.)
    - Page settings (margins, headers, footers)
    - \\begin{document}

    This function simply combines preamble + body + \\end{document}.

    Args:
        preamble: Complete document preamble including \\begin{document}
        body: Rendered document body
        settings: Page settings (currently unused, settings are in preamble)

    Returns:
        Complete LaTeX document
    """
    # Preamble already includes \documentclass, packages, and \begin{document}
    # Just append the body and close the document
    document = f"""{preamble}

{body}

\\end{{document}}
"""
    return document


def render_from_file(
    template_name: str,
    data: dict[str, Any],
    charts: list[ChartResult],
    settings: dict[str, Any] | None = None,
) -> str:
    """
    Render a template from file.

    Args:
        template_name: Template filename (e.g., "investment_summary.tex.j2")
        data: Template data
        charts: Generated charts
        settings: Page settings

    Returns:
        Complete LaTeX document
    """
    env = create_jinja_env()

    template = env.get_template(template_name)
    chart_refs = {chart.name: f"{chart.name}.png" for chart in charts}

    # Use timezone-aware UTC datetime
    now_utc = datetime.now(timezone.utc)

    context = {
        "summary": data.get("summary", {}),
        "company": data.get("company", {}),
        "charts": chart_refs,
        "settings": settings or {},
        "report_date": now_utc.strftime("%B %d, %Y"),
    }

    body = template.render(**context)

    return build_document(
        preamble="",
        body=body,
        settings=settings or {},
    )


class TemplateRenderError(Exception):
    """Raised when template rendering fails."""

    pass

