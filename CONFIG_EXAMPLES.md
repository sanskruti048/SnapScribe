# SnapScribe Configuration Override Examples

This file shows how to customize SnapScribe settings for different use cases.

## Example 1: Optimized for Scanned Documents

If you're working with clean scanned PDFs/images:

```python
# In config/settings.py, modify IMAGE_PROCESSING:

IMAGE_PROCESSING = {
    "grayscale": True,
    "threshold_enabled": True,
    "threshold_value": 130,      # Slightly higher for scans
    "denoise_enabled": False,     # Scans are usually clean
    "denoise_strength": 5,
    "deskew_enabled": False,      # Scans are usually straight
    "max_angle": 5,
}
```

## Example 2: Optimized for Smartphone Photos

For photos taken with phone cameras (often noisy, tilted):

```python
IMAGE_PROCESSING = {
    "grayscale": True,
    "threshold_enabled": True,
    "threshold_value": 120,
    "denoise_enabled": True,      # Heavy denoising for phone photos
    "denoise_strength": 20,       # Aggressive noise removal
    "deskew_enabled": True,       # Often tilted
    "max_angle": 15,
}
```

## Example 3: Optimized for Low-Contrast Documents

For faded or low-contrast text:

```python
IMAGE_PROCESSING = {
    "grayscale": True,
    "threshold_enabled": True,
    "threshold_value": 100,       # Lower threshold = more white
    "denoise_enabled": True,
    "denoise_strength": 15,
    "deskew_enabled": False,
    "max_angle": 10,
}
```

## Example 4: Strict Quality - Minimal Processing

For already-optimal images:

```python
IMAGE_PROCESSING = {
    "grayscale": True,
    "threshold_enabled": False,   # Keep original colors
    "denoise_enabled": False,     # No processing
    "deskew_enabled": False,
    "max_angle": 0,
}
```

## OCR Language Configuration (Phase 2)

Once multi-language support is added:

```python
# For French text
OCR_SETTINGS = {
    "lang": "fra",
    "config": "--psm 3",
}

# For mixed English + German
OCR_SETTINGS = {
    "lang": "eng+deu",
    "config": "--psm 3",
}

# For sparse/scattered text
OCR_SETTINGS = {
    "lang": "eng",
    "config": "--psm 11",  # PSM 11 = Sparse text
}
```

## Text Cleanup Profiles

```python
# Aggressive cleanup (for formal documents)
POSTPROCESSING = {
    "remove_extra_whitespace": True,
    "fix_line_breaks": True,
    "remove_empty_lines": True,    # Remove blank lines
    "spellcheck_enabled": True,    # Phase 2: fix typos
}

# Minimal cleanup (preserve formatting)
POSTPROCESSING = {
    "remove_extra_whitespace": False,
    "fix_line_breaks": False,
    "remove_empty_lines": False,
    "spellcheck_enabled": False,
}
```

## Using Environment Variables (Advanced)

For deployment/Docker environments:

```python
# In config/settings.py
import os

TESSERACT_PATH = os.getenv(
    "TESSERACT_PATH",
    "tesseract"  # Fallback
)

# In .env or container environment:
# TESSERACT_PATH=/usr/bin/tesseract
```

## Programmatic Configuration Override (Advanced)

```python
# In app.py or custom script
from core import preprocessing, ocr_engine
from config import settings

# Override settings at runtime
custom_config = {
    "grayscale": True,
    "threshold_enabled": True,
    "threshold_value": 125,
    "denoise_enabled": True,
    "denoise_strength": 15,
    "deskew_enabled": True,
}

# Use custom config
processed_image = preprocessing.preprocess_image(image, config=custom_config)

# Extract text with custom config
ocr_settings = {
    "lang": "eng",
    "config": "--psm 6"
}
text = ocr_engine.extract_text(processed_image, config=ocr_settings)
```

## Troubleshooting via Configuration

| Problem | Try |
|---------|-----|
| Over-processed, losing text | Disable denoise, lower threshold_value |
| Under-processed, keeping artifacts | Enable denoise, raise threshold_value |
| Rotated text not corrected | Enable deskew, increase max_angle |
| Slow processing | Disable deskew, reduce denoise_strength |
| Wrong language detected | Set lang explicitly in OCR_SETTINGS |

---

For more details, see the comments in `config/settings.py` and the module docstrings in the `core/` directory.
