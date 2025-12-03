"""
File and I/O utilities for OCR application.

This module handles:
- File validation and format checking
- Saving extracted text to various formats
- Batch processing file handling (Phase 2)
- ZIP archive creation (Phase 2)
- Temporary file management
- Download preparation
"""

import logging
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, BinaryIO, List, Tuple, Dict
from datetime import datetime

from PIL import Image

from config.settings import (
    SUPPORTED_IMAGE_FORMATS,
    MAX_IMAGE_SIZE_MB,
    MAX_BATCH_IMAGES,
    TEMP_DIR,
)

logger = logging.getLogger(__name__)


def validate_image_file(file_path: str | Path) -> tuple[bool, Optional[str]]:
    """
    Validate if file is a supported image format.

    Args:
        file_path: Path to image file

    Returns:
        Tuple of (is_valid, error_message)
    """
    file_path = Path(file_path)

    # Check file exists
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    # Check file extension
    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_IMAGE_FORMATS:
        supported = ", ".join(SUPPORTED_IMAGE_FORMATS)
        return False, f"Unsupported format: {suffix}. Supported: {supported}"

    # Check file size
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_IMAGE_SIZE_MB:
        return False, f"File too large: {file_size_mb:.1f}MB. Maximum: {MAX_IMAGE_SIZE_MB}MB"

    return True, None


def load_image(file_source: str | Path | BinaryIO) -> tuple[Optional[Image.Image], Optional[str]]:
    """
    Load image from various sources.

    Args:
        file_source: File path, Path object, or file-like object (BytesIO)

    Returns:
        Tuple of (PIL Image, error_message)
        If successful: (Image, None)
        If failed: (None, error_description)
    """
    try:
        if isinstance(file_source, (str, Path)):
            # File path
            file_path = Path(file_source)
            is_valid, error = validate_image_file(file_path)
            if not is_valid:
                return None, error

            image = Image.open(file_path)

        else:
            # File-like object (e.g., BytesIO from Streamlit upload)
            image = Image.open(file_source)

        # Convert to RGB if necessary (remove alpha channel, etc.)
        if image.mode in ("RGBA", "LA", "P"):
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
            image = rgb_image
        elif image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        logger.info(f"Image loaded successfully: {image.size}, mode: {image.mode}")
        return image, None

    except Exception as e:
        error_msg = f"Failed to load image: {str(e)}"
        logger.error(error_msg)
        return None, error_msg


def save_text_to_file(
    text: str,
    output_path: Optional[str | Path] = None,
    filename: Optional[str] = None,
) -> tuple[Optional[Path], Optional[str]]:
    """
    Save extracted text to a .txt file.

    Args:
        text: Text to save
        output_path: Directory to save file in. If None, uses TEMP_DIR.
        filename: Filename to use. If None, generates timestamp-based name.

    Returns:
        Tuple of (Path to saved file, error_message)
        If successful: (Path, None)
        If failed: (None, error_description)
    """
    try:
        # Determine output path
        if output_path is None:
            output_path = TEMP_DIR
        else:
            output_path = Path(output_path)

        # Create directory if needed
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"extracted_text_{timestamp}.txt"

        # Full file path
        file_path = output_path / filename

        # Write file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        logger.info(f"Text saved to {file_path}")
        return file_path, None

    except Exception as e:
        error_msg = f"Failed to save text file: {str(e)}"
        logger.error(error_msg)
        return None, error_msg


def save_preprocessed_image(
    image: Image.Image,
    output_path: Optional[str | Path] = None,
    filename: Optional[str] = None,
) -> tuple[Optional[Path], Optional[str]]:
    """
    Save preprocessed image for debugging/inspection.

    Args:
        image: PIL Image to save
        output_path: Directory to save in. If None, uses TEMP_DIR.
        filename: Filename to use. If None, generates timestamp-based name.

    Returns:
        Tuple of (Path to saved file, error_message)
    """
    try:
        if output_path is None:
            output_path = TEMP_DIR
        else:
            output_path = Path(output_path)

        output_path.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"preprocessed_{timestamp}.png"

        file_path = output_path / filename
        image.save(file_path)

        logger.info(f"Preprocessed image saved to {file_path}")
        return file_path, None

    except Exception as e:
        error_msg = f"Failed to save preprocessed image: {str(e)}"
        logger.error(error_msg)
        return None, error_msg


def get_temp_file(suffix: str = ".txt") -> str:
    """
    Get path to a temporary file.

    Args:
        suffix: File suffix/extension (e.g., '.txt', '.png')

    Returns:
        Path to temporary file (file not yet created)
    """
    temp_file = tempfile.NamedTemporaryFile(
        suffix=suffix,
        dir=TEMP_DIR,
        delete=False
    )
    return temp_file.name


