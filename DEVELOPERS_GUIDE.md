"""
SnapScribe OCR - Developer's Guide

This guide explains the code architecture, data flow, and design patterns
used in SnapScribe OCR. Useful for understanding, maintaining, and extending
the codebase.
"""

# =============================================================================
# DATA FLOW & ARCHITECTURE
# =============================================================================

"""
The SnapScribe OCR pipeline follows a clean, linear data flow:

┌─────────────────────────────────────────────────────────────────┐
│                   USER INTERACTION (Streamlit)                   │
│                        (app.py)                                  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   FILE UPLOAD         │  (file_utils.load_image)
         │   Image loaded as PIL │
         └───────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────────┐
    │  IMAGE PREPROCESSING           │  (preprocessing.preprocess_image)
    │  • Grayscale conversion        │
    │  • Denoising                   │
    │  • Thresholding                │
    │  • Deskew                      │
    │  (PIL Image → PIL Image)       │
    └────────────┬───────────────────┘
                 │
                 ▼
    ┌────────────────────────────────┐
    │  OCR EXTRACTION                │  (ocr_engine.extract_text)
    │  • Validate image              │
    │  • Call Tesseract              │
    │  • Return raw text             │
    │  (PIL Image → String)          │
    └────────────┬───────────────────┘
                 │
                 ▼
    ┌────────────────────────────────┐
    │  TEXT POSTPROCESSING           │  (postprocessing.clean_text)
    │  • Remove extra spaces         │
    │  • Fix line breaks             │
    │  • Normalize quotes            │
    │  (String → String)             │
    └────────────┬───────────────────┘
                 │
                 ▼
    ┌────────────────────────────────┐
    │  RESULT DISPLAY & DOWNLOAD     │  (file_utils.save_text_to_file)
    │  • Show text in UI             │
    │  • Display statistics          │
    │  • Enable download             │
    └────────────────────────────────┘

"""

# =============================================================================
# MODULE RESPONSIBILITIES
# =============================================================================

"""
Each module has a single, clear responsibility:

config/settings.py
──────────────────
Responsibility: Centralized configuration management
Does:
  • Define all constants (paths, settings)
  • Load environment variables
  • Provide default settings
  • Separate concerns (image, OCR, UI, postprocessing)
Does NOT:
  • Perform any image processing
  • Interface with Tesseract
  • Generate UI
  • Write to files

Dependency Graph: No dependencies (except pathlib)

Usage Pattern:
  from config.settings import IMAGE_PROCESSING, TESSERACT_PATH
  config = IMAGE_PROCESSING
  # Use config throughout app

---

core/preprocessing.py
─────────────────────
Responsibility: Image preprocessing/enhancement
Does:
  • Transform PIL Images via OpenCV
  • Provide preprocessing functions
  • Handle image format conversions
  • Validate preprocessing results
Does NOT:
  • Call Tesseract
  • Clean text
  • Interact with files
  • Display UI

Dependency Graph:
  • PIL (Image library)
  • OpenCV (cv2)
  • NumPy
  • config.settings (read-only)

Usage Pattern:
  from core import preprocessing
  from PIL import Image
  image = Image.open("test.jpg")
  processed = preprocessing.preprocess_image(image)
  # Returns PIL Image

---

core/ocr_engine.py
──────────────────
Responsibility: Tesseract OCR interface
Does:
  • Initialize Tesseract
  • Extract text from images
  • Validate images
  • Handle OCR errors gracefully
Does NOT:
  • Preprocess images (use preprocessing.py)
  • Modify extracted text (use postprocessing.py)
  • Save files (use file_utils.py)
  • Display UI

Dependency Graph:
  • pytesseract
  • PIL
  • config.settings (read-only)

Usage Pattern:
  from core import ocr_engine
  ocr_engine.initialize_tesseract()
  text = ocr_engine.extract_text(pil_image)
  # Returns string

---

core/postprocessing.py
──────────────────────
Responsibility: Text cleanup and formatting
Does:
  • Normalize whitespace
  • Fix line breaks
  • Correct quotes
  • Generate text statistics
Does NOT:
  • Modify images
  • Call OCR
  • Save files
  • Display UI

Dependency Graph:
  • re (regular expressions)
  • config.settings (read-only)

Usage Pattern:
  from core import postprocessing
  cleaned = postprocessing.clean_text(raw_ocr_text)
  stats = postprocessing.get_text_stats(text)
  # Returns string and dict

---

utils/file_utils.py
───────────────────
Responsibility: File I/O and validation
Does:
  • Load images from files or BytesIO
  • Validate file formats and sizes
  • Save text to files
  • Manage temporary files
Does NOT:
  • Preprocess images (use preprocessing.py)
  • Call OCR
  • Clean text
  • Display UI

Dependency Graph:
  • PIL
  • pathlib
  • tempfile
  • config.settings (read-only)

Usage Pattern:
  from utils import file_utils
  image, error = file_utils.load_image(uploaded_file)
  file_path, error = file_utils.save_text_to_file(text)

---

app.py (Streamlit UI)
─────────────────────
Responsibility: User interface and orchestration
Does:
  • Orchestrate the entire pipeline
  • Manage session state
  • Display UI elements
  • Handle user interactions
Uses: All other modules

Dependency Graph:
  • streamlit
  • config (settings, UI strings)
  • core (preprocessing, ocr_engine, postprocessing)
  • utils (file_utils)
  • PIL

Usage Pattern:
  # This is the entry point
  streamlit run app.py

"""

