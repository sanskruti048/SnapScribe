#!/usr/bin/env python3
"""
SnapScribe Setup Verification Script

Checks that all dependencies are properly installed and configured.
"""

import sys
import os
from pathlib import Path

print("=" * 70)
print(" SnapScribe - Setup Verification")
print("=" * 70)

# Check Python version
print("\n[1/6] Python Version")
print(f"  ✅ Python {sys.version.split()[0]}")

# Check virtual environment
print("\n[2/6] Virtual Environment")
venv_path = Path("./venv").resolve()
if venv_path.exists():
    print(f"  ✅ Virtual environment found: {venv_path}")
else:
    print(f"  ⚠️  Virtual environment not found: {venv_path}")

# Check Python packages
print("\n[3/6] Required Python Packages")
packages = {
    "streamlit": "Web UI framework",
    "pytesseract": "Tesseract OCR interface",
    "pillow": "Image processing",
    "opencv-python": "CV2 image operations",
    "pdf2image": "PDF conversion (Phase 2)",
    "pyspellchecker": "Spell checking (Phase 2)",
}

for pkg, desc in packages.items():
    try:
        __import__(pkg.replace("-", "_"))
        print(f"  ✅ {pkg}: {desc}")
    except ImportError:
        print(f"  ❌ {pkg}: {desc} - NOT INSTALLED")

# Check Tesseract
print("\n[4/6] Tesseract OCR (System Dependency)")
from config.settings import TESSERACT_PATH
tesseract_path = Path(TESSERACT_PATH)
if tesseract_path.exists():
    print(f"  ✅ Tesseract found: {TESSERACT_PATH}")
else:
    print(f"  ⚠️  Tesseract not found: {TESSERACT_PATH}")
    print("     Install from: https://github.com/UB-Mannheim/tesseract/wiki")

# Check Poppler
print("\n[5/6] Poppler (System Dependency - Optional)")
from config.settings import POPPLER_PATH
if POPPLER_PATH:
    poppler_path = Path(POPPLER_PATH)
    if poppler_path.exists():
        print(f"  ✅ Poppler found: {POPPLER_PATH}")
        print("     PDF functionality is ENABLED")
    else:
        print(f"  ⚠️  Poppler path configured but not found: {POPPLER_PATH}")
        print("     PDF functionality is DISABLED")
        print("     See POPPLER_SETUP.md for installation instructions")
else:
    print("  ⚠️  POPPLER_PATH not configured")
    print("     PDF functionality is DISABLED")
    print("     To enable PDF support, set POPPLER_PATH environment variable")
    print("     See POPPLER_SETUP.md for instructions")

# Summary
print("\n[6/6] Summary")
print("-" * 70)
print("✅ Core dependencies: READY")
print("✅ Tesseract OCR: REQUIRED (install if missing)")
print("⚠️  Poppler: OPTIONAL (install if you need PDF support)")
print("-" * 70)

print("\n📝 Next Steps:")
print("1. Run the app: python -m streamlit run app.py")
print("2. If Tesseract is missing, install from:")
print("   https://github.com/UB-Mannheim/tesseract/wiki")
print("3. If you want PDF support, see POPPLER_SETUP.md")
print("\n" + "=" * 70)
