"""Tests for text post-processing."""

from surya_ocr.engine.text_postprocessor import (
    clean_ocr_text,
    clean_for_markdown,
    extract_grounding_regions,
)


class TestCleanOcrText:
    def test_basic_text(self):
        assert clean_ocr_text("Hello world") == "Hello world"

    def test_removes_markdown_headers(self):
        text = "## Title\n\nParagraph"
        result = clean_ocr_text(text)
        assert result == "Title\n\nParagraph"

    def test_removes_bold_italic(self):
        text = "This is **bold** and *italic* text"
        result = clean_ocr_text(text)
        assert "**" not in result
        assert "*" not in result
        assert "bold" in result
        assert "italic" in result

    def test_removes_horizontal_rules(self):
        text = "Above\n---\nBelow"
        result = clean_ocr_text(text)
        assert "---" not in result

    def test_removes_image_references(self):
        text = "Text ![alt](image.png) more text"
        result = clean_ocr_text(text)
        assert "![" not in result

    def test_normalizes_blank_lines(self):
        text = "line1\n\n\n\n\nline2"
        result = clean_ocr_text(text)
        assert result == "line1\n\nline2"

    def test_strips_trailing_whitespace(self):
        text = "line1   \nline2  \n"
        result = clean_ocr_text(text)
        assert "   " not in result

    def test_empty_text(self):
        assert clean_ocr_text("") == ""


class TestCleanForMarkdown:
    def test_preserves_markdown(self):
        text = "# Title\n\n**Bold** and *italic*"
        result = clean_for_markdown(text)
        assert "# Title" in result
        assert "**Bold**" in result

    def test_normalizes_blank_lines(self):
        text = "para1\n\n\n\n\npara2"
        result = clean_for_markdown(text)
        assert result == "para1\n\npara2"

    def test_strips_trailing_whitespace(self):
        text = "line1   \nline2  "
        result = clean_for_markdown(text)
        assert "   " not in result


class TestExtractGroundingRegions:
    def test_returns_empty_list(self):
        """marker-pdf doesn't use grounding tags, so always returns empty."""
        assert extract_grounding_regions("any text") == []

    def test_empty_text(self):
        assert extract_grounding_regions("") == []
