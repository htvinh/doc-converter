import pypandoc
import re
from pathlib import Path
from config import logger
from converters.kroki_renderer import render_diagrams
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def _set_border(element, border_name: str):
    border = OxmlElement(f'w:{border_name}')
    border.set(qn('w:val'), 'single')
    border.set(qn('w:sz'), '4')
    border.set(qn('w:space'), '0')
    border.set(qn('w:color'), '000000')
    element.append(border)

def _set_table_borders(table):
    tbl = table._tbl
    tblPr = tbl.find(qn('w:tblPr'))
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        tbl.insert(0, tblPr)

    # Remove the style reference — Pandoc sets "Table" which is a
    # no-border style that can override our explicit borders.
    style_el = tblPr.find(qn('w:tblStyle'))
    if style_el is not None:
        tblPr.remove(style_el)

    existing = tblPr.find(qn('w:tblBorders'))
    if existing is not None:
        tblPr.remove(existing)

    tblBorders = OxmlElement('w:tblBorders')
    tblPr.append(tblBorders)
    for name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        _set_border(tblBorders, name)

    for row in table.rows:
        for cell in row.cells:
            tcPr = cell._tc.find(qn('w:tcPr'))
            if tcPr is None:
                tcPr = OxmlElement('w:tcPr')
                cell._tc.insert(0, tcPr)
            existing = tcPr.find(qn('w:tcBorders'))
            if existing is not None:
                tcPr.remove(existing)
            tcBorders = OxmlElement('w:tcBorders')
            tcPr.append(tcBorders)
            for name in ['top', 'left', 'bottom', 'right']:
                _set_border(tcBorders, name)

def _apply_borders_to_docx(file_path: Path):
    """
    Opens a DOCX file and applies borders to all tables.
    """
    try:
        doc = Document(str(file_path))
        for table in doc.tables:
            _set_table_borders(table)
        doc.save(str(file_path))
        logger.info(f"Successfully applied borders to tables in {file_path.name}")
    except Exception as e:
        logger.warning(f"Failed to apply table borders: {e}")

def _strip_yaml_frontmatter(content: str) -> str:
    """
    Surgically removes YAML frontmatter if it exists to avoid Pandoc Exit Code 64.
    Frontmatter must start at the very first character of the file.
    """
    # More robust regex: 
    # ^---[ \t]*\r?\n  : Starts with --- followed by optional spaces and a newline
    # (.*?)            : Non-greedy match for the content
    # \r?\n---[ \t]*\r?\n : Ends with a newline, ---, optional spaces, and a newline
    robust_regex = r'^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n'
    
    if content.startswith('---'):
        cleaned = re.sub(robust_regex, '', content, count=1, flags=re.DOTALL)
        if cleaned != content:
            logger.info("YAML frontmatter successfully identified and stripped.")
            return cleaned
        else:
            logger.warning("File starts with '---' but closing '---' not found or malformed. Trying aggressive strip.")
            # Aggressive fallback: strip everything between the first and second '---' lines
            lines = content.splitlines(keepends=True)
            if len(lines) > 0 and lines[0].strip() == '---':
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        logger.info(f"Aggressively stripped YAML from line 1 to {i+1}.")
                        return "".join(lines[i+1:])
    return content

def convert_to_docx(input_path: Path, output_path: Path, enable_kroki: bool = True) -> bool:
    """
    Converts a file to DOCX using Pandoc with automatic YAML correction.
    If enable_kroki is True, renders Mermaid/PlantUML diagrams via Kroki.
    """
    try:
        logger.info(f"Starting Pandoc conversion: {input_path} -> {output_path}")
        
        # Check if pandoc is available
        try:
            pypandoc.get_pandoc_version()
        except OSError:
            logger.error("Pandoc is not installed or not in PATH.")
            return False

        # Pre-process for Markdown/Text files to avoid YAML errors
        if input_path.suffix.lower() in [".md", ".markdown", ".txt"]:
            logger.info(f"Cleaning YAML frontmatter for {input_path.name}")
            try:
                content = input_path.read_text(encoding="utf-8")
                cleaned_content = _strip_yaml_frontmatter(content)
                if enable_kroki:
                    cleaned_content = render_diagrams(cleaned_content, input_path.parent)
                
                # Write to a temporary 'clean' file to keep original intact
                clean_path = input_path.with_name(f"clean_{input_path.name}")
                clean_path.write_text(cleaned_content, encoding="utf-8")
                
                # Use the clean file for conversion
                # Specifying format 'markdown-yaml_metadata_block+pipe_tables+grid_tables+multiline_tables' 
                # tells Pandoc to ignore YAML blocks but support all table types.
                pypandoc.convert_file(
                    str(clean_path), 
                    'docx', 
                    format='markdown-yaml_metadata_block+pipe_tables+grid_tables+multiline_tables' if input_path.suffix.lower() in [".md", ".markdown"] else None,
                    outputfile=str(output_path)
                )
                
                # Cleanup clean file and diagram SVGs
                clean_path.unlink()
                for f in input_path.parent.glob("kroki_*.svg"):
                    f.unlink()
                
                # Post-process: Add borders
                _apply_borders_to_docx(output_path)
                
                logger.info("Pandoc conversion (with YAML cleaning and table support) successful.")
                return True
            except Exception as e:
                logger.warning(f"YAML cleaning or specific format conversion failed, attempting standard conversion: {e}")

        # Standard conversion for non-markdown or if cleaning skipped
        pypandoc.convert_file(
            str(input_path), 
            'docx', 
            format='markdown-yaml_metadata_block+pipe_tables+grid_tables+multiline_tables' if input_path.suffix.lower() in [".md", ".markdown"] else None,
            outputfile=str(output_path)
        )
        
        # Post-process: Add borders
        _apply_borders_to_docx(output_path)
        
        logger.info("Pandoc conversion successful.")
        return True

    except RuntimeError as re:
        error_msg = str(re)
        if "exitcode \"64\"" in error_msg and "YAML metadata" in error_msg:
            logger.error(f"Pandoc YAML Error: Malformed metadata in {input_path.name}. Automatic cleaning attempted but failed.")
        else:
            logger.error(f"Pandoc Runtime Error: {error_msg}")
        return False
    except Exception as e:
        logger.error(f"Pandoc conversion failed: {str(e)}", exc_info=True)
        return False
    finally:
        for f in input_path.parent.glob("kroki_*.svg"):
            f.unlink()


