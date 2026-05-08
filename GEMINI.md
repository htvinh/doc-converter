# Doc Converter

A Streamlit-based web application for seamless document conversion.

## Project Overview
A production-grade Streamlit application for document conversion, featuring high-fidelity output and robust error handling.

### Core Technologies
- **Streamlit**: Web interface with session-safe operations.
- **Pandoc (via pypandoc)**: Handles Markdown/HTML to DOCX.
- **Docling**: Advanced AI-powered document extraction for DOCX/DOC to Markdown.
- **Logging**: Centralized system logging for monitoring and debugging.

## Architecture
- `app.py`: Streamlit UI logic with safe file handling and UX enhancements.
- `config.py`: Centralized configuration, logging setup, and `DoclingManager` (Singleton) to optimize resource usage.
- `converters/`: Modular conversion logic with explicit error handling.

## Development Setup

### Prerequisites
- Python 3.9+
- **Pandoc**: Must be installed on the system (e.g., `brew install pandoc` or `apt-get install pandoc`).
- **Docling**: requires significant resources (CPU/RAM) for model initialization.

### Installation
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the App
```bash
streamlit run app.py
```

## Conventions
- **Resource Management**: Use the `DoclingManager` to avoid re-initializing heavy models.
- **Error Handling**: Every conversion must be logged; use `try-except` blocks with `logger.error(..., exc_info=True)`.
- **Cleanup**: Provide mechanisms (manual or automated) to clear `temp_files/`.
- **Typing**: Use Python type hints for better maintainability.

