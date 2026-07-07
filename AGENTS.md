# Doc Converter — AGENTS.md

## Quick start

```bash
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
streamlit run app.py          # or: bash run_app.sh
```

Requires **pandoc** system package (`brew install pandoc` / `apt-get install pandoc`).

## Repo structure

| File | Role |
|---|---|
| `app.py` | Streamlit UI, file upload, routes conversion by extension |
| `config.py` | Logging, `TEMP_DIR = Path("temp_files")`, `DoclingManager` singleton |
| `converters/pandoc_converter.py` | `.md`/`.html`/`.htm`/`.txt` → `.docx` via pypandoc + python-docx |
| `converters/docling_converter.py` | `.docx`/`.doc`/`.xls`/`.xlsx`/`.csv`/`.pdf` → `.md` via Docling AI |
| `converters/kroki_renderer.py` | Renders `` ```mermaid `` / `` ```plantuml `` blocks by calling the Kroki HTTP API |

## Conversion routing (in `app.py`)

- Input ends in `.md`/`.html`/`.markdown`/`.htm`/`.txt` → **Pandoc** path → output `.docx`
- Input ends in `.docx`/`.doc`/`.xls`/`.xlsx`/`.csv`/`.pdf` → **Docling** path → output `.md`

## Quirks & gotchas

- **No tests, no linter, no type checker, no CI.** Do not try to run them.
- **No `.gitignore`.** Add one before committing if `temp_files/` or `__pycache__` would be bothersome.
- **No version pins** in `requirements.txt`. Install resolves latest.
- **Docling** initializes a heavy AI model on first call (~CPU/RAM heavy) — `DoclingManager` caches it as a singleton (`config.py:12`).
- **Temp files** (`temp_files/`) are cleaned via `cleanup_temp_files()` in `app.py`, not automatically.
- **YAML frontmatter** in Markdown is stripped before Pandoc conversion (`pandoc_converter.py:_strip_yaml_frontmatter`) to avoid Pandoc Exit Code 64.
- **Table borders** are injected into output DOCX via OXML manipulation (`pandoc_converter.py:_set_table_borders`).
- **Kroki renderer** (`kroki_renderer.py`) calls `https://kroki.io` over HTTP — requires internet. Disable via the UI checkbox. On failure, original diagram code blocks are preserved as-is.
- **SVG temp files** (`kroki_*.svg`) created by diagram rendering live alongside the input file and are auto-cleaned in `convert_to_docx`'s `finally` block.
- **Primary docs** live in `GEMINI.md`, not `README.md`.

## Dependencies

```
streamlit, docling, pypandoc, pathlib, python-docx, requests   (requirements.txt)
pandoc                                                 (system, listed in packages.txt)
```

No lockfile — `pip install` each time for consistency.
