"""
SnapScribe OCR - Main Streamlit Application

Phase 1 & 2: Core MVP + Extended Features

A clean, production-ready OCR-based text extraction tool with:
- Single image OCR with preprocessing
- Multi-language OCR support (Phase 2)
- Batch image processing (Phase 2)
- PDF to OCR conversion (Phase 2)
- Text cleanup and spell correction (Phase 2)
- Bounding box visualization (Phase 2)

Usage:
    streamlit run app.py

Requirements:
    - Python 3.9+
    - Tesseract OCR installed on system
    - Dependencies from requirements.txt
"""

import logging
import io
from pathlib import Path

import streamlit as st
from PIL import Image

# Local imports
from config.settings import (
    STREAMLIT_CONFIG,
    UI_STRINGS,
    IMAGE_PROCESSING,
    POSTPROCESSING,
    SUPPORTED_LANGUAGES,
    SPELLCHECKER_CONFIG,
)
from core import preprocessing, ocr_engine, postprocessing
from utils import file_utils, pdf_utils


# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# STREAMLIT PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title=STREAMLIT_CONFIG["page_title"],
    page_icon=STREAMLIT_CONFIG["page_icon"],
    layout=STREAMLIT_CONFIG["layout"],
    initial_sidebar_state=STREAMLIT_CONFIG["initial_sidebar_state"],
)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None
if "preprocessed_image" not in st.session_state:
    st.session_state.preprocessed_image = None
if "batch_results" not in st.session_state:
    st.session_state.batch_results = []
if "pdf_images" not in st.session_state:
    st.session_state.pdf_images = []


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def display_text_statistics(text: str) -> None:
    """
    Display text statistics in three columns (characters, words, lines).
    
    Args:
        text: The extracted text to analyze
    """
    stats = postprocessing.get_text_stats(text)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Characters", stats["character_count"])
    with col2:
        st.metric("Words", stats["word_count"])
    with col3:
        st.metric("Lines", stats["line_count"])


def create_download_button(text: str, filename: str, label: str = "⬇️ Download as TXT") -> None:
    """
    Create a download button for extracted text.
    
    Args:
        text: The text content to download
        filename: Output filename
        label: Button label (default: "⬇️ Download as TXT")
    """
    st.download_button(
        label=label,
        data=text,
        file_name=filename,
        mime="text/plain",
        use_container_width=True,
    )


def build_preprocess_config() -> dict:
    """
    Build preprocessing configuration from sidebar settings.
    
    Returns:
        Dictionary with preprocessing parameters
    """
    return {
        "grayscale": st.session_state.get("grayscale_enabled", False),
        "denoise_enabled": st.session_state.get("denoise_enabled", False),
        "denoise_strength": st.session_state.get("denoise_strength", 5),
        "threshold_enabled": st.session_state.get("threshold_enabled", False),
        "threshold_value": st.session_state.get("threshold_value", 127),
        "deskew_enabled": st.session_state.get("deskew_enabled", False),
    }


def validate_pdf_support() -> bool:
    """
    Validate that PDF support is available and Poppler is configured.
    Shows appropriate error message if support is unavailable.
    
    Returns:
        True if PDF support is available, False otherwise
    """
    if not pdf_utils.PDF_SUPPORT_AVAILABLE:
        st.error("❌ PDF support not available. Install with: `pip install pdf2image`")
        return False
    
    if not pdf_utils.POPPLER_CONFIGURED:
        st.error("""
        ❌ **Poppler is not installed or not in PATH**
        
        Poppler is a required system dependency for PDF processing.
        
        **To install Poppler:**
        
        1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/
        2. Extract the ZIP file to a folder (e.g., `C:\\poppler`)
        3. Set environment variable:
           - Variable name: `POPPLER_PATH`
           - Variable value: `C:\\path\\to\\poppler\\bin`
        4. Restart the Streamlit app
        
        **See POPPLER_SETUP.md for detailed instructions.**
        """)
        st.info("Other tabs (Single Image & Batch Processing) work without Poppler.")
        return False
    
    return True


