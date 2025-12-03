"""
OCR Engine using Tesseract.

This module provides a clean interface to Tesseract OCR via pytesseract.
It handles:
- Text extraction from images
- Multi-language support (Phase 2)
- Error handling and validation
- Confidence scores
- Bounding box extraction (Phase 2)
"""

from typing import Dict, Optional, List, Tuple
import logging
from pathlib import Path

import pytesseract
from PIL import Image
import numpy as np
import cv2

from config.settings import (
    TESSERACT_PATH,
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    OCR_SETTINGS,
)

logger = logging.getLogger(__name__)


def set_tesseract_path(path: str) -> None:
    """
    Set the Tesseract executable path.

    Call this at startup if Tesseract is not on system PATH.

    Args:
        path: Full path to tesseract executable (e.g., 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe')
    """
    pytesseract.pytesseract.pytesseract_cmd = path
    logger.info(f"Tesseract path set to: {path}")


def initialize_tesseract() -> bool:
    """
    Initialize Tesseract OCR.

    Attempts to verify Tesseract is available and accessible.

    Returns:
        True if Tesseract is ready, False otherwise
    """
    try:
        # Set path if custom path is configured
        if TESSERACT_PATH != "tesseract":
            pytesseract.pytesseract.pytesseract_cmd = TESSERACT_PATH

        # Test Tesseract availability
        version = pytesseract.get_tesseract_version()
        logger.info(f"Tesseract initialized successfully. Version: {version}")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize Tesseract: {e}")
        return False


def extract_text(
    image: Image.Image,
    language: str = DEFAULT_LANGUAGE,
    config: Optional[Dict] = None,
) -> str:
    """
    Extract text from image using Tesseract OCR.

    Args:
        image: PIL Image object (preferably preprocessed)
        language: Language code (e.g., 'eng', 'fra', 'deu'). Supports '+' for multiple.
        config: Optional Tesseract config string or dict from settings.OCR_SETTINGS

    Returns:
        Extracted text string

    Raises:
        RuntimeError: If OCR fails or Tesseract is not available
    """
    if not isinstance(image, Image.Image):
        raise TypeError("image must be a PIL Image object")

    try:
        if config is None:
            config = OCR_SETTINGS

        # Build pytesseract config
        if isinstance(config, dict):
            lang = config.get("lang", language)
            psm_config = config.get("config", "--psm 3")
        else:
            lang = language
            psm_config = config

        # Run OCR
        text = pytesseract.image_to_string(image, lang=lang, config=psm_config)

        logger.info(f"OCR completed. Extracted {len(text)} characters.")
        return text

    except pytesseract.TesseractNotFoundError as e:
        logger.error("Tesseract not found. Ensure it's installed and on PATH.")
        raise RuntimeError(
            "Tesseract OCR is not installed or not found. "
            "Please install Tesseract-OCR from https://github.com/UB-Mannheim/tesseract/wiki"
        ) from e

    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise RuntimeError(f"OCR extraction failed: {str(e)}") from e


