# SnapScribe OCR - Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Install Tesseract (One-time setup)

**Windows:**
- Download: https://github.com/UB-Mannheim/tesseract/wiki
- Run installer (accepts defaults)
- Tesseract is now ready ✓

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### 2. Install Python Dependencies

```bash
# Navigate to project directory
cd SnapScribe

# Create virtual environment (recommended)
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the App

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`

## 🎯 Using the App

1. **Upload**: Click "Upload an image" and select a JPEG or PNG
2. **Configure**: Adjust preprocessing in the sidebar (most images work with defaults)
3. **Extract**: Click "🚀 Extract Text"
4. **Download**: Click download button to save as .txt

## ⚙️ Common Settings

| Issue | Solution |
|-------|----------|
| Blurry text | Enable "Remove Noise" + increase strength |
| Dark/reversed colors | Enable "Apply Thresholding" |
| Tilted text | Enable "Auto-Correct Rotation" |
| Lots of spaces | Enable "Remove Extra Spaces" |

## 🆘 Troubleshooting

**"Tesseract not found"**
- Windows: Ensure installer ran, restart terminal
- macOS: `brew install tesseract`
- Linux: `apt-get install tesseract-ocr`

**"Bad OCR results"**
- Ensure image is 200x200+ pixels
- Text should be clearly visible
- Try enabling preprocessing options

**"App won't start"**
- Check Python version: `python --version` (must be 3.8+)
- Verify all dependencies: `pip list`
- Check for typos in file paths

## 📁 Project Structure

```
SnapScribe/
├── app.py                    # Main Streamlit app
├── config/settings.py        # Configuration
├── core/                     # OCR pipeline
│   ├── preprocessing.py      # Image processing
│   ├── ocr_engine.py         # Tesseract interface
│   └── postprocessing.py     # Text cleanup
├── utils/
│   ├── file_utils.py         # File handling
│   └── pdf_utils.py          # PDF support (Phase 2)
└── samples/                  # Sample images/outputs
```

## 🎓 Learning the Code

1. **Start with** `app.py` - see how UI orchestrates the pipeline
2. **Explore** `core/preprocessing.py` - image manipulation with OpenCV
3. **Check** `core/ocr_engine.py` - Tesseract interaction
4. **Review** `config/settings.py` - all configuration in one place

## 🚀 Next Steps

After Phase 1 works:

- **Phase 2**: Add PDF support, multiple languages, batch processing
- **Phase 3**: Deploy to Streamlit Cloud, add spell checking

See `README.md` for full documentation and roadmap.

## 📝 Tips for Best Results

- **Clear images**: Higher resolution = better OCR
- **Good contrast**: Text should be dark on light background
- **Straight text**: Minimal rotation works best
- **Test preprocessing**: Try different settings for different image types

---

**Stuck?** Check the troubleshooting section above or review README.md for detailed guidance.

Happy OCR-ing! 🎉
