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


def markdown_to_latex(text: str | None) -> str:
    """
    Convert Markdown formatting to LaTeX before escaping.

    Handles common Markdown syntax from AI-generated content:
    - **bold** → \\textbf{bold}
    - *italic* → \\textit{italic}
    - [text](url) → text\\footnote{url}
    - [[n]](url) → citation format
    - - list items → \\item

    Args:
        text: Markdown-formatted text

    Returns:
        LaTeX-formatted string
    """
    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

    # Step 1: Extract and protect URLs/citations before any processing
    # Store citations for footnotes: [[n]](url) or [n](url)
    citations: dict[str, str] = {}
    citation_counter = [0]  # Use list to allow mutation in closure

    def extract_citation(match: re.Match) -> str:
        """Extract citation and store URL for footnote."""
        bracket_content = match.group(1)  # The [n] or [[n]] content
        url = match.group(2)
        citation_counter[0] += 1
        key = f"__CITE_{citation_counter[0]}__"
        citations[key] = url
        # Return just the citation number in superscript
        # Extract just the number from [[n]] or [n]
        num = re.sub(r"[\[\]]", "", bracket_content)
        return f"__CITEREF_{num}_{citation_counter[0]}__"

    # Match [[n]](url) or [n](url) citation patterns
    text = re.sub(r"\[(\[?\d+\]?)\]\(([^)]+)\)", extract_citation, text)

    # Step 2: Handle inline links [text](url) → text (see footnote)
    def convert_link(match: re.Match) -> str:
        """Convert markdown link to text with footnote marker."""
        link_text = match.group(1)
        url = match.group(2)
        citation_counter[0] += 1
        key = f"__LINK_{citation_counter[0]}__"
        citations[key] = url
        return f"{link_text}__FNREF_{citation_counter[0]}__"

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", convert_link, text)

    # Step 3: Convert Markdown formatting BEFORE LaTeX escaping
    # Bold: **text** or __text__
    bold_pattern = r"\*\*([^*]+)\*\*|__([^_]+)__"

    def bold_replace(match: re.Match) -> str:
        content = match.group(1) or match.group(2)
        return f"__BOLD_START__{content}__BOLD_END__"

    text = re.sub(bold_pattern, bold_replace, text)

    # Italic: *text* or _text_ (but not inside words)
    italic_pattern = r"(?<![*_])\*([^*]+)\*(?![*_])|(?<![*_])_([^_]+)_(?![*_])"

    def italic_replace(match: re.Match) -> str:
        content = match.group(1) or match.group(2)
        return f"__ITALIC_START__{content}__ITALIC_END__"

    text = re.sub(italic_pattern, italic_replace, text)

    # Step 4: Now escape LaTeX special characters
    text = escape_latex(text)

    # Step 5: Restore LaTeX formatting commands
    text = text.replace("__BOLD_START__", r"\textbf{")
    text = text.replace("__BOLD_END__", "}")
    text = text.replace("__ITALIC_START__", r"\textit{")
    text = text.replace("__ITALIC_END__", "}")

    # Step 6: Restore citations as superscript references
    for i in range(1, citation_counter[0] + 1):
        # Citation references: [n] → superscript
        cite_ref_pattern = f"__CITEREF_(\\d+)_{i}__"
        text = re.sub(cite_ref_pattern, r"[\\textsuperscript{\1}]", text)

        # Footnote references for links
        fn_ref = f"__FNREF_{i}__"
        if fn_ref in text:
            url = citations.get(f"__LINK_{i}__", "")
            # Escape URL for LaTeX (already escaped, just add footnote)
            text = text.replace(fn_ref, "")  # Remove marker, URL in citation

    return text


def escape_latex_preserve_newlines(text: str | None) -> str:
    """
    Convert Markdown to LaTeX and preserve paragraph breaks.

    Converts double newlines to LaTeX paragraph breaks (\\par).
    Single newlines are converted to spaces.
    Handles Markdown formatting (bold, italic, links, citations).

    Args:
        text: Input text (may contain Markdown)

    Returns:
        LaTeX-safe string with preserved paragraphs and formatting
    """
    if text is None:
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

