import logging
import sys
from pathlib import Path
from docling.document_converter import DocumentConverter

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("doc-converter")

# Constants
TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)

# Docling is heavy to initialize, so we use a singleton-like pattern or cache it
class DoclingManager:
    _instance = None

    @classmethod
    def get_converter(cls):
        if cls._instance is None:
            logger.info("Initializing Docling DocumentConverter...")
            cls._instance = DocumentConverter()
        return cls._instance
