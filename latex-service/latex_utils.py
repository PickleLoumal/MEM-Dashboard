"""
LaTeX Utility Functions

Provides LaTeX-specific utilities: escaping, compilation, and file handling.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess
from pathlib import Path
from tempfile import mkdtemp

from config import config

logger = logging.getLogger(__name__)


def _extract_text_from_json(text: str) -> str:
    """
    Extract plain text from JSON-formatted string if applicable.

    Some database fields store JSON like:
    {"raw_text": "actual content...", "parsed": {...}}

    This function detects JSON and extracts the raw_text field.

    Args:
        text: Input text (may be JSON or plain text)

    Returns:
        Extracted raw_text if JSON, otherwise original text
    """
    if not text or not isinstance(text, str):
        return text or ""

    text = text.strip()

    # Quick check: does it look like JSON?
    if not (text.startswith("{") and text.endswith("}")):
        return text

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            # Try to get raw_text field
            if "raw_text" in data:
                return data["raw_text"]
            # Or try common alternatives
            if "text" in data:
                return data["text"]
            if "content" in data:
                return data["content"]
        # If parsed but no text field found, return original
        return text
    except (json.JSONDecodeError, TypeError):
        # Not valid JSON, return as-is
        return text


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


def markdown_to_latex(text: str | None) -> str:
    """
    Convert Markdown formatting to LaTeX using pypandoc.

    Handles all Markdown syntax from AI-generated content:
    - **bold** → \\textbf{bold}
    - *italic* → \\textit{italic}
    - [text](url) → proper hyperlinks
    - [[n]](url) → citation format
    - - list items → \\item

    Also handles JSON-formatted fields by extracting raw_text.

    Args:
        text: Markdown-formatted text (or JSON containing raw_text)

    Returns:
        LaTeX-formatted string
    """
    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

    # Extract text from JSON if applicable
    text = _extract_text_from_json(text)

    text = text.strip()
    if not text:
        return ""

    try:
        import pypandoc

        # Convert Markdown to LaTeX using pandoc
        # Use 'latex' output format for body content (no document wrapper)
        latex = pypandoc.convert_text(
            text,
            to="latex",
            format="markdown",
            extra_args=[
                "--wrap=none",  # Don't wrap lines
            ],
        )

        # Clean up pandoc output
        latex = latex.strip()

        # Remove pandoc-specific commands that LaTeX doesn't know
        # \tightlist is used by pandoc for compact lists
        latex = latex.replace(r"\tightlist", "")

        # Remove empty lines that might be left after removing commands
        latex = re.sub(r"\n\s*\n\s*\n", "\n\n", latex)

        return latex

    except ImportError:
        logger.warning("pypandoc not available, falling back to basic escaping")
        return _markdown_to_latex_fallback(text)
    except Exception as e:
        logger.warning(f"pypandoc conversion failed: {e}, falling back to basic escaping")
        return _markdown_to_latex_fallback(text)


def _markdown_to_latex_fallback(text: str) -> str:
    """
    Fallback Markdown to LaTeX conversion when pypandoc is unavailable.

    Handles basic patterns:
    - **bold** → \\textbf{bold}
    - *italic* → \\textit{italic}
    - [[n]](url) → superscript citation

    Args:
        text: Markdown-formatted text

    Returns:
        LaTeX-formatted string with basic conversion
    """
    # Use UUID-like placeholders that won't be affected by escape_latex
    # (only contain alphanumeric characters)
    BOLD_START = "XBOLDSTARTX"
    BOLD_END = "XBOLDENDX"
    ITALIC_START = "XITALICSTARTX"
    ITALIC_END = "XITALICENDX"
    CITE_PREFIX = "XCITEX"

    # Step 1: Handle citation links [[n]](url) → placeholder for superscript
    def citation_replace(match: re.Match) -> str:
        num = match.group(1).strip("[]")
        return f"{CITE_PREFIX}{num}{CITE_PREFIX}"

    text = re.sub(r"\[\[(\d+)\]\]\([^)]+\)", citation_replace, text)
    text = re.sub(r"\[(\d+)\]\([^)]+\)", citation_replace, text)

    # Step 2: Handle regular links [text](url) → text only
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Step 3: Bold **text** → placeholder
    text = re.sub(r"\*\*([^*]+)\*\*", rf"{BOLD_START}\1{BOLD_END}", text)

    # Step 4: Italic *text* → placeholder (not matching ** for bold)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", rf"{ITALIC_START}\1{ITALIC_END}", text)

    # Step 5: Escape LaTeX special characters
    text = escape_latex(text)

    # Step 6: Restore formatting (after escaping, placeholders are intact)
    text = text.replace(BOLD_START, r"\textbf{")
    text = text.replace(BOLD_END, "}")
    text = text.replace(ITALIC_START, r"\textit{")
    text = text.replace(ITALIC_END, "}")

    # Step 7: Restore citations as superscript
    # Find all XCITEX{num}XCITEX patterns and convert to [superscript]
    text = re.sub(
        rf"{CITE_PREFIX}(\d+){CITE_PREFIX}",
        r"[\\textsuperscript{\1}]",
        text,
    )

    return text


def escape_latex_preserve_newlines(text: str | None) -> str:
    """
    Convert Markdown to LaTeX and preserve paragraph breaks.

    Converts double newlines to LaTeX paragraph breaks (\\par).
    Single newlines are converted to spaces.
    Handles Markdown formatting (bold, italic, links, citations).
    Also handles JSON-formatted fields by extracting raw_text.

    Args:
        text: Input text (may contain Markdown or JSON)

    Returns:
        LaTeX-safe string with preserved paragraphs and formatting
    """
    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

    # Extract text from JSON if applicable
    text = _extract_text_from_json(text)

    if not text:
        return ""

    # Step 1: Handle bullet points - convert to LaTeX itemize
    lines = text.split("\n")
    processed_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        # Check for markdown bullet points
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                processed_lines.append("\\begin{itemize}[leftmargin=*,nosep]")
                in_list = True
            # Convert bullet to \item
            item_content = stripped[2:]  # Remove "- " or "* "
            processed_lines.append(f"\\item {markdown_to_latex(item_content)}")
        else:
            if in_list and stripped:
                # End of list
                processed_lines.append("\\end{itemize}")
                in_list = False
            processed_lines.append(line)

    if in_list:
        processed_lines.append("\\end{itemize}")

    text = "\n".join(processed_lines)

    # Step 2: Split into paragraphs
    paragraphs = re.split(r"\n\s*\n", text)

    # Step 3: Process each paragraph
    escaped_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue

        # Check if this is an itemize block (already processed)
        if p.startswith("\\begin{itemize}") or "\\item" in p:
            escaped_paragraphs.append(p)
        else:
            # Regular paragraph: convert markdown and escape
            escaped = markdown_to_latex(p.replace("\n", " "))
            escaped_paragraphs.append(escaped)

    return r"\par ".join(escaped_paragraphs)


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

