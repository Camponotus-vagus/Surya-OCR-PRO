"""Tests for PDF handler."""

import pytest
from PIL import Image

from deepseek_ocr.engine.pdf_handler import PDFHandler


class TestPDFHandler:
    def setup_method(self):
        self.handler = PDFHandler()

    def test_get_page_count(self, sample_pdf):
        assert self.handler.get_page_count(sample_pdf) == 1

    def test_get_page_count_multi(self, multi_page_pdf):
        assert self.handler.get_page_count(multi_page_pdf) == 5

    def test_get_page_count_blank(self, empty_pdf):
        """A 'blank' PDF still has 1 page (PyMuPDF requires >= 1 page)."""
        assert self.handler.get_page_count(empty_pdf) == 1

    def test_get_page_count_nonexistent(self):
        assert self.handler.get_page_count("/nonexistent.pdf") == 0

    def test_extract_page_image(self, sample_pdf):
        img = self.handler.extract_page_image(sample_pdf, 0)
        assert isinstance(img, Image.Image)
        assert img.mode == "RGB"
        assert img.size[0] > 0
        assert img.size[1] > 0

    def test_extract_page_image_multi(self, multi_page_pdf):
        for i in range(5):
            img = self.handler.extract_page_image(multi_page_pdf, i)
            assert isinstance(img, Image.Image)
            assert img.mode == "RGB"

    def test_extract_page_out_of_range(self, sample_pdf):
        with pytest.raises(RuntimeError, match="out of range"):
            self.handler.extract_page_image(sample_pdf, 10)

    def test_extract_page_negative(self, sample_pdf):
        with pytest.raises(RuntimeError, match="out of range"):
            self.handler.extract_page_image(sample_pdf, -1)

    def test_extract_bw_scan(self, bw_scan_pdf):
        """B&W scanned pages should be converted to RGB."""
        img = self.handler.extract_page_image(bw_scan_pdf, 0)
        assert isinstance(img, Image.Image)
        assert img.mode == "RGB"
        assert img.size[0] > 100
        assert img.size[1] > 100

    def test_get_pdf_info(self, sample_pdf):
        info = self.handler.get_pdf_info(sample_pdf)
        assert info["page_count"] == 1
        assert "page_size" in info
        assert info["filename"] == "test_document.pdf"

    def test_get_pdf_info_scanned(self, bw_scan_pdf):
        info = self.handler.get_pdf_info(bw_scan_pdf)
        assert info["is_scanned"] is True
