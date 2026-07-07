import streamlit as st
from pathlib import Path
from config import logger, TEMP_DIR
from converters.pandoc_converter import convert_to_docx
from converters.docling_converter import convert_to_markdown

# --- UI Configuration ---
st.set_page_config(
    page_title="Doc Converter Pro",
    page_icon="📄",
    layout="centered"
)

def cleanup_temp_files():
    """Removes files in TEMP_DIR that are older than a certain threshold (optional) 
    or just clears the current session's files.
    """
    for file in TEMP_DIR.glob("*"):
        try:
            file.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete {file}: {e}")

# --- Main App ---
st.title("📄 Doc Converter Pro")
st.subheader("Production-grade document conversion: Markdown, HTML, DOCX, XLSX, CSV, PDF and more!")
st.write("NO STRING ATTACHED, USE WITH CAUTION. ")    
st.write("ho.tuong.vinh@gmail.com")


# File uploader
uploaded_file = st.file_uploader(
    "Upload a document to convert", 
    type=["md", "html", "docx", "doc", "markdown", "htm", "xls", "xlsx", "csv", "txt", "pdf", "pptx", "ppt", "pptm", "pptx", "odt", "ods", "odp"],
    help="Supported formats: .md, .html, .docx, .doc, .markdown, .htm, .xls, .xlsx, .csv, .txt, .pdf, .pptx, .ppt, .pptm, .odt, .ods, .odp"
)

if uploaded_file:
    file_extension = Path(uploaded_file.name).suffix.lower()
    input_path = TEMP_DIR / uploaded_file.name

    # Save uploaded file safely
    try:
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logger.info(f"User uploaded: {uploaded_file.name}")
    except Exception as e:
        st.error("Failed to save uploaded file.")
        logger.error(f"File save error: {e}")
        st.stop()

    st.success(f"File ready: `{uploaded_file.name}`")

    # Diagram rendering toggle (only relevant for Pandoc/DOCX path)
    enable_kroki = st.checkbox(
        "Render Mermaid/PlantUML diagrams via Kroki",
        value=True,
        help="Requires internet access. Disable for offline or private documents.",
    )

    # Logic for conversion
    if file_extension in [".md", ".html", ".markdown", ".htm", ".txt"]:
        target_format = "DOCX"
        convert_func = convert_to_docx
        output_ext = ".docx"
        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif file_extension in [".docx", ".doc", ".xls", ".xlsx", ".csv", ".pdf", ".pptx", ".ppt", ".pptm", ".odt", ".ods", ".odp"]:
        target_format = "Markdown"
        convert_func = convert_to_markdown
        output_ext = ".md"
        mime_type = "text/markdown"
    else:
        st.error("Unsupported file type.")
        st.stop()

    if st.button(f"Convert to {target_format}", use_container_width=True):
        output_path = input_path.with_suffix(output_ext)
        
        with st.spinner(f"Converting to {target_format}..."):
            kwargs = {"enable_kroki": enable_kroki} if convert_func == convert_to_docx else {}
            success = convert_func(input_path, output_path, **kwargs)
            
            if success and output_path.exists():
                st.success(f"Conversion to {target_format} complete!")
                
                with open(output_path, "rb") as f:
                    st.download_button(
                        label=f"📥 Download {target_format}",
                        data=f,
                        file_name=output_path.name,
                        mime=mime_type,
                        use_container_width=True
                    )
            else:
                st.error(f"Conversion to {target_format} failed.")
                if target_format == "DOCX":
                    st.warning("Possible Issue: Malformed YAML metadata (Exit Code 64) or Pandoc missing. Check the logs for details.")
                else:
                    st.warning("Check the logs for detailed error information.")

