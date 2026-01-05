"""
LaTeX Utility Functions

Provides LaTeX-specific utilities: escaping, compilation, and file handling.
"""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
from pathlib import Path
from tempfile import mkdtemp

from config import config

logger = logging.getLogger(__name__)


# LaTeX special characters that need escaping (order matters!)
# Note: Backslash must be handled FIRST to avoid double-escaping
LATEX_SPECIAL_CHARS_ORDERED = [
    # Backslash MUST be first - otherwise \& becomes \\textbackslash{}&
    ("\\", r"\textbackslash{}"),
    # Then all other special characters
    ("&", r"\&"),
    ("%", r"\%"),
    ("$", r"\$"),
    ("#", r"\#"),
    ("_", r"\_"),
    ("{", r"\{"),
    ("}", r"\}"),
    ("~", r"\textasciitilde{}"),
    ("^", r"\textasciicircum{}"),
    ("<", r"\textless{}"),
    (">", r"\textgreater{}"),
    ("|", r"\textbar{}"),
]


def escape_latex(text: str | None) -> str:
    """
    Escape special LaTeX characters in text.

    Args:
        text: Input text (may be None)

    Returns:
        LaTeX-safe escaped string

    Note:
        The order of escaping is critical - backslash must be escaped first
        to avoid double-escaping issues (e.g., & -> \\& -> \\textbackslash{}&)
    """
    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

    # Replace special characters in correct order (backslash first!)
    for char, escape in LATEX_SPECIAL_CHARS_ORDERED:
        text = text.replace(char, escape)

    return text


def escape_latex_preserve_newlines(text: str | None) -> str:
    """
    Escape LaTeX characters while preserving paragraph breaks.

    Converts double newlines to LaTeX paragraph breaks (\\par).
    Single newlines are converted to spaces.

    Args:
        text: Input text

    Returns:
        LaTeX-safe string with preserved paragraphs
    """
    if text is None:
        return ""

    # Split into paragraphs
    paragraphs = re.split(r"\n\s*\n", text)

    # Escape each paragraph and join with \par
    escaped_paragraphs = [escape_latex(p.replace("\n", " ").strip()) for p in paragraphs]

    return r"\par ".join(p for p in escaped_paragraphs if p)


def format_number(value: float | int | None, decimals: int = 2) -> str:
    """
    Format a number for LaTeX display.

    Args:
        value: Numeric value (may be None)
        decimals: Decimal places

    Returns:
        Formatted string with thousands separators
    """
    if value is None:
        return "N/A"

    try:
        if isinstance(value, int) or value == int(value):
            return f"{int(value):,}"
        return f"{value:,.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_percentage(value: float | None, decimals: int = 2) -> str:
    """
    Format a value as percentage for LaTeX.

    Args:
        value: Decimal value (0.15 = 15%)
        decimals: Decimal places

    Returns:
        Formatted percentage string
    """
    if value is None:
        return "N/A"

    try:
        pct = float(value) * 100
        return f"{pct:.{decimals}f}\\%"
    except (ValueError, TypeError):
        return "N/A"


def format_currency(
    value: float | None,
    currency: str = "USD",
    decimals: int = 2,
) -> str:
    """
    Format a value as currency for LaTeX.

    Args:
        value: Numeric value
        currency: Currency code
        decimals: Decimal places

    Returns:
        Formatted currency string
    """
    if value is None:
        return "N/A"

    symbols = {
        "USD": r"\$",
        "CNY": r"¥",
        "HKD": r"HK\$",
        "JPY": r"¥",
        "EUR": r"€",
        "GBP": r"£",
    }

    symbol = symbols.get(currency, currency + " ")

    try:
        formatted = format_number(value, decimals)
        return f"{symbol}{formatted}"
    except (ValueError, TypeError):
        return "N/A"


