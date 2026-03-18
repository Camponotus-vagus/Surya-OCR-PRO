"""Test fixtures for Surya OCR PRO."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def tmp_output(tmp_path):
    """Temporary output directory."""
    out = tmp_path / "output"
    out.mkdir()
    return str(out)


@pytest.fixture
def sample_pdf(tmp_path):
    """Create a minimal 1-page PDF with text content."""
    import fitz

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((72, 72), "This is a test document.", fontsize=12)
    page.insert_text((72, 100), "It contains sample text for OCR testing.", fontsize=12)
    page.insert_text((72, 128), "Page 1 of 1.", fontsize=10)

    pdf_path = tmp_path / "test_document.pdf"
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


@pytest.fixture
def multi_page_pdf(tmp_path):
    """Create a 5-page PDF."""
    import fitz

    doc = fitz.open()
    for i in range(5):
        page = doc.new_page(width=595, height=842)
        page.insert_text((72, 72), f"Page {i + 1} content", fontsize=14)
        page.insert_text((72, 100), f"This is page number {i + 1} of the test document.", fontsize=12)

    pdf_path = tmp_path / "multi_page.pdf"
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


@pytest.fixture
def bw_scan_pdf(tmp_path):
    """Create a PDF that simulates a B&W scanned page (image-based)."""
    import fitz
    from PIL import Image
    import io

    # Create a B&W image
    img = Image.new("1", (2835, 4074), color=1)  # White background
    # Draw some black rectangles to simulate text
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    for y in range(100, 3900, 50):
        draw.rectangle([200, y, 2600, y + 20], fill=0)

    # Save image to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Create PDF with embedded image
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    rect = page.rect
    page.insert_image(rect, stream=img_bytes.read())

    pdf_path = tmp_path / "bw_scan.pdf"
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


@pytest.fixture
def empty_pdf(tmp_path):
    """Create a PDF that appears empty (1 blank page, since PyMuPDF requires >= 1 page)."""
    import fitz

    doc = fitz.open()
    doc.new_page(width=595, height=842)  # Blank page
    pdf_path = tmp_path / "empty.pdf"
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


@pytest.fixture
def default_config(tmp_path, sample_pdf):
    """Default OCRConfig for testing."""
    from surya_ocr.config import OCRConfig
    return OCRConfig(
        pdf_paths=[sample_pdf],
        output_dir=str(tmp_path / "output"),
        formats=["txt"],
    )
