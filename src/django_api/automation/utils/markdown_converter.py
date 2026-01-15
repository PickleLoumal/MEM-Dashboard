import re

from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor


def add_formatted_text(paragraph, text):
    """Add formatted text to paragraph with support for bold, italic, and inline code"""
    code_parts = re.split(r"(`[^`]*`)", text)

    for code_part in code_parts:
        if code_part.startswith("`") and code_part.endswith("`") and len(code_part) >= 2:
            run = paragraph.add_run(code_part[1:-1])
            run.font.name = "Courier New"
        else:
            bold_parts = re.split(r"(\*\*[^*]*\*\*)", code_part)

            for bold_part in bold_parts:
                if bold_part.startswith("**") and bold_part.endswith("**") and len(bold_part) >= 4:
                    bold_content = bold_part[2:-2]
                    italic_parts = re.split(r"(\*[^*]+\*)", bold_content)

                    for italic_part in italic_parts:
                        if (
                            italic_part.startswith("*")
                            and italic_part.endswith("*")
                            and len(italic_part) >= 3
                        ):
                            run = paragraph.add_run(italic_part[1:-1])
                            run.bold = True
                            run.italic = True
                        elif italic_part:
                            run = paragraph.add_run(italic_part)
                            run.bold = True
                else:
                    italic_parts = re.split(r"(\*[^*]+\*)", bold_part)

                    for italic_part in italic_parts:
                        if (
                            italic_part.startswith("*")
                            and italic_part.endswith("*")
                            and len(italic_part) >= 3
                        ):
                            run = paragraph.add_run(italic_part[1:-1])
                            run.italic = True
                        elif italic_part:
                            paragraph.add_run(italic_part)


def convert_markdown_to_word(markdown_text, doc):
    """Convert Markdown text to Word document"""
    lines = markdown_text.split("\n")
    in_code_block = False
    in_table = False
    table_obj = None

    for line in lines:
        # Code block handling
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            p = doc.add_paragraph(line)
            for run in p.runs:
                run.font.name = "Courier New"
                run.font.size = Pt(10)
            continue

        # Table handling
        if "|" in line and line.strip().startswith("|"):
            if not in_table:
                in_table = True
                cells = [cell.strip() for cell in line.strip().split("|")[1:-1]]
                table_obj = doc.add_table(rows=1, cols=len(cells))
                table_obj.style = "Table Grid"
                for i, cell_text in enumerate(cells):
                    table_obj.rows[0].cells[i].text = cell_text
            elif line.strip().replace("|", "").replace("-", "").replace(" ", "") == "":  # Separator
                continue
            else:
                cells = [cell.strip() for cell in line.strip().split("|")[1:-1]]
                row_cells = table_obj.add_row().cells
                for i, cell_text in enumerate(cells):
                    if i < len(row_cells):
                        row_cells[i].text = cell_text
            continue
        if in_table:
            in_table = False
            table_obj = None

        # Empty lines
        if not line.strip():
            doc.add_paragraph()
            continue

        # Headings
        if line.startswith("# ") and not line.startswith("## "):
            doc.add_heading(line[2:].strip(), level=1)
        elif line.startswith("## ") and not line.startswith("### "):
            doc.add_heading(line[3:].strip(), level=2)
        elif line.startswith("### ") and not line.startswith("#### "):
            doc.add_heading(line[4:].strip(), level=3)

        # Lists
        elif re.match(r"^[ \t]*[-*+] ", line):
            bullet_text = re.sub(r"^[ \t]*[-*+] ", "", line)
            p = doc.add_paragraph(style="List Bullet")
            add_formatted_text(p, bullet_text)
        elif re.match(r"^[ \t]*\d+\. ", line):
            bullet_text = re.sub(r"^[ \t]*\d+\. ", "", line)
            p = doc.add_paragraph(style="List Number")
            add_formatted_text(p, bullet_text)

        # Horizontal rule
        elif line.strip() in ["---", "***", "___"]:
            p = doc.add_paragraph()
            p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            run = p.add_run("─" * 50)
            run.font.color.rgb = RGBColor(128, 128, 128)

        # Blockquote
        elif line.strip().startswith("> "):
            quote_text = line.strip()[2:]
            p = doc.add_paragraph()
            p.left_indent = Inches(0.5)
            add_formatted_text(p, quote_text)

        # Normal text
        elif line.strip():
            p = doc.add_paragraph()
            add_formatted_text(p, line.strip())

    return doc