def process_single_image(image: Image.Image, preprocess_config: dict, selected_language: str) -> None:
    """
    Process a single image and extract text.
    Updates session state with extracted text and preprocessed image.
    
    Args:
        image: PIL Image object
        preprocess_config: Preprocessing configuration dictionary
        selected_language: OCR language code
    """
    try:
        with st.spinner("🔄 Processing image..."):
            # Preprocess
            st.session_state.preprocessed_image = preprocessing.preprocess_image(
                image, config=preprocess_config
            )
            
            # OCR extraction
            st.session_state.extracted_text = ocr_engine.extract_text(
                st.session_state.preprocessed_image, 
                language=selected_language
            )
            
            # Post-processing
            st.session_state.extracted_text = postprocessing.clean_text(
                st.session_state.extracted_text,
                remove_extra_spaces=st.session_state.get("remove_spaces", True)
            )
        
        st.success("✅ OCR complete!")
        logger.info("OCR completed successfully")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        logger.error(f"OCR failed: {e}")


if "pdf_images" not in st.session_state:
    st.session_state.pdf_images = []


# ============================================================================
# SIDEBAR - SETTINGS & INFO
# ============================================================================

with st.sidebar:
    st.header("⚙️ Settings")

    # Preprocessing options
    st.subheader("Image Preprocessing")

    grayscale_enabled = st.checkbox(
        "Convert to Grayscale",
        value=IMAGE_PROCESSING["grayscale"],
        help="Convert image to grayscale before OCR"
    )

    denoise_enabled = st.checkbox(
        "Remove Noise",
        value=IMAGE_PROCESSING["denoise_enabled"],
        help="Apply noise reduction filter"
    )

    denoise_strength = st.slider(
        "Denoising Strength",
        min_value=1,
        max_value=30,
        value=IMAGE_PROCESSING["denoise_strength"],
        disabled=not denoise_enabled,
        help="Higher = more aggressive noise removal"
    )

    threshold_enabled = st.checkbox(
        "Apply Thresholding",
        value=IMAGE_PROCESSING["threshold_enabled"],
        help="Convert to black & white binary image"
    )

    threshold_value = st.slider(
        "Threshold Value",
        min_value=0,
        max_value=255,
        value=IMAGE_PROCESSING["threshold_value"],
        disabled=not threshold_enabled,
        help="Lower = more white, Higher = more black"
    )

    deskew_enabled = st.checkbox(
        "Auto-Correct Rotation",
        value=IMAGE_PROCESSING["deskew_enabled"],
        help="Automatically correct tilted images (slower)"
    )

    # Set language to English (only supported language)
    selected_lang_name = "English"
    selected_language = SUPPORTED_LANGUAGES[selected_lang_name]

    # Text postprocessing options
    st.subheader("Text Cleanup")

    remove_spaces = st.checkbox(
        "Remove Extra Spaces",
        value=POSTPROCESSING["remove_extra_whitespace"],
        help="Collapse multiple spaces/tabs"
    )

    fix_breaks = st.checkbox(
        "Normalize Line Breaks",
        value=POSTPROCESSING["fix_line_breaks"],
        help="Fix line ending styles"
    )

    fix_ocr_errors = st.checkbox(
        "Fix Common OCR Errors",
        value=POSTPROCESSING.get("fix_common_ocr_errors", True),
        help="Correct common OCR mistakes"
    )

    # Phase 2: Spell checker toggle
    spellcheck_enabled = st.checkbox(
        "Apply Spell Correction",
        value=SPELLCHECKER_CONFIG.get("enabled", False),
        help="Optional spell checking (experimental, slower)"
    )

    # Phase 2: Bounding box visualization
    st.subheader("Advanced Options")

    show_bounding_boxes = st.checkbox(
        "Show Text Region Boxes",
        value=False,
        help="Highlight detected text regions (Phase 2)"
    )

    # Info section
    st.divider()
    st.subheader("ℹ️ Information")
    st.markdown("""
    **SnapScribe OCR** - Text Extraction Tool
    
    Features:
    - Upload images (JPEG/PNG)
    - Adjust preprocessing for accuracy
    - Extract text in multiple languages
    - Batch process multiple files
    - Convert PDFs to text
    - Download results
    """)


# ============================================================================
# MAIN CONTENT AREA - TAB INTERFACE
# ============================================================================

st.title(UI_STRINGS["title"])
st.markdown(UI_STRINGS["subtitle"])

# Create tabs for different OCR modes
tab1, tab2, tab3 = st.tabs(["📸 Single Image", "📦 Batch Images", "📄 PDF to Text"])


# ============================================================================
# TAB 1: SINGLE IMAGE OCR (Phase 1 functionality)
# ============================================================================

