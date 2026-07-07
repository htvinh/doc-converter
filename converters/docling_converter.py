from pathlib import Path
from config import logger
from markitdown import MarkItDown

_converter = MarkItDown()

def convert_to_markdown(input_path: Path, output_path: Path) -> bool:
    try:
        logger.info(f"Starting MarkItDown conversion: {input_path} -> {output_path}")

        result = _converter.convert(str(input_path))
        markdown_content = result.text_content

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        logger.info("MarkItDown conversion successful.")
        return True
    except Exception as e:
        logger.error(f"MarkItDown conversion failed: {str(e)}", exc_info=True)
        return False

