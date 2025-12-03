"""
Import verification script - Ensures all modules can be imported successfully.

Run this after installation to verify the project is set up correctly:
    python verify_imports.py

If all imports succeed, you're ready to run:
    streamlit run app.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("SnapScribe OCR - Import Verification")
print("=" * 60)

# Track results
passed = []
failed = []

# Test imports
tests = [
    ("config.settings", "Configuration"),
    ("core.preprocessing", "Image Preprocessing"),
    ("core.ocr_engine", "OCR Engine"),
    ("core.postprocessing", "Text Postprocessing"),
    ("utils.file_utils", "File Utilities"),
    ("utils.pdf_utils", "PDF Utilities"),
]

print("\nTesting imports...\n")

for module_name, description in tests:
    try:
        __import__(module_name)
        print(f"✅ {module_name:<25} ({description})")
        passed.append(module_name)
    except ImportError as e:
        print(f"❌ {module_name:<25} ({description})")
        print(f"   Error: {str(e)}")
        failed.append((module_name, str(e)))

print("\n" + "=" * 60)
print(f"Results: {len(passed)} passed, {len(failed)} failed")
print("=" * 60)

if failed:
    print("\n⚠️  Import Failures:\n")
    for module_name, error in failed:
        print(f"  • {module_name}")
        print(f"    {error}\n")
    print("\nTroubleshooting:")
    print("  1. Ensure requirements.txt is installed: pip install -r requirements.txt")
    print("  2. Check Python version: python --version (must be 3.8+)")
    print("  3. Verify Tesseract is installed on system")
    sys.exit(1)
else:
    print("\n✅ All imports successful!")
    print("\nYou're ready to run SnapScribe:")
    print("  streamlit run app.py")
    sys.exit(0)