with tab1:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📸 Upload Image")

        uploaded_file = st.file_uploader(
            "Choose an image file (JPEG/PNG)",
            type=list(file_utils.SUPPORTED_IMAGE_FORMATS),
            key="single_image_uploader"
        )

        if uploaded_file is None:
            st.info("👆 Upload an image to begin")
        else:
            # Load image
            image, error = file_utils.load_image(uploaded_file)

            if error:
                st.error(f"❌ Error: {error}")
            else:
                # Display original image
                st.subheader("Original Image")
                st.image(image, use_column_width=True)

                # Validate image for OCR
                is_valid, validation_error = ocr_engine.validate_image_for_ocr(image)
                if not is_valid:
                    st.warning(f"⚠️ {validation_error}")

    with col2:
        st.subheader("🔤 Extracted Text")

        if uploaded_file is not None:
            # Build preprocessing config from sidebar
            preprocess_config = {
                "grayscale": grayscale_enabled,
                "denoise_enabled": denoise_enabled,
                "denoise_strength": denoise_strength,
                "threshold_enabled": threshold_enabled,
                "threshold_value": threshold_value,
                "deskew_enabled": deskew_enabled,
            }

            # Process button
            if st.button("🚀 Extract Text", type="primary", use_container_width=True, key="single_extract"):

                # Show processing message
                with st.spinner("🔄 Processing your image..."):

                    try:
                        # Step 1: Preprocess image
                        logger.info("Starting image preprocessing...")
                        preprocessed_image = preprocessing.preprocess_image(image, config=preprocess_config)

                        # Step 2: Run OCR
                        logger.info(f"Running OCR with language: {selected_lang_name}")
                        extracted_text = ocr_engine.extract_text(
                            preprocessed_image,
                            language=selected_language
                        )

                        # Step 3: Post-process text
                        logger.info("Post-processing text...")
                        cleaned_text = postprocessing.clean_text(
                            extracted_text,
                            remove_extra_spaces=remove_spaces,
                            fix_breaks=fix_breaks,
                            normalize_quotes_mode=True,
                        )

                        # Step 3b: Fix OCR errors
                        if fix_ocr_errors:
                            cleaned_text = postprocessing.fix_common_ocr_errors(cleaned_text)

                        # Step 3c: Apply spell correction (optional)
                        if spellcheck_enabled:
                            try:
                                cleaned_text = postprocessing.apply_spell_correction(cleaned_text)
                            except Exception as e:
                                st.warning(f"Spell correction failed: {str(e)}")
                                logger.warning(f"Spell correction error: {e}")

                        # Store in session state
                        st.session_state.extracted_text = cleaned_text
                        st.session_state.preprocessed_image = preprocessed_image

                        st.success("✅ OCR complete!")
                        logger.info("OCR completed successfully")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        logger.error(f"OCR failed: {e}")

            # Display extracted text if available
            if st.session_state.extracted_text:
                # Text statistics
                display_text_statistics(st.session_state.extracted_text)

                # Text display
                st.text_area(
                    "Extracted Text:",
                    value=st.session_state.extracted_text,
                    height=250,
                    disabled=True,
                    key="text_display_single"
                )

                # Download button
                create_download_button(
                    st.session_state.extracted_text,
                    f"extracted_{Path(uploaded_file.name).stem}.txt"
                )

                # Phase 2: Show preprocessed image
                if st.checkbox("Show preprocessed image", value=False, key="show_preproc_single"):
                    st.image(st.session_state.preprocessed_image, use_column_width=True)

                # Phase 2: Show bounding boxes
                if show_bounding_boxes:
                    try:
                        with st.spinner("🔄 Generating text region boxes..."):
                            annotated_image = ocr_engine.get_annotated_image_with_boxes(
                                image,
                                language=selected_language
                            )
                            st.image(annotated_image, caption="Text Regions with Confidence Scores")
                    except Exception as e:
                        st.warning(f"Could not generate bounding boxes: {str(e)}")


# ============================================================================
# TAB 2: BATCH IMAGE PROCESSING (Phase 2)
# ============================================================================

