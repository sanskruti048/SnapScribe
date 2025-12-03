"""
Configuration settings for OCR Text Extractor.

This module defines all constants, paths, and configurable parameters
for the OCR pipeline, UI, and file handling.

All paths are relative or environment-based for cross-platform compatibility.
"""

import os
import platform
from pathlib import Path

# ============================================================================
# PROJECT PATHS (All relative for deployment)
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
TEMP_DIR = PROJECT_ROOT / ".tmp"
SAMPLES_DIR = PROJECT_ROOT / "samples"
SAMPLES_IMAGES_DIR = SAMPLES_DIR / "images"
SAMPLES_OUTPUTS_DIR = SAMPLES_DIR / "outputs"

# Ensure temp directory exists
TEMP_DIR.mkdir(exist_ok=True)


# ============================================================================
# TESSERACT CONFIGURATION (System Dependency)
# ============================================================================

# Path to Tesseract executable (Windows: tesseract.exe, Linux/Mac: tesseract)
# 
# IMPORTANT: Tesseract must be installed separately on the system.
# The app will try to find it in PATH first, then check common installation locations.
#
# Installation:
# - Windows: https://github.com/UB-Mannheim/tesseract/wiki
# - Linux: sudo apt-get install tesseract-ocr
# - macOS: brew install tesseract
#
# You can also set TESSERACT_PATH environment variable to override the default path.

TESSERACT_PATH = os.getenv("TESSERACT_PATH", None)

# If not set, try common installation locations
if not TESSERACT_PATH or not Path(TESSERACT_PATH).exists():
    COMMON_TESSERACT_PATHS = []
    
    if platform.system() == "Windows":
        COMMON_TESSERACT_PATHS = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
    elif platform.system() == "Darwin":  # macOS
        COMMON_TESSERACT_PATHS = [
            "/usr/local/bin/tesseract",
            "/opt/homebrew/bin/tesseract",  # Apple Silicon
        ]
    elif platform.system() == "Linux":
        COMMON_TESSERACT_PATHS = [
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
        ]
    
    # Try to find Tesseract in common locations
    for path in COMMON_TESSERACT_PATHS:
        if Path(path).exists():
            TESSERACT_PATH = path
            break

# ============================================================================
# POPPLER CONFIGURATION (System Dependency - Optional for PDF)
# ============================================================================

# Path to Poppler executable directory
# Poppler is OPTIONAL and only required for PDF processing.
# The app will work fine for image OCR without it.
#
# Installation:
# - Windows: https://github.com/oschwartz10612/poppler-windows/releases/
# - Linux: sudo apt-get install poppler-utils
# - macOS: brew install poppler
#
# You can set POPPLER_PATH environment variable to the bin directory path.

POPPLER_PATH = os.getenv("POPPLER_PATH", None)

# If not set, try common installation locations
if not POPPLER_PATH:
    COMMON_POPPLER_PATHS = []
    
    if platform.system() == "Windows":
        COMMON_POPPLER_PATHS = [
            r"C:\poppler\Library\bin",  # Conda/MinGW style
            r"C:\poppler\bin",
            r"C:\Program Files\poppler\bin",
            r"C:\Program Files (x86)\poppler\bin",
            os.path.expanduser("~\\Downloads\\bin"),
        ]
    elif platform.system() == "Darwin":  # macOS
        COMMON_POPPLER_PATHS = [
            "/usr/local/bin",
            "/opt/homebrew/bin",  # Apple Silicon
        ]
    elif platform.system() == "Linux":
        COMMON_POPPLER_PATHS = [
            "/usr/bin",
            "/usr/local/bin",
        ]
    
    # Try to find Poppler in common locations
    for path in COMMON_POPPLER_PATHS:
        path_obj = Path(path)
        if path_obj.exists():
            # Check for pdftoppm executable
            pdftoppm_exe = path_obj / ("pdftoppm.exe" if platform.system() == "Windows" else "pdftoppm")
            if pdftoppm_exe.exists():
                POPPLER_PATH = path
                break

# Ensure Poppler is in PATH if found
if POPPLER_PATH:
    if Path(POPPLER_PATH).exists():
        if POPPLER_PATH not in os.environ.get("PATH", ""):
            os.environ["PATH"] = str(POPPLER_PATH) + os.pathsep + os.environ.get("PATH", "")


# Default OCR language(s) - can be extended in Phase 2
DEFAULT_LANGUAGE = "eng"

# Supported languages (English only)
SUPPORTED_LANGUAGES = {
    "English": "eng",
}


# ============================================================================
# IMAGE PROCESSING SETTINGS
# ============================================================================

# Supported image formats for upload
SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

# Image processing parameters
IMAGE_PROCESSING = {
    "grayscale": True,              # Convert to grayscale before processing
    "threshold_enabled": True,      # Apply binary thresholding
    "threshold_value": 127,         # Binary threshold cutoff (0-255)
    "denoise_enabled": True,        # Apply denoising (fastNlMeansDenoising)
    "denoise_strength": 10,         # Strength of denoising (1-30)
    "deskew_enabled": False,        # Apply deskew (rotation correction)
    "max_angle": 10,                # Max rotation angle to detect/correct (degrees)
}

# Maximum image file size (in MB)
MAX_IMAGE_SIZE_MB = 10

# Supported PDF formats
SUPPORTED_PDF_FORMATS = {".pdf"}

# Maximum PDF file size (in MB)
MAX_PDF_SIZE_MB = 50

# Maximum images to process in batch (prevents overwhelming server)
MAX_BATCH_IMAGES = 20

# Phase 2: PDF page rendering settings
PDF_SETTINGS = {
    "dpi": 200,  # Higher DPI = better OCR but slower
    "first_page": None,  # None = all pages, or specify page number
    "last_page": None,   # None = all pages
}


# ============================================================================
# OCR SETTINGS
# ============================================================================

OCR_SETTINGS = {
    "lang": DEFAULT_LANGUAGE,
    "config": "--psm 3",  # PSM 3: Fully automatic page segmentation
}

# Optional: Use custom PSM (Page Segmentation Mode)
# PSM values (0-13):
# 0: Orientation and script detection only
# 1: Automatic page segmentation with OSD
# 3: Fully automatic page segmentation (default)
# 6: Uniform block of text
# 11: Sparse text


# ============================================================================
# TEXT POST-PROCESSING
# ============================================================================

POSTPROCESSING = {
    "remove_extra_whitespace": True,    # Collapse multiple spaces/tabs
    "fix_line_breaks": True,             # Normalize line endings
    "remove_empty_lines": False,         # Remove lines with only whitespace
    "spellcheck_enabled": False,         # Phase 2: spell correction (optional)
    "fix_common_ocr_errors": True,       # Phase 2: fix common OCR mistakes
}

# Phase 2: Spell checker settings
SPELLCHECKER_CONFIG = {
    "enabled": False,                    # Must be explicitly enabled
    "language": "en",
    "max_edit_distance": 2,
}


# ============================================================================
# STREAMLIT UI SETTINGS
# ============================================================================

STREAMLIT_CONFIG = {
    "page_title": "SnapScribe OCR",
    "page_icon": "📄",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# UI text and labels
UI_STRINGS = {
    "title": "📄 SnapScribe OCR",
    "subtitle": "Extract text from images with intelligent preprocessing",
    "upload_label": "Upload an image (JPEG/PNG)",
    "processing_message": "🔄 Processing your image...",
    "success_message": "✅ OCR complete!",
    "error_message": "❌ An error occurred:",
    "download_label": "Download extracted text as .txt",
    "no_image_warning": "⚠️ Please upload an image first.",
}


# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