# =============================================================================
# DESIGN PATTERNS USED
# =============================================================================

"""
1. SEPARATION OF CONCERNS
   Each module handles one aspect (preprocessing, OCR, cleanup, I/O, UI)
   Easy to test, maintain, and extend individually

2. CONFIGURATION EXTERNALIZATION
   All settings in config/settings.py
   Easy to modify behavior without changing code
   Supports environment variables

3. ERROR HANDLING PATTERN
   Functions return (result, error) tuples where applicable
   Example: (image, error_message)
   Allows graceful degradation in UI

4. PIPELINE COMPOSITION
   Small functions composed into larger pipelines
   preprocess_image() calls grayscale(), denoise(), threshold(), etc.
   clean_text() calls multiple cleaning functions

5. LOGGING FOR DEBUGGING
   Structured logging throughout
   Helps diagnose issues in production

6. TYPE HINTS
   All functions have type annotations
   Makes code self-documenting
   Helps catch errors early

7. DOCSTRING DOCUMENTATION
   Every function has docstring explaining:
   - What it does
   - Parameters (with types)
   - Returns (with types)
   - Raises (exceptions)

"""

# =============================================================================
# KEY DECISION POINTS
# =============================================================================

"""
1. PIL vs OpenCV for Images
   Decision: Use PIL as primary format, convert to OpenCV when needed
   Why:
   • PIL (Pillow) is standard for file I/O and compatibility
   • OpenCV (cv2) is better for image processing algorithms
   • Conversion functions hide this complexity

2. Configuration Centralization
   Decision: All settings in config/settings.py
   Why:
   • Easy to find and modify settings
   • Supports different environments
   • No scattered magic constants

3. Separate Preprocessing, OCR, Postprocessing
   Decision: Three distinct modules
   Why:
   • Each can be tested independently
   • Easy to use modules individually
   • Clear responsibility boundaries
   • Easier to optimize each phase

4. Streamlit for UI
   Decision: Streamlit for rapid web development
   Why:
   • Simple to learn and deploy
   • Great for data science/ML apps
   • Fast iteration
   • Built-in components (file upload, download)

5. Tesseract via pytesseract
   Decision: Use pytesseract wrapper instead of subprocess
   Why:
   • Cleaner API
   • Better error handling
   • More Pythonic
   • Easier to maintain

"""

# =============================================================================
# TESTING STRATEGY
# =============================================================================

