"""
Image preprocessing pipeline for OCR.

This module provides image preprocessing utilities including:
- Grayscale conversion
- Binary thresholding
- Noise removal (denoising)
- Perspective correction (deskew)

All functions accept PIL Images and return PIL Images for easy integration
with the rest of the pipeline.
"""

from typing import Tuple, Optional
import cv2
import numpy as np
from PIL import Image

from config.settings import IMAGE_PROCESSING


def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    """
    Convert PIL Image to OpenCV (cv2) format.

    Args:
        pil_image: PIL Image object

    Returns:
        numpy array in BGR format (OpenCV default)
    """
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)


def cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
    """
    Convert OpenCV image (BGR) to PIL Image (RGB).

    Args:
        cv2_image: numpy array in BGR format

    Returns:
        PIL Image object
    """
    rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_image)


def to_grayscale(image: Image.Image) -> Image.Image:
    """
    Convert image to grayscale.

    Args:
        image: PIL Image object

    Returns:
        Grayscale PIL Image
    """
    if image.mode == "L":
        return image
    return image.convert("L")


def apply_threshold(image: Image.Image, threshold_value: int = 127) -> Image.Image:
    """
    Apply binary thresholding to image.

    Uses Otsu's method if threshold_value is None for automatic threshold detection.

    Args:
        image: PIL Image (should be grayscale)
        threshold_value: Threshold value (0-255). If None, uses Otsu's method.

    Returns:
        Binary thresholded PIL Image
    """
    # Convert to grayscale if needed
    gray = to_grayscale(image)
    cv2_image = pil_to_cv2(gray)

    if threshold_value is None:
        # Otsu's method
        _, binary = cv2.threshold(cv2_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        # Standard binary threshold
        _, binary = cv2.threshold(cv2_image, threshold_value, 255, cv2.THRESH_BINARY)

    return Image.fromarray(binary)


def denoise(image: Image.Image, strength: int = 10) -> Image.Image:
    """
    Remove noise from image using fast Non-Local Means denoising.

    Args:
        image: PIL Image
        strength: Denoising strength (1-30). Higher = more aggressive.

    Returns:
        Denoised PIL Image
    """
    # Clamp strength value
    strength = max(1, min(30, strength))

    if image.mode == "L":
        # Grayscale denoising
        cv2_image = cv2.cvtColor(np.array(image), cv2.COLOR_GRAY2BGR)
        denoised = cv2.fastNlMeansDenoising(cv2_image, h=strength)
        return Image.fromarray(cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY))
    else:
        # Color denoising
        cv2_image = pil_to_cv2(image)
        denoised = cv2.fastNlMeansDenoisingColored(cv2_image, h=strength)
        return cv2_to_pil(denoised)


def estimate_skew_angle(image: Image.Image) -> float:
    """
    Estimate the skew angle of text in an image.

    Uses Hough transform to detect lines and calculate rotation angle.

    Args:
        image: PIL Image (grayscale works best)

    Returns:
        Estimated skew angle in degrees (positive = counterclockwise)
    """
    # Convert to grayscale
    gray = to_grayscale(image)
    cv2_image = cv2.cvtColor(np.array(gray), cv2.COLOR_GRAY2BGR)

    # Edge detection
    edges = cv2.Canny(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY), 50, 150)

    # Hough line transform
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)

    if lines is None or len(lines) == 0:
        return 0.0

    # Extract angles and find median
    angles = []
    for line in lines:
        rho, theta = line[0]
        angle = np.degrees(theta) - 90
        angles.append(angle)

    # Return median angle
    median_angle = float(np.median(angles))

    # Normalize to [-45, 45] range
    if median_angle > 45:
        median_angle -= 90
    elif median_angle < -45:
        median_angle += 90

    return median_angle


def deskew(image: Image.Image, max_angle: float = 10.0) -> Image.Image:
    """
    Correct image skew/rotation.

    Args:
        image: PIL Image
        max_angle: Maximum angle to correct for (degrees). Helps avoid overcorrection.

    Returns:
        Deskewed PIL Image
    """
    angle = estimate_skew_angle(image)

    # Only correct if angle is within threshold
    if abs(angle) > max_angle:
        return image

    # Convert to cv2 for rotation
    cv2_image = pil_to_cv2(image)
    h, w = cv2_image.shape[:2]

    # Get rotation matrix
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Apply rotation
    rotated = cv2.warpAffine(
        cv2_image, rotation_matrix, (w, h),
        borderMode=cv2.BORDER_REFLECT,
        flags=cv2.INTER_LINEAR
    )

    return cv2_to_pil(rotated)


def preprocess_image(image: Image.Image, config: Optional[dict] = None) -> Image.Image:
    """
    Apply full preprocessing pipeline to image.

    Pipeline includes:
    1. Grayscale conversion (if enabled)
    2. Denoising (if enabled)
    3. Deskewing (if enabled)
    4. Thresholding (if enabled)

    Args:
        image: PIL Image to preprocess
        config: Dictionary with preprocessing options. If None, uses IMAGE_PROCESSING from settings.

    Returns:
        Preprocessed PIL Image ready for OCR
    """
    if config is None:
        config = IMAGE_PROCESSING

    processed = image

    # Step 1: Grayscale
    if config.get("grayscale", True):
        processed = to_grayscale(processed)

    # Step 2: Denoise
    if config.get("denoise_enabled", True):
        strength = config.get("denoise_strength", 10)
        processed = denoise(processed, strength=strength)

    # Step 3: Deskew
    if config.get("deskew_enabled", False):
        max_angle = config.get("max_angle", 10)
        processed = deskew(processed, max_angle=max_angle)

    # Step 4: Threshold
    if config.get("threshold_enabled", True):
        threshold_value = config.get("threshold_value", 127)
        processed = apply_threshold(processed, threshold_value=threshold_value)

    return processed


def get_preprocessing_stats(original: Image.Image, processed: Image.Image) -> dict:
    """
    Generate statistics about preprocessing changes.

    Args:
        original: Original PIL Image
        processed: Processed PIL Image

    Returns:
        Dictionary with stats (mode, size, etc.)
    """
    return {
        "original_mode": original.mode,
        "original_size": original.size,
        "processed_mode": processed.mode,
        "processed_size": processed.size,
    }
