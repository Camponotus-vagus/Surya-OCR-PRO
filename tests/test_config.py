"""Tests for configuration module."""

import json
import pytest
from pathlib import Path

from deepseek_ocr.config import OCRConfig


class TestOCRConfig:
    def test_defaults(self):
        config = OCRConfig()
        assert config.languages == ["it", "la"]
        assert config.force_ocr is True
        assert config.formats == ["txt"]
        assert config.resume is False
        assert config.extract_images is False

    def test_custom_languages(self):
        config = OCRConfig(languages=["en", "fr", "de"])
        assert config.languages == ["en", "fr", "de"]

    def test_validate_no_pdfs(self):
        config = OCRConfig()
        errors = config.validate()
        assert any("No PDF" in e for e in errors)

    def test_validate_missing_pdf(self):
        config = OCRConfig(pdf_paths=["/nonexistent/file.pdf"])
        errors = config.validate()
        assert any("not found" in e for e in errors)

    def test_validate_not_a_pdf(self, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not a pdf")
        config = OCRConfig(pdf_paths=[str(txt_file)])
        errors = config.validate()
        assert any("Not a PDF" in e for e in errors)

    def test_validate_invalid_format(self):
        config = OCRConfig(pdf_paths=[], formats=["html"])
        errors = config.validate()
        assert any("Invalid format" in e for e in errors)

    def test_validate_invalid_workers(self):
        config = OCRConfig(pdf_paths=[], num_workers=0)
        errors = config.validate()
        assert any("num_workers" in e for e in errors)

    def test_from_file_json(self, tmp_path):
        config_data = {
            "languages": ["en", "de"],
            "formats": ["txt", "markdown"],
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        config = OCRConfig.from_file(str(config_file))
        assert config.languages == ["en", "de"]
        assert config.formats == ["txt", "markdown"]

    def test_to_dict(self):
        config = OCRConfig(formats=["txt", "docx"])
        d = config.to_dict()
        assert d["formats"] == ["txt", "docx"]
        assert isinstance(d, dict)

    def test_valid_config(self, sample_pdf):
        config = OCRConfig(
            pdf_paths=[sample_pdf],
        )
        errors = config.validate()
        assert len(errors) == 0