def extract_text_with_confidence(
    image: Image.Image,
    language: str = DEFAULT_LANGUAGE,
) -> Dict[str, str | float]:
    """
    Extract text with confidence score using Tesseract.

    Args:
        image: PIL Image object
        language: Language code

    Returns:
        Dictionary with 'text' and 'confidence' keys
    """
    try:
        data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)

        # Extract text
        text = " ".join([word for word in data.get("text", []) if word.strip()])

        # Calculate average confidence (Tesseract returns -1 for some entries)
        confidences = [int(conf) for conf in data.get("conf", []) if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return {
            "text": text,
            "confidence": avg_confidence,
        }

    except Exception as e:
        logger.error(f"Failed to extract text with confidence: {e}")
        raise RuntimeError(f"OCR with confidence failed: {str(e)}") from e


def validate_image_for_ocr(image: Image.Image) -> tuple[bool, Optional[str]]:
    """
    Validate if image is suitable for OCR.

    Checks:
    - Image is not None or empty
    - Image dimensions are reasonable (>= 20x20 pixels)
    - Image has some content (not pure white/black)

    Args:
        image: PIL Image to validate

    Returns:
        Tuple of (is_valid, error_message)
        If valid, returns (True, None)
        If invalid, returns (False, error_description)
    """
    if image is None:
        return False, "Image is None"

    try:
        # Check dimensions
        width, height = image.size
        if width < 20 or height < 20:
            return False, f"Image too small ({width}x{height}). Minimum is 20x20 pixels."

        # Check for empty/blank image
        # Convert to grayscale for analysis
        gray = image.convert("L")
        pixels = list(gray.getdata())

        if not pixels:
            return False, "Image has no pixel data"

        # Check if image is mostly uniform (all white or all black)
        min_pixel = min(pixels)
        max_pixel = max(pixels)
        pixel_range = max_pixel - min_pixel

        if pixel_range < 10:  # Very little variation
            return False, "Image appears to be blank or nearly uniform (insufficient contrast)"

        return True, None

    except Exception as e:
        return False, f"Error validating image: {str(e)}"


def get_available_languages() -> List[str]:
    """
    Get list of available languages in Tesseract installation.

    Returns:
        List of language codes (e.g., ['eng', 'fra', 'deu'])

    Note:
        This attempts to list available tessdata files. Requires proper
        Tesseract installation with language data files.
    """
    try:
        from tesserwrap import get_languages
        return get_languages()
    except Exception:
        # Fallback if tesserwrap not available
        logger.warning("Could not retrieve available languages from Tesseract")
        return ["eng"]  # Default fallback


def get_supported_language_codes() -> Dict[str, str]:
    """
    Get dictionary of supported language display names to codes.

    Phase 2: Multi-language support

    Returns:
        Dictionary mapping display names to language codes
        Example: {"English": "eng", "Hindi": "hin", ...}
    """
    return SUPPORTED_LANGUAGES


def extract_text_with_bounding_boxes(
    image: Image.Image,
    language: str = DEFAULT_LANGUAGE,
) -> Dict:
    """
    Extract text with bounding box information.

    Phase 2: Visual text region highlighting

    Args:
        image: PIL Image object
        language: Language code (e.g., 'eng', 'hin')

    Returns:
        Dictionary with:
        - 'text': Full extracted text
        - 'boxes': List of bounding boxes [(x, y, w, h, text, confidence), ...]
        - 'raw_data': Full pytesseract data output

    Raises:
        RuntimeError: If OCR fails
    """
    try:
        data = pytesseract.image_to_data(
            image,
            lang=language,
            output_type=pytesseract.Output.DICT
        )

        # Extract bounding boxes
        boxes = []
        n_boxes = len(data['level'])

        for i in range(n_boxes):
            if data['text'][i].strip():  # Only non-empty text
                box_data = {
                    'x': int(data['left'][i]),
                    'y': int(data['top'][i]),
                    'width': int(data['width'][i]),
                    'height': int(data['height'][i]),
                    'text': data['text'][i],
                    'confidence': int(data['conf'][i]),
                    'level': int(data['level'][i]),  # Word vs block vs line
                }
                boxes.append(box_data)

        # Reconstruct full text
        full_text = " ".join([word for word in data.get("text", []) if word.strip()])

        return {
            'text': full_text,
            'boxes': boxes,
            'raw_data': data,
        }

    except Exception as e:
        logger.error(f"Failed to extract text with boxes: {e}")
        raise RuntimeError(f"OCR with bounding boxes failed: {str(e)}") from e


def get_annotated_image_with_boxes(
    image: Image.Image,
    language: str = DEFAULT_LANGUAGE,
    box_color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
    text_color: Tuple[int, int, int] = (0, 0, 255),
    font_scale: float = 0.5,
) -> Image.Image:
    """
    Draw bounding boxes on image highlighting detected text regions.

    Phase 2: Visual text region highlighting

    Args:
        image: PIL Image object
        language: Language code
        box_color: RGB color for boxes (default: green)
        thickness: Line thickness for boxes
        text_color: RGB color for confidence text
        font_scale: Font size for confidence labels

    Returns:
        PIL Image with bounding boxes drawn

    Raises:
        RuntimeError: If OCR or annotation fails
    """
    try:
        # Convert PIL to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Get bounding box data
        ocr_data = extract_text_with_bounding_boxes(image, language)
        boxes = ocr_data['boxes']

        # Draw boxes on image
        for box in boxes:
            # Only draw high-confidence boxes (>50%) to avoid clutter
            if box['confidence'] > 50:
                x, y = box['x'], box['y']
                w, h = box['width'], box['height']

                # Draw rectangle
                cv2.rectangle(
                    cv_image,
                    (x, y),
                    (x + w, y + h),
                    box_color,
                    thickness
                )

                # Draw confidence label (if space available)
                if box['level'] == 5:  # Word level
                    conf_text = f"{box['confidence']}%"
                    cv2.putText(
                        cv_image,
                        conf_text,
                        (x, max(y - 5, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale,
                        text_color,
                        1
                    )

        # Convert back to PIL
        result_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(result_image)

    except Exception as e:
        logger.error(f"Failed to annotate image with boxes: {e}")
        raise RuntimeError(f"Image annotation failed: {str(e)}") from e