def compile_latex(
    tex_content: str,
    task_id: str,
    output_name: str = "report",
) -> Path:
    """
    Compile LaTeX content to PDF using XeLaTeX.

    Args:
        tex_content: Complete LaTeX document content
        task_id: Task ID for directory naming
        output_name: Output filename (without extension)

    Returns:
        Path to generated PDF file

    Raises:
        LaTeXCompilationError: If compilation fails
    """
    # Create temporary working directory
    work_dir = Path(mkdtemp(prefix=f"latex_{task_id}_", dir=config.tmp_dir))

    try:
        # Copy charts from output directory to work directory
        # XeLaTeX needs local file access for \includegraphics
        charts_source = config.output_dir / task_id
        if charts_source.exists():
            for chart_file in charts_source.glob("*.png"):
                shutil.copy2(chart_file, work_dir / chart_file.name)
            logger.debug(
                "Copied charts to work directory",
                extra={"task_id": task_id, "count": len(list(charts_source.glob("*.png")))},
            )

        # Write .tex file
        tex_file = work_dir / f"{output_name}.tex"
        tex_file.write_text(tex_content, encoding="utf-8")

        logger.info(
            "Starting LaTeX compilation",
            extra={"task_id": task_id, "work_dir": str(work_dir)},
        )

        # Run xelatex twice for cross-references
        for run in range(2):
            result = subprocess.run(
                [
                    "xelatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    f"-output-directory={work_dir}",
                    str(tex_file),
                ],
                capture_output=True,
                text=True,
                timeout=config.latex_timeout_seconds,
                cwd=work_dir,
            )

            if result.returncode != 0:
                # Extract error from log
                log_file = work_dir / f"{output_name}.log"
                error_msg = _extract_latex_error(log_file, result.stderr)
                logger.error(
                    "LaTeX compilation failed",
                    extra={
                        "task_id": task_id,
                        "run": run + 1,
                        "error": error_msg[:500],
                    },
                )
                raise LaTeXCompilationError(error_msg)

        # Check for PDF output
        pdf_file = work_dir / f"{output_name}.pdf"
        if not pdf_file.exists():
            raise LaTeXCompilationError("PDF file not generated")

        # Move PDF to output directory
        output_path = config.output_dir / task_id / f"{output_name}.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf_file, output_path)

        logger.info(
            "LaTeX compilation successful",
            extra={
                "task_id": task_id,
                "pdf_size": output_path.stat().st_size,
            },
        )

        return output_path

    finally:
        # Cleanup temporary directory
        try:
            shutil.rmtree(work_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup work dir: {e}")


def _extract_latex_error(log_file: Path, stderr: str) -> str:
    """Extract meaningful error message from LaTeX log with context."""
    error_lines = []
    context_lines = []
    in_error = False

    if log_file.exists():
        try:
            log_content = log_file.read_text(encoding="utf-8", errors="ignore")
            lines = log_content.split("\n")

            for i, line in enumerate(lines):
                # Capture error line
                if line.startswith("!"):
                    in_error = True
                    error_lines.append(line.strip())
                    # Get next few lines for context
                    for j in range(1, 6):
                        if i + j < len(lines):
                            context_lines.append(lines[i + j].strip())
                    break
                elif "Error:" in line or "error:" in line:
                    error_lines.append(line.strip())
                    if len(error_lines) >= 3:
                        break

            # Also look for "l.XXX" line number indicator
            for line in lines:
                if line.startswith("l.") and line[2:].split()[0].isdigit():
                    error_lines.append(line.strip())
                    break

        except Exception as e:
            logger.warning(f"Failed to parse log file: {e}")

    result_parts = []
    if error_lines:
        result_parts.append("\n".join(error_lines))
    if context_lines:
        result_parts.append("Context: " + " | ".join(context_lines[:3]))

    if result_parts:
        return " ".join(result_parts)

    if stderr:
        return stderr[:500]

    return "Unknown LaTeX compilation error"


class LaTeXCompilationError(Exception):
    """Raised when LaTeX compilation fails."""

    pass

