from pathlib import Path
from config import logger, DoclingManager

def convert_to_markdown(input_path: Path, output_path: Path) -> bool:
    """
    Converts a DOCX/DOC file to Markdown using Docling with production-level standards.
    """
    try:
        logger.info(f"Starting Docling conversion: {input_path} -> {output_path}")
        
        converter = DoclingManager.get_converter()
        result = converter.convert(input_path)
        markdown_content = result.document.export_to_markdown()
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        logger.info("Docling conversion successful.")
        return True
    except Exception as e:
        logger.error(f"Docling conversion failed: {str(e)}", exc_info=True)
        return False

