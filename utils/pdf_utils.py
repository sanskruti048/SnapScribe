"""
PDF utilities for OCR application.

Phase 2: PDF support with page-to-image conversion.

This module provides:
- PDF to image conversion
- Multi-page PDF handling
- Batch processing support
"""

import logging
import os
from typing import List, Optional, Tuple
from pathlib import Path
from PIL import Image
from io import BytesIO

from config.settings import PDF_SETTINGS, POPPLER_PATH

logger = logging.getLogger(__name__)

# Configure Poppler path if available
POPPLER_CONFIGURED = False
if POPPLER_PATH:
    if Path(POPPLER_PATH).exists():
        if POPPLER_PATH not in os.environ.get("PATH", ""):
            os.environ["PATH"] = POPPLER_PATH + os.pathsep + os.environ.get("PATH", "")
        POPPLER_CONFIGURED = True
        logger.info(f"Poppler path configured: {POPPLER_PATH}")
    else:
        logger.warning(f"Poppler path does not exist: {POPPLER_PATH}")
else:
    logger.info("POPPLER_PATH not set. Checking system PATH for Poppler...")

# Optional: PDF support (Phase 2)
try:
    from pdf2image import convert_from_path, convert_from_bytes
    PDF_SUPPORT_AVAILABLE = True
    logger.info("PDF support available (pdf2image installed)")
except ImportError:
    PDF_SUPPORT_AVAILABLE = False
    logger.info("pdf2image not installed. PDF support disabled.")


def is_pdf(file_path: str | Path) -> bool:
    """
    Check if file is a PDF.

    Args:
        file_path: Path to file

    Returns:
        True if file has .pdf extension
    """
    return Path(file_path).suffix.lower() == ".pdf"


def validate_pdf_file(file_path: str | Path) -> Tuple[bool, Optional[str]]:
    """
    Validate if file is a valid PDF.

    Args:
        file_path: Path to PDF file

    Returns:
        Tuple of (is_valid, error_message)
    """
    file_path = Path(file_path)

    # Check file exists
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    # Check file extension
    if not is_pdf(file_path):
        return False, "File is not a PDF (must have .pdf extension)"

    # Check file size
    from config.settings import MAX_PDF_SIZE_MB
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_PDF_SIZE_MB:
        return False, f"PDF too large: {file_size_mb:.1f}MB. Maximum: {MAX_PDF_SIZE_MB}MB"

    return True, None


def pdf_to_images(
    pdf_source: str | Path | bytes,
    dpi: int = None,
    first_page: Optional[int] = None,
    last_page: Optional[int] = None,
) -> Tuple[Optional[List[Image.Image]], Optional[str]]:
    """
    Convert PDF pages to PIL Images.

    Phase 2: PDF to image conversion

    Args:
        pdf_source: Path to PDF file or PDF bytes
        dpi: DPI for conversion (higher = better quality but slower)
             If None, uses PDF_SETTINGS['dpi']
        first_page: First page to convert (1-indexed, None = start from 1)
        last_page: Last page to convert (1-indexed, None = all pages)

    Returns:
        Tuple of (list of PIL Images, error_message)
        If successful: (images_list, None)
        If failed: (None, error_description)

    Raises:
        RuntimeError: If pdf2image is not installed
    """
    if not PDF_SUPPORT_AVAILABLE:
        return None, (
            "PDF support not available. Install with: "
            "pip install pdf2image"
        )

    try:
        # Use default DPI from settings if not provided
        if dpi is None:
            dpi = PDF_SETTINGS.get("dpi", 200)

        # Convert PDF to images
        if isinstance(pdf_source, bytes):
            # Convert from bytes
            images = convert_from_bytes(
                pdf_source,
                dpi=dpi,
                first_page=first_page,
                last_page=last_page,
            )
        else:
            # Convert from file path
            pdf_path = Path(pdf_source)
            is_valid, error = validate_pdf_file(pdf_path)
            if not is_valid:
                return None, error

            images = convert_from_path(
                str(pdf_path),
                dpi=dpi,
                first_page=first_page,
                last_page=last_page,
            )

        logger.info(f"Successfully converted {len(images)} pages from PDF")
        return images, None

    except Exception as e:
        error_msg = str(e)
        if "poppler" in error_msg.lower() or "pdfimages" in error_msg.lower():
            detailed_error = (
                "Poppler is not installed or not in PATH. "
                "Poppler is a required system dependency for PDF processing.\n\n"
                "Install Poppler:\n"
                "- Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/\n"
                "  Extract and add bin folder to PATH environment variable\n"
                "- Linux: sudo apt-get install poppler-utils\n"
                "- macOS: brew install poppler\n\n"
                f"Original error: {error_msg}"
            )
        else:
            detailed_error = f"PDF conversion failed: {error_msg}"
        
        logger.error(detailed_error)
        return None, detailed_error


def get_pdf_page_count(pdf_source: str | Path | bytes) -> Tuple[Optional[int], Optional[str]]:
    """
    Get number of pages in PDF.

    Phase 2: PDF page counting

    Args:
        pdf_source: Path to PDF file or PDF bytes

    Returns:
        Tuple of (page_count, error_message)
        If successful: (count, None)
        If failed: (None, error_description)
    """
    if not PDF_SUPPORT_AVAILABLE:
        return None, "pdf2image not installed"

    try:
        # For bytes: try to get count with minimal PDF parsing
        if isinstance(pdf_source, bytes):
            # Try using PyPDF2 if available for bytes
            try:
                import PyPDF2
                pdf_file = BytesIO(pdf_source)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                page_count = len(pdf_reader.pages)
                logger.info(f"PDF has {page_count} pages")
                return page_count, None
            except ImportError:
                # PyPDF2 not installed, try pdf2image for count
                try:
                    images = convert_from_bytes(pdf_source, dpi=100)
                    page_count = len(images)
                    logger.info(f"PDF has {page_count} pages")
                    return page_count, None
                except Exception as e:
                    raise e
        else:
            # For file paths: use PyPDF2 if available
            try:
                import PyPDF2
                with open(pdf_source, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    page_count = len(pdf_reader.pages)
                    logger.info(f"PDF has {page_count} pages")
                    return page_count, None
            except ImportError:
                # Fallback: use pdf2image to count pages
                pdf_path = Path(pdf_source)
                is_valid, error = validate_pdf_file(pdf_path)
                if not is_valid:
                    return None, error

                images = convert_from_path(str(pdf_path), dpi=100)
                page_count = len(images)
                logger.info(f"PDF has {page_count} pages")
                return page_count, None

    except Exception as e:
        error_msg = str(e)
        if "poppler" in error_msg.lower() or "pdfimages" in error_msg.lower():
            detailed_error = (
                "❌ Poppler is not installed or not in PATH.\n\n"
                "Poppler is a required system dependency for PDF processing.\n\n"
                "🔧 To install Poppler:\n"
                "1. Download: https://github.com/oschwartz10612/poppler-windows/releases/\n"
                "2. Extract the zip file\n"
                "3. Set POPPLER_PATH environment variable to the 'bin' folder path\n"
                "   OR add the bin folder to your system PATH\n\n"
                "Example: POPPLER_PATH=C:\\poppler\\bin"
            )
        else:
            detailed_error = f"Failed to get PDF page count: {error_msg}"
        
        logger.error(detailed_error)
        return None, detailed_error


__all__ = [
    "is_pdf",
    "validate_pdf_file",
    "pdf_to_images",
    "get_pdf_page_count",
    "PDF_SUPPORT_AVAILABLE",
]