"""
How to test each module independently:

Testing preprocessing.py
────────────────────────
from core import preprocessing
from PIL import Image

# Load test image
img = Image.open("test.jpg")

# Test individual functions
gray = preprocessing.to_grayscale(img)
threshold = preprocessing.apply_threshold(gray)
denoised = preprocessing.denoise(img)

# Test full pipeline
processed = preprocessing.preprocess_image(img)

# Verify output
assert isinstance(processed, Image.Image)
assert processed.mode == "L"  # Should be grayscale

---

Testing ocr_engine.py
─────────────────────
from core import ocr_engine
from PIL import Image

# Initialize
ocr_engine.initialize_tesseract()

# Load preprocessed image
img = Image.open("processed.jpg")

# Test extraction
text = ocr_engine.extract_text(img)
assert isinstance(text, str)
assert len(text) > 0

# Test validation
is_valid, error = ocr_engine.validate_image_for_ocr(img)
assert is_valid is True

---

Testing postprocessing.py
─────────────────────────
from core import postprocessing

# Test individual functions
text = "  Hello   world  "
cleaned = postprocessing.remove_extra_whitespace(text)
assert cleaned == "Hello world"

text = "Line1\r\nLine2\rLine3"
fixed = postprocessing.fix_line_breaks(text)
assert "\\r" not in fixed

# Test stats
text = "Hello world. This is a test."
stats = postprocessing.get_text_stats(text)
assert stats["word_count"] > 0

---

Testing file_utils.py
─────────────────────
from utils import file_utils
from PIL import Image
import io

# Test image loading from file
img, error = file_utils.load_image("test.jpg")
assert img is not None
assert error is None

# Test image loading from BytesIO
file_like = io.BytesIO()
Image.new("RGB", (100, 100)).save(file_like, format="PNG")
file_like.seek(0)
img, error = file_utils.load_image(file_like)
assert img is not None

# Test text saving
text = "Extracted text"
path, error = file_utils.save_text_to_file(text)
assert path is not None
assert path.exists()

"""

# =============================================================================
# EXTENDING THE CODE
# =============================================================================

"""
Adding a New Preprocessing Technique
─────────────────────────────────────
1. Add function to core/preprocessing.py
2. Add configuration to config/settings.py
3. Add to preprocess_image() pipeline
4. Test independently
5. Add to UI sidebar (app.py)

Example: Adding brightness adjustment

# In core/preprocessing.py:
def adjust_brightness(image: Image.Image, factor: float = 1.0) -> Image.Image:
    \"\"\"Adjust image brightness.
    
    Args:
        image: PIL Image
        factor: 1.0 = normal, >1.0 = brighter, <1.0 = darker
    
    Returns:
        Adjusted PIL Image
    \"\"\"
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

# In config/settings.py:
IMAGE_PROCESSING = {
    ...,
    "brightness_enabled": False,
    "brightness_factor": 1.0,
}

# In core/preprocessing.py preprocess_image():
if config.get("brightness_enabled", False):
    processed = adjust_brightness(processed, config.get("brightness_factor", 1.0))

# In app.py sidebar:
brightness_enabled = st.checkbox("Adjust Brightness")
brightness_factor = st.slider("Brightness", 0.5, 2.0, 1.0, disabled=not brightness_enabled)

---

Adding Multi-Language Support (Phase 2)
────────────────────────────────────────
1. Update config/settings.py:
   SUPPORTED_LANGUAGES = ["eng", "fra", "deu", "spa", ...]

2. In app.py sidebar:
   selected_lang = st.selectbox("Language", SUPPORTED_LANGUAGES)

3. Pass to ocr_engine.extract_text():
   text = ocr_engine.extract_text(processed_image, language=selected_lang)

---

Adding PDF Support (Phase 2)
────────────────────────────
1. Implement utils/pdf_utils.py:
   - pdf_to_images(pdf_path) function
   - Batch process each page

2. In app.py:
   - Add PDF file upload support
   - Loop through pages
   - Run OCR on each page
   - Combine results

---

Adding Spell Checking (Phase 2)
───────────────────────────────
1. Add to postprocessing.py:
   def spellcheck(text: str, language: str = "en") -> str:
       from pyspellchecker import SpellChecker
       spell = SpellChecker(language=language)
       return " ".join(spell.correction(word) for word in text.split())

2. In config/settings.py:
   POSTPROCESSING["spellcheck_enabled"] = False

3. In postprocessing.clean_text():
   if config.get("spellcheck_enabled", False):
       text = spellcheck(text)

"""

