import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("doc-converter")

TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)
