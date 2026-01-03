"""
Template Renderer Module

Renders Jinja2 LaTeX templates with data and chart references.
"""

from __future__ import annotations

import logging
from datetime import datetime
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

    # Register custom filters
    env.filters["escape"] = escape_latex
    env.filters["escape_para"] = escape_latex_preserve_newlines
    env.filters["number"] = format_number
    env.filters["percentage"] = format_percentage
    env.filters["currency"] = format_currency
    env.filters["date"] = lambda d: _format_date(d)

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

    # Prepare template context
    context = {
        "summary": data.get("summary", {}),
        "company": data.get("company", {}),
        "charts": chart_refs,
        "settings": settings,
        "report_date": datetime.now().strftime("%B %d, %Y"),
        "generated_at": datetime.now().isoformat(),
    }

    # Create Jinja environment for string template
    env = Environment(
        block_start_string=r"\BLOCK{",
        block_end_string=r"}",
        variable_start_string=r"\VAR{",
        variable_end_string=r"}",
        comment_start_string=r"\#{",
        comment_end_string=r"}",
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Register filters
    env.filters["escape"] = escape_latex
    env.filters["escape_para"] = escape_latex_preserve_newlines
    env.filters["number"] = format_number
    env.filters["percentage"] = format_percentage
    env.filters["currency"] = format_currency
    env.filters["date"] = lambda d: _format_date(d)

    try:
        # Render main content
        template = env.from_string(template_content)
        rendered_body = template.render(**context)

        # Build complete document
        document = build_document(
            preamble=preamble,
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

    Args:
        preamble: Package imports and custom commands
        body: Rendered document body
        settings: Page settings

    Returns:
        Complete LaTeX document
    """
    page_size = settings.get("page_size", "a4paper")
    margins = settings.get("margins", {})

    # Default margins
    top = margins.get("top", "2.5cm")
    bottom = margins.get("bottom", "2.5cm")
    left = margins.get("left", "2.5cm")
    right = margins.get("right", "2.5cm")

    # Header/Footer
    header_left = settings.get("header_left", "")
    header_right = settings.get("header_right", "")
    footer_center = settings.get("footer_center", r"\thepage")

    document = rf"""
\documentclass[{page_size},11pt]{{article}}

% ============================================================================
% PACKAGES
% ============================================================================
\usepackage{{fontspec}}
\usepackage{{xeCJK}}
\usepackage{{geometry}}
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{longtable}}
\usepackage{{array}}
\usepackage{{xcolor}}
\usepackage{{hyperref}}
\usepackage{{fancyhdr}}
\usepackage{{titlesec}}
\usepackage{{enumitem}}
\usepackage{{float}}
\usepackage{{caption}}

% ============================================================================
% PAGE GEOMETRY
% ============================================================================
\geometry{{
    top={top},
    bottom={bottom},
    left={left},
    right={right}
}}

% ============================================================================
% FONTS
% ============================================================================
\setmainfont{{Noto Sans}}
\setCJKmainfont{{Noto Sans CJK SC}}

% ============================================================================
% COLORS
% ============================================================================
\definecolor{{primary}}{{HTML}}{{2563eb}}
\definecolor{{secondary}}{{HTML}}{{10b981}}
\definecolor{{accent}}{{HTML}}{{f59e0b}}
\definecolor{{danger}}{{HTML}}{{ef4444}}
\definecolor{{textgray}}{{HTML}}{{6b7280}}

% ============================================================================
% HEADER/FOOTER
% ============================================================================
\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[L]{{{escape_latex(header_left)}}}
\fancyhead[R]{{{escape_latex(header_right)}}}
\fancyfoot[C]{{{footer_center}}}
\renewcommand{{\headrulewidth}}{{0.4pt}}
\renewcommand{{\footrulewidth}}{{0pt}}

% ============================================================================
% SECTION STYLING
% ============================================================================
\titleformat{{\section}}
    {{\Large\bfseries\color{{primary}}}}
    {{\thesection}}
    {{1em}}
    {{}}

\titleformat{{\subsection}}
    {{\large\bfseries\color{{primary!80!black}}}}
    {{\thesubsection}}
    {{1em}}
    {{}}

% ============================================================================
% CUSTOM PREAMBLE
% ============================================================================
{preamble}

% ============================================================================
% DOCUMENT
% ============================================================================
\begin{{document}}

{body}

\end{{document}}
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

    context = {
        "summary": data.get("summary", {}),
        "company": data.get("company", {}),
        "charts": chart_refs,
        "settings": settings or {},
        "report_date": datetime.now().strftime("%B %d, %Y"),
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