# =============================================================================
# DEBUGGING TIPS
# =============================================================================

"""
Enable Detailed Logging
───────────────────────
In app.py or any module:
  import logging
  logging.basicConfig(level=logging.DEBUG)

Check Image Properties
──────────────────────
from PIL import Image
img = Image.open("test.jpg")
print(f"Size: {img.size}")
print(f"Mode: {img.mode}")
print(f"Format: {img.format}")

Test OCR Directly
─────────────────
python -c "
import pytesseract
from PIL import Image
img = Image.open('test.jpg')
print(pytesseract.image_to_string(img))
"

Inspect Preprocessing Steps
────────────────────────────
from core import preprocessing
from PIL import Image

img = Image.open("test.jpg")
gray = preprocessing.to_grayscale(img)
gray.save("debug_gray.jpg")

threshold = preprocessing.apply_threshold(gray)
threshold.save("debug_threshold.jpg")

# Compare original vs processed

Save Intermediate Results
─────────────────────────
from utils import file_utils

# Save preprocessed image for inspection
path, _ = file_utils.save_preprocessed_image(processed_image)
print(f"Saved to: {path}")

Profile Performance
───────────────────
import time

start = time.time()
processed = preprocessing.preprocess_image(image)
preprocess_time = time.time() - start

start = time.time()
text = ocr_engine.extract_text(processed)
ocr_time = time.time() - start

print(f"Preprocessing: {preprocess_time:.2f}s")
print(f"OCR: {ocr_time:.2f}s")

"""

# =============================================================================
# PERFORMANCE OPTIMIZATION
# =============================================================================

"""
Identified Performance Bottlenecks (in order):
──────────────────────────────────────────────
1. OCR (Tesseract) - 70-80% of time
   • Optimize image preprocessing
   • Disable unnecessary preprocessing
   • Use appropriate PSM mode

2. Deskew (Hough transform) - 10-20% of time
   • Disable if images are straight
   • Reduce edge detection parameters

3. Denoising - 5-10% of time
   • Reduce denoise_strength if quality acceptable
   • Disable if image is clean

4. Thresholding - <5% of time
   • Minimal impact

Optimization Strategies
──────────────────────
1. User-Configurable Pipeline
   ✓ Users can disable unused preprocessing
   ✓ No wasted computation

2. Cache Preprocessing Results (Future)
   • Remember settings per image type
   • Skip redundant operations

3. Parallel Processing (Phase 2)
   • Process multiple images simultaneously
   • Batch processing

4. GPU Acceleration (Future)
   • GPU-accelerated preprocessing
   • CUDA-enabled Tesseract if available

"""

# =============================================================================
# CODE QUALITY CHECKLIST
# =============================================================================

"""
Before committing changes:

□ All functions have type hints
□ All functions have docstrings
□ Error handling with try/except
□ Logging added for debugging
□ Code follows PEP 8 style
□ No unused imports
□ No hardcoded paths or values (use config)
□ Configuration centralized in settings.py
□ Module has single responsibility
□ Functions are testable in isolation
□ Comments explain "why", not "what"
□ Code is DRY (Don't Repeat Yourself)

"""

# =============================================================================
# SUMMARY
# =============================================================================

"""
SnapScribe OCR is structured for:

✅ MAINTAINABILITY: Clear module boundaries and responsibilities
✅ TESTABILITY: Each module can be tested independently
✅ EXTENSIBILITY: Easy to add new features (phases 2 & 3)
✅ READABILITY: Type hints, docstrings, and comments
✅ CONFIGURABILITY: Centralized settings management
✅ ROBUSTNESS: Error handling and validation throughout
✅ PERFORMANCE: Optimized pipeline with user control

The architecture supports both current MVP use and future enhancements.

"""

if __name__ == "__main__":
    print(__doc__)