with tab2:
    st.subheader("📦 Batch Image Processing")
    st.markdown("Upload multiple images and extract text from all at once.")

    # Batch file uploader
    batch_files = st.file_uploader(
        "Choose multiple images (JPEG/PNG)",
        type=list(file_utils.SUPPORTED_IMAGE_FORMATS),
        accept_multiple_files=True,
        key="batch_uploader"
    )

    if not batch_files:
        st.info("👆 Upload one or more images to process")
    else:
        st.info(f"Selected {len(batch_files)} image(s)")

        # Validate batch
        valid_files, validation_errors = file_utils.validate_batch_files(batch_files)

        if validation_errors:
            for filename, error in validation_errors:
                st.warning(f"⚠️ {filename}: {error}")

        if valid_files:
            # Build preprocessing config
            preprocess_config = {
                "grayscale": grayscale_enabled,
                "denoise_enabled": denoise_enabled,
                "denoise_strength": denoise_strength,
                "threshold_enabled": threshold_enabled,
                "threshold_value": threshold_value,
                "deskew_enabled": deskew_enabled,
            }

            # Process button
            if st.button("🚀 Process Batch", type="primary", use_container_width=True, key="batch_process"):

                progress_bar = st.progress(0)
                status_text = st.empty()

                batch_results = []
                errors = []

                # Load images
                loaded_images, load_errors = file_utils.load_batch_images(valid_files)
                errors.extend(load_errors)

                # Process each image
                for idx, (filename, image) in enumerate(loaded_images):
                    status_text.text(f"Processing {idx + 1}/{len(loaded_images)}: {filename}")
                    progress_bar.progress((idx + 1) / len(loaded_images))

                    try:
                        # Preprocess
                        preprocessed = preprocessing.preprocess_image(image, config=preprocess_config)

                        # OCR
                        text = ocr_engine.extract_text(preprocessed, language=selected_language)

                        # Post-process
                        text = postprocessing.clean_text(
                            text,
                            remove_extra_spaces=remove_spaces,
                            fix_breaks=fix_breaks,
                        )

                        if fix_ocr_errors:
                            text = postprocessing.fix_common_ocr_errors(text)

                        if spellcheck_enabled:
                            try:
                                text = postprocessing.apply_spell_correction(text)
                            except Exception:
                                pass  # Silently skip spell check on errors

                        batch_results.append({
                            'filename': filename,
                            'text': text,
                        })

                    except Exception as e:
                        errors.append((filename, str(e)))
                        logger.error(f"Batch processing error for {filename}: {e}")

                # Store results in session state
                st.session_state.batch_results = batch_results

                status_text.empty()
                progress_bar.empty()

                st.success(f"✅ Processed {len(batch_results)} image(s)")

                if errors:
                    st.warning(f"⚠️ {len(errors)} error(s) during processing:")
                    for filename, error in errors:
                        st.write(f"- {filename}: {error}")

            # Display batch results
            if st.session_state.batch_results:
                st.subheader("📋 Results")

                # Aggregated text
                aggregated = file_utils.aggregate_batch_results(st.session_state.batch_results)

                st.text_area(
                    "All Extracted Text:",
                    value=aggregated,
                    height=300,
                    disabled=True,
                )

                # Download options
                col_dl1, col_dl2 = st.columns(2)

                with col_dl1:
                    # Single concatenated file
                    st.download_button(
                        label="⬇️ Download as Single TXT",
                        data=aggregated,
                        file_name="batch_results.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )

                with col_dl2:
                    # ZIP archive
                    zip_path, error = file_utils.create_batch_zip(st.session_state.batch_results)
                    if zip_path and zip_path.exists():
                        with open(zip_path, 'rb') as zf:
                            st.download_button(
                                label="⬇️ Download as ZIP",
                                data=zf.read(),
                                file_name=zip_path.name,
                                mime="application/zip",
                                use_container_width=True,
                            )

                # Individual results in expandable sections
                st.subheader("Individual Results")
                for result in st.session_state.batch_results:
                    with st.expander(f"📄 {result['filename']}"):
                        st.text_area(
                            f"Text from {result['filename']}:",
                            value=result['text'],
                            height=200,
                            disabled=True,
                            key=f"batch_text_{result['filename']}"
                        )


# ============================================================================
# TAB 3: PDF TO TEXT (Phase 2)
# ============================================================================

with tab3:
    st.subheader("📄 PDF to Text Conversion")
    st.markdown("Convert PDF pages to text using OCR.")

    if not pdf_utils.PDF_SUPPORT_AVAILABLE:
        st.error("❌ PDF support not available. Install with: `pip install pdf2image`")
    elif not pdf_utils.POPPLER_CONFIGURED:
        st.error("""
        ❌ **Poppler is not installed or not in PATH**
        
        Poppler is a required system dependency for PDF processing.
        
        **To install Poppler:**
        
        1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/
        2. Extract the ZIP file to a folder (e.g., `C:\\poppler`)
        3. Set environment variable:
           - Variable name: `POPPLER_PATH`
           - Variable value: `C:\\path\\to\\poppler\\bin`
        4. Restart the Streamlit app
        
        **See POPPLER_SETUP.md for detailed instructions.**
        """)
        
        st.info("Other tabs (Single Image & Batch Processing) work without Poppler and don't require PDF support.")
    else:
        pdf_file = st.file_uploader(
            "Choose a PDF file",
            type=[".pdf"],
            key="pdf_uploader"
        )

        if pdf_file is None:
            st.info("👆 Upload a PDF to convert to text")
        else:
            # Get page count
            pdf_bytes = pdf_file.read()
            page_count, page_error = pdf_utils.get_pdf_page_count(pdf_bytes)

            if page_error:
                st.error(f"❌ Error: {page_error}")
            else:
                st.info(f"📄 PDF has {page_count} page(s)")

                # Page range selection
                col_pdf1, col_pdf2 = st.columns(2)
                with col_pdf1:
                    first_page = st.number_input(
                        "Start page",
                        min_value=1,
                        max_value=page_count,
                        value=1,
                        step=1
                    )

                with col_pdf2:
                    last_page = st.number_input(
                        "End page",
                        min_value=first_page,
                        max_value=page_count,
                        value=min(first_page + 5, page_count),  # Default to first 5 pages
                        step=1
                    )

                # DPI selection
                dpi = st.slider(
                    "PDF Rendering Quality (DPI)",
                    min_value=100,
                    max_value=300,
                    value=200,
                    step=50,
                    help="Higher = better quality but slower"
                )

                # Build preprocessing config
                preprocess_config = {
                    "grayscale": grayscale_enabled,
                    "denoise_enabled": denoise_enabled,
                    "denoise_strength": denoise_strength,
                    "threshold_enabled": threshold_enabled,
                    "threshold_value": threshold_value,
                    "deskew_enabled": deskew_enabled,
                }

                # Process button
                if st.button("🚀 Convert PDF to Text", type="primary", use_container_width=True, key="pdf_process"):

                    with st.spinner("🔄 Converting PDF pages to images..."):
                        # Convert PDF to images
                        images, pdf_error = pdf_utils.pdf_to_images(
                            pdf_bytes,
                            dpi=dpi,
                            first_page=first_page,
                            last_page=last_page
                        )

                        if pdf_error:
                            st.error(f"❌ PDF conversion error: {pdf_error}")
                        else:
                            st.session_state.pdf_images = images
                            st.success(f"✅ Converted {len(images)} page(s)")

                # Process pages if images are ready
                if st.session_state.pdf_images:
                    if st.button("🚀 Extract Text from Pages", type="primary", use_container_width=True, key="pdf_ocr"):

                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        pdf_results = []

                        # Process each page
                        for page_idx, page_image in enumerate(st.session_state.pdf_images):
                            page_num = first_page + page_idx

                            status_text.text(f"Processing page {page_num}...")
                            progress_bar.progress((page_idx + 1) / len(st.session_state.pdf_images))

                            try:
                                # Preprocess
                                preprocessed = preprocessing.preprocess_image(page_image, config=preprocess_config)

                                # OCR
                                text = ocr_engine.extract_text(preprocessed, language=selected_language)

                                # Post-process
                                text = postprocessing.clean_text(text, remove_extra_spaces=remove_spaces)

                                pdf_results.append({
                                    'filename': f"page_{page_num:04d}",
                                    'text': text,
                                })

                            except Exception as e:
                                st.error(f"Error processing page {page_num}: {str(e)}")
                                logger.error(f"PDF OCR error on page {page_num}: {e}")

                        status_text.empty()
                        progress_bar.empty()

                        # Display results
                        if pdf_results:
                            st.success(f"✅ Extracted text from {len(pdf_results)} page(s)")

                            # Aggregated text
                            aggregated = file_utils.aggregate_batch_results(pdf_results)

                            st.text_area(
                                "All Extracted Text:",
                                value=aggregated,
                                height=400,
                                disabled=True,
                            )

                            # Download button
                            st.download_button(
                                label="⬇️ Download as TXT",
                                data=aggregated,
                                file_name=f"{Path(pdf_file.name).stem}_extracted.txt",
                                mime="text/plain",
                                use_container_width=True,
                            )

                            # Individual page results
                            with st.expander("📄 View Individual Pages", expanded=False):
                                for result in pdf_results:
                                    with st.expander(result['filename']):
                                        st.text_area(
                                            f"Text from {result['filename']}:",
                                            value=result['text'],
                                            height=200,
                                            disabled=True,
                                            key=f"pdf_text_{result['filename']}"
                                        )


# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.85rem;'>
    <p>🔤 SnapScribe OCR • Phases 1 & 2 • Powered by Tesseract</p>
</div>
""", unsafe_allow_html=True)
