# DeepSeek OCR PRO V3

High-precision document OCR powered by [Surya](https://github.com/datalab-to/surya) and [marker-pdf](https://github.com/datalab-to/marker). Extracts text and images from scanned PDFs with state-of-the-art accuracy, full layout analysis, and 90+ language support.

## Features

- **CLI-first** with optional GUI - scriptable, automatable, testable
- **Multiple output formats**: TXT, TXT per page, DOCX, Markdown
- **Full layout analysis**: tables, headings, reading order preservation
- **90+ languages** including Italian, Latin, and scientific nomenclature
- **Image extraction**: embedded images from PDF pages
- **Checkpoint/resume**: interrupt and resume long OCR jobs
- **Cross-platform**: Windows, macOS, Linux

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Camponotus-vagus/DeepSeek-OCR-PRO.git
cd DeepSeek-OCR-PRO

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install
pip install -e ".[gui]"
```

OCR models are downloaded automatically on first run (managed by marker-pdf/Surya).

### Usage

```bash
# Basic OCR
deepseek-ocr document.pdf

# Multiple formats with image extraction
deepseek-ocr document.pdf -f txt -f markdown -f docx --extract-images

# Resume interrupted job
deepseek-ocr large_book.pdf --resume

# Specify languages (default: Italian + Latin)
deepseek-ocr document.pdf --languages it,la,en

# Process all PDFs in a directory
deepseek-ocr /path/to/pdfs/ -o ./output

# Launch GUI
deepseek-ocr --gui
```

### CLI Options

```
deepseek-ocr [OPTIONS] INPUT [INPUT...]

Arguments:
  INPUT                     PDF file(s) or directory

Options:
  -o, --output DIR          Output directory (default: ./output)
  -f, --format FMT          Output format: txt, txt_pages, docx, markdown
  --languages LANGS         Comma-separated OCR languages (default: it,la)
  --no-force-ocr            Skip OCR on pages with digital text
  --extract-images          Extract embedded images
  --resume                  Enable checkpoint/resume
  --gui                     Launch GUI mode
  --verbose                 Verbose logging
```

## System Requirements

- **Python**: 3.10+
- **RAM**: 8 GB minimum, 16 GB recommended
- **Disk**: ~2 GB (Surya model weights, downloaded automatically)
- **GPU** (optional): CUDA for faster processing (CPU works but is slower)

## Performance

Processing speed depends on page complexity and hardware:
- **GPU (CUDA)**: ~2-5 seconds per page
- **CPU**: ~5-30 minutes per page (varies with text density)

For long documents on CPU, use `--resume` to enable checkpoint/resume.

## Project Structure

```
src/deepseek_ocr/
  cli.py            # Command-line interface
  config.py         # Configuration management
  engine/           # OCR engine (marker-pdf/Surya), PDF handling
  pipeline/         # Orchestrator, checkpoint, progress
  output/           # TXT, DOCX, Markdown writers
  gui/              # Optional CustomTkinter GUI
  utils/            # Device detection, logging, paths
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src/deepseek_ocr --cov-report=html
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Surya OCR](https://github.com/datalab-to/surya) - Layout analysis and text recognition
- [marker-pdf](https://github.com/datalab-to/marker) - PDF-to-Markdown conversion pipeline
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing
