"""Tests for checkpoint/resume system."""

import json
import pytest
from pathlib import Path

from surya_ocr.engine.ocr_engine import PageResult
from surya_ocr.pipeline.checkpoint import CheckpointManager


class TestCheckpointManager:
    def test_init_creates_directory(self, sample_pdf, tmp_output):
        cm = CheckpointManager(sample_pdf, tmp_output)
        cm.init(10, "accurate")
        assert cm.checkpoint_dir.exists()
        assert (cm.checkpoint_dir / "meta.json").exists()

    def test_is_valid_after_init(self, sample_pdf, tmp_output):
        cm = CheckpointManager(sample_pdf, tmp_output)
        cm.init(10, "accurate")
        assert cm.is_valid(10) is True

    def test_is_valid_wrong_page_count(self, sample_pdf, tmp_output):
        cm = CheckpointManager(sample_pdf, tmp_output)
        cm.init(10, "accurate")
        assert cm.is_valid(20) is False

    def test_is_valid_no_checkpoint(self, sample_pdf, tmp_output):
        cm = CheckpointManager(sample_pdf, tmp_output)
        assert cm.is_valid(10) is False

    def test_save_and_load_page(self, sample_pdf, tmp_output):
        cm = CheckpointManager(sample_pdf, tmp_output)
        cm.init(10, "accurate")

        result = PageResult(page_number=3, raw_text="Test text", processing_time=1.5)
        cm.save_page(result)

        loaded = cm.load_page(3)
        assert loaded.page_number == 3
        assert loaded.raw_text == "Test text"
        assert loaded.processing_time == 1.5
        assert loaded.error is None

    def test_save_page_with_error(self, sample_pdf, tmp_output):
        cm = CheckpointManager(sample_pdf, tmp_output)
        cm.init(10, "accurate")

        result = PageResult(page_number=5, raw_text="", processing_time=0.1, error="OCR failed")
        cm.save_page(result)

        loaded = cm.load_page(5)
        assert loaded.error == "OCR failed"

    def test_get_completed_pages(self, sample_pdf, tmp_output):
        cm = CheckpointManager(sample_pdf, tmp_output)
        cm.init(10, "accurate")

        for i in [0, 2, 4, 7]:
            cm.save_page(PageResult(page_number=i, raw_text=f"Page {i}", processing_time=1.0))

        completed = cm.get_completed_pages()
        assert completed == {0, 2, 4, 7}

    def test_get_completed_pages_empty(self, sample_pdf, tmp_output):
        cm = CheckpointManager(sample_pdf, tmp_output)
        cm.init(10, "accurate")
        assert cm.get_completed_pages() == set()

    def test_cleanup(self, sample_pdf, tmp_output):
        cm = CheckpointManager(sample_pdf, tmp_output)
        cm.init(10, "accurate")
        cm.save_page(PageResult(page_number=0, raw_text="test", processing_time=1.0))

        assert cm.checkpoint_dir.exists()
        cm.cleanup()
        assert not cm.checkpoint_dir.exists()

    def test_unicode_text(self, sample_pdf, tmp_output):
        """Test with Italian and Latin text (like the Carabidi books)."""
        cm = CheckpointManager(sample_pdf, tmp_output)
        cm.init(5, "accurate")

        text = "Carabus italicus, specie endemica italiana. Distribuzione: Alpi e Appennini."
        result = PageResult(page_number=0, raw_text=text, processing_time=2.0)
        cm.save_page(result)

        loaded = cm.load_page(0)
        assert loaded.raw_text == text

    def test_special_chars_in_path(self, tmp_path):
        """Test with special characters in PDF path."""
        pdf_path = tmp_path / "file with spaces & accents e.pdf"

        # Create a minimal PDF
        import fitz
        doc = fitz.open()
        doc.new_page()
        doc.save(str(pdf_path))
        doc.close()

        output = str(tmp_path / "output")
        cm = CheckpointManager(str(pdf_path), output)
        cm.init(1, "test")
        assert cm.is_valid(1) is True
