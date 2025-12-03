# SnapScribe - OCR Text Extraction Tool

![SnapScribe](https://img.shields.io/badge/Version-3.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green.svg)

## 📋 Project Description

**SnapScribe** is a modern, user-friendly OCR (Optical Character Recognition) application that converts scanned documents, images, and PDFs into searchable, editable text. Powered by Tesseract OCR and built with Streamlit, it makes document digitization accessible to everyone—no technical expertise required.

### Problem Statement

Millions of documents exist only in image or PDF form, making them unsearchable and difficult to work with digitally. SnapScribe solves this by:
- Converting image and PDF documents to editable text in seconds
- Supporting multiple languages out of the box
- Providing batch processing for bulk document conversion
- Offering a clean, intuitive web interface

### Why SnapScribe?

✨ **Easy to Use** - Upload files and get results immediately  
🎯 **Accurate** - Powered by industry-standard Tesseract OCR  
⚡ **Fast** - Process single images or batch 20+ files at once  
🌍 **Multi-Language** - Supports 7+ languages out of the box  
📱 **Web-Based** - Access from any device with a browser  
☁️ **Deployable** - One-click deployment to Streamlit Cloud  

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9 or higher**
- **Tesseract OCR** (system dependency)
- **Git** (optional, for cloning)

### Installation

#### 1. Clone or Download the Repository

```bash
git clone https://github.com/yourusername/snapscribe.git
cd snapscribe
```

#### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Install Tesseract OCR

SnapScribe requires Tesseract to be installed on your system. Choose your OS:

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Run the installer
- Default installation path: `C:\Program Files\Tesseract-OCR\`

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

#### 5. (Optional) Install Poppler for PDF Support

PDF processing requires Poppler. This is **optional**—the app works great for images without it.

**Windows:**
- Download from: https://github.com/oschwartz10612/poppler-windows/releases/
- Extract to `C:\poppler` (or set `POPPLER_PATH` environment variable)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

#### 6. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## ✨ Features

### 🖼️ Single Image OCR
- Upload images (PNG, JPG, BMP, TIFF)
- Extract text instantly
- Advanced preprocessing options
- Select from 7+ OCR languages
- Download or copy results

### 📸 Batch Image Processing
- Upload up to 20 images simultaneously
- Apply consistent settings to all
- Real-time progress tracking
- Download results as TXT file

### 📄 PDF to Text Conversion
- Upload PDF files (multi-page supported)
- Select specific page ranges
- Control output quality (DPI: 100-300)
- Extract text from each page

### 🌍 Supported Languages
English, Spanish, French, German, Portuguese, Italian, Russian, Chinese, and more!

### 🔧 Advanced Features
- **Spell Checking** - Automatic text correction
- **Text Cleanup** - Remove OCR artifacts
- **Flexible Preprocessing** - Customize image enhancement
- **Progress Tracking** - Real-time status updates

---

## 💻 Technology Stack

- **Python 3.9+**
- **Streamlit 1.28+** - Web interface
- **Tesseract OCR** - Text recognition
- **OpenCV 4.8+** - Image processing
- **Pillow 10+** - Image handling
- **PyPDF2 4.0+** - PDF parsing
- **pdf2image 1.17+** - PDF conversion
- **pyspellchecker 0.8+** - Text correction

---

## 📖 How to Use

### Single Image OCR
1. Open **"🖼️ Single Image OCR"** tab
2. Upload an image
3. Configure preprocessing if needed
4. Select language
5. Click **"🚀 Extract Text"**
6. Download results

### Batch Processing
1. Open **"📸 Batch Processing"** tab
2. Upload 1-20 images
3. Configure settings
4. Click **"🚀 Process All Images"**
5. Download results

### PDF to Text
1. Open **"📄 PDF to Text"** tab
2. Upload a PDF
3. Select page range and DPI
4. Click processing buttons
5. Download results

---

## ⚙️ Configuration

SnapScribe works out-of-the-box! Optional customization:

```bash
# Set Tesseract path (if not auto-detected)
export TESSERACT_PATH="/path/to/tesseract"

# Set Poppler path (for PDF support)
export POPPLER_PATH="/path/to/poppler/bin"
```

See `CONFIG_EXAMPLES.md` for more options.

---


## 📚 Documentation

- **[START_HERE.md](START_HERE.md)** - Entry point, quick orientation
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[README.md](README.md)** - Complete reference documentation
- **[DEVELOPERS_GUIDE.md](DEVELOPERS_GUIDE.md)** - Architecture & code patterns
- **[CONFIG_EXAMPLES.md](CONFIG_EXAMPLES.md)** - Configuration profiles

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Tesseract not found" | Install Tesseract (see Installation section) |
| "Poppler not found" | Optional - install only if you need PDF support |
| Poor OCR results | Enable preprocessing (Grayscale, Denoise, Threshold) |
| App runs slowly | Reduce image resolution or lower PDF DPI |

See detailed troubleshooting in `SETUP_GUIDE.md`

---

## 👨‍💻 Contributing

We welcome contributions! See [DEVELOPERS_GUIDE.md](DEVELOPERS_GUIDE.md) for:
- Code style guidelines
- Development setup
- Testing procedures
- Pull request process

---

## 💬 Support

- 📖 Check [Troubleshooting](#troubleshooting) above
- 📚 Read detailed [Documentation](#-documentation)
- 🐛 [Report issues](https://github.com/yourusername/snapscribe/issues)
- 💭 [Ask questions](https://github.com/yourusername/snapscribe/discussions)

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🎉 Get Started Now!

```bash
git clone https://github.com/yourusername/snapscribe.git
cd snapscribe
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 and start extracting text!

---

## 👩‍💻 Author

**Sanskruti Sugandhi**
*AI & Data Science Engineer*

📫 **Connect:**

- **GitHub:** [sanskruti048](https://github.com/sanskruti048)
- **LinkedIn:** [Sanskruti Sugandhi](https://www.linkedin.com/in/sanskruti-sugandhi/)
- **Blog:** [dev.to/sanskruti_sugandhi](https://dev.to/sanskruti_sugandhi)

---

**Sanskruti Sugandhi**
*AI & Data Science Engineer*

📫 **Connect:**

- **GitHub:** [sanskruti048](https://github.com/sanskruti048)
- **LinkedIn:** [Sanskruti Sugandhi](https://www.linkedin.com/in/sanskruti-sugandhi/)
- **Blog:** [dev.to/sanskruti_sugandhi](https://dev.to/sanskruti_sugandhi)

---
