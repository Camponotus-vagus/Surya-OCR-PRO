"""Tests for output writers."""

import pytest
from pathlib import Path

from surya_ocr.engine.ocr_engine import PageResult
from surya_ocr.output.writer_txt import write_txt, write_txt_per_page
from surya_ocr.output.writer_markdown import write_markdown


def _make_results(n=3):
    return [
        PageResult(page_number=i, raw_text=f"Content of page {i + 1}.", processing_time=1.0)
        for i in range(n)
    ]


class TestTxtWriter:
    def test_write_single_file(self, tmp_output):
        results = _make_results(3)
        path = write_txt(results, tmp_output, "test_doc")

        content = Path(path).read_text(encoding="utf-8")
        assert "Content of page 1" in content
        assert "Content of page 2" in content
        assert "Content of page 3" in content

    def test_write_per_page(self, tmp_output):
        results = _make_results(3)
        paths = write_txt_per_page(results, tmp_output, "test_doc")

        assert len(paths) == 3
        for i, path in enumerate(paths):
            content = Path(path).read_text(encoding="utf-8")
            assert f"Content of page {i + 1}" in content

    def test_write_with_errors(self, tmp_output):
        results = [
            PageResult(page_number=0, raw_text="Good page", processing_time=1.0),
            PageResult(page_number=1, raw_text="", processing_time=0.1, error="Failed"),
        ]
        path = write_txt(results, tmp_output, "test_errors")
        content = Path(path).read_text(encoding="utf-8")
        assert "Good page" in content
        assert "Error" in content

    def test_write_empty_results(self, tmp_output):
        path = write_txt([], tmp_output, "empty")
        content = Path(path).read_text(encoding="utf-8")
        assert content == ""

    def test_unicode_content(self, tmp_output):
        results = [
            PageResult(page_number=0, raw_text="Carabus italicus e distribuzione alpina", processing_time=1.0),
        ]
        path = write_txt(results, tmp_output, "unicode_test")
        content = Path(path).read_text(encoding="utf-8")
        assert "italicus" in content


class TestMarkdownWriter:
    def test_write_markdown(self, tmp_output):
        results = _make_results(2)
        path = write_markdown(results, tmp_output, "test_doc")

        content = Path(path).read_text(encoding="utf-8")
        assert "# test_doc" in content
        assert "Content of page 1" in content
        assert "---" in content  # Separator

    def test_write_with_errors(self, tmp_output):
        results = [
            PageResult(page_number=0, raw_text="", processing_time=0.1, error="OCR failed"),
        ]
        path = write_markdown(results, tmp_output, "error_doc")
        content = Path(path).read_text(encoding="utf-8")
        assert "Error" in content


class TestDocxWriter:
    def test_write_docx(self, tmp_output):
        try:
            from surya_ocr.output.writer_docx import write_docx
        except ImportError:
            pytest.skip("python-docx not installed")

        results = _make_results(2)
        path = write_docx(results, tmp_output, "test_doc")

        assert Path(path).exists()
        assert path.endswith(".docx")

        # Read back and verify
        from docx import Document
        doc = Document(path)
        full_text = "\n".join(p.text for p in doc.paragraphs)
        assert "Content of page 1" in full_text
        assert "Content of page 2" in full_text