def cleanup_temp_files(max_age_hours: int = 24) -> int:
    """
    Remove old temporary files.

    Args:
        max_age_hours: Remove files older than this many hours

    Returns:
        Number of files removed
    """
    try:
        from time import time
        cutoff_time = time() - (max_age_hours * 3600)
        removed_count = 0

        for temp_file in TEMP_DIR.glob("*"):
            if temp_file.is_file():
                if temp_file.stat().st_mtime < cutoff_time:
                    temp_file.unlink()
                    removed_count += 1

        logger.info(f"Cleaned up {removed_count} temporary files")
        return removed_count

    except Exception as e:
        logger.error(f"Error cleaning temporary files: {e}")
        return 0


def get_file_size_mb(file_path: str | Path) -> float:
    """
    Get file size in megabytes.

    Args:
        file_path: Path to file

    Returns:
        File size in MB
    """
    return Path(file_path).stat().st_size / (1024 * 1024)


# ============================================================================
# PHASE 2: BATCH & ZIP SUPPORT
# ============================================================================

def aggregate_batch_results(
    batch_results: List[Dict],
    include_separator: bool = True,
    separator: str = "\n" + "=" * 80 + "\n"
) -> str:
    """
    Aggregate multiple OCR results into single text.

    Phase 2: Batch processing

    Args:
        batch_results: List of dicts with 'filename' and 'text' keys
        include_separator: Add separator between results
        separator: Separator string to use

    Returns:
        Aggregated text with all results
    """
    aggregated = []

    for i, result in enumerate(batch_results):
        filename = result.get('filename', f'File {i+1}')

        if include_separator and i > 0:
            aggregated.append(separator)

        # Add file header
        aggregated.append(f"\n📄 FILE: {filename}\n")
        aggregated.append("-" * 40 + "\n")

        # Add OCR text
        aggregated.append(result.get('text', '[No text extracted]'))
        aggregated.append("\n")

    return "".join(aggregated)


def create_batch_zip(
    batch_results: List[Dict],
    output_path: Optional[str | Path] = None,
    zip_filename: Optional[str] = None,
) -> Tuple[Optional[Path], Optional[str]]:
    """
    Create ZIP archive of batch results.

    Phase 2: Batch processing - ZIP export

    Args:
        batch_results: List of dicts with 'filename' and 'text' keys
        output_path: Directory for ZIP file. If None, uses TEMP_DIR.
        zip_filename: Name for ZIP file. If None, generates timestamp-based name.

    Returns:
        Tuple of (Path to ZIP file, error_message)
        If successful: (Path, None)
        If failed: (None, error_description)
    """
    try:
        if output_path is None:
            output_path = TEMP_DIR
        else:
            output_path = Path(output_path)

        output_path.mkdir(parents=True, exist_ok=True)

        # Generate ZIP filename
        if zip_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"batch_results_{timestamp}.zip"

        zip_path = output_path / zip_filename

        # Create ZIP archive
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for result in batch_results:
                filename = result.get('filename', 'unknown.txt')
                text = result.get('text', '')

                # Create .txt filename from original
                txt_filename = Path(filename).stem + ".txt"

                # Add to ZIP
                zf.writestr(txt_filename, text)

        logger.info(f"Batch ZIP created: {zip_path}")
        return zip_path, None

    except Exception as e:
        error_msg = f"Failed to create batch ZIP: {str(e)}"
        logger.error(error_msg)
        return None, error_msg


def validate_batch_files(uploaded_files: List) -> Tuple[List, List]:
    """
    Validate batch of uploaded files.

    Phase 2: Batch processing validation

    Args:
        uploaded_files: List of Streamlit uploaded file objects

    Returns:
        Tuple of (valid_files, errors)
        valid_files: List of valid file objects
        errors: List of (filename, error_message) tuples for invalid files
    """
    valid_files = []
    errors = []

    # Check batch size limit
    if len(uploaded_files) > MAX_BATCH_IMAGES:
        return [], [(f"Batch size", f"Maximum {MAX_BATCH_IMAGES} images allowed")]

    for uploaded_file in uploaded_files:
        # Check extension
        suffix = Path(uploaded_file.name).suffix.lower()
        if suffix not in SUPPORTED_IMAGE_FORMATS:
            errors.append((uploaded_file.name, f"Unsupported format: {suffix}"))
            continue

        # Check file size
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        if file_size_mb > MAX_IMAGE_SIZE_MB:
            errors.append((
                uploaded_file.name,
                f"File too large: {file_size_mb:.1f}MB. Max: {MAX_IMAGE_SIZE_MB}MB"
            ))
            continue

        valid_files.append(uploaded_file)

    return valid_files, errors


def load_batch_images(
    uploaded_files: List,
) -> Tuple[List[Tuple[str, Image.Image]], List[Tuple[str, str]]]:
    """
    Load multiple images from uploaded files.

    Phase 2: Batch processing

    Args:
        uploaded_files: List of Streamlit uploaded file objects

    Returns:
        Tuple of (successful_images, load_errors)
        successful_images: List of (filename, PIL Image) tuples
        load_errors: List of (filename, error_message) tuples
    """
    successful_images = []
    load_errors = []

    for uploaded_file in uploaded_files:
        image, error = load_image(uploaded_file)

        if error:
            load_errors.append((uploaded_file.name, error))
        else:
            successful_images.append((uploaded_file.name, image))

    return successful_images, load_errors
