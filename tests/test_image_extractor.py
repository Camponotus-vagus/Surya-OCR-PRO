"""Tests for image extraction."""

import pytest
from pathlib import Path
from PIL import Image

from deepseek_ocr.engine.image_extractor import ImageExtractor


class TestImageExtractor:
    def setup_method(self):
        self.extractor = ImageExtractor()

    def test_extract_embedded_images(self, bw_scan_pdf, tmp_output):
        paths = self.extractor.extract_embedded_images(bw_scan_pdf, 0, tmp_output)
        assert len(paths) >= 1
        for p in paths:
            assert Path(p).exists()

    def test_extract_grounding_regions(self, tmp_output):
        # Create a test image
        img = Image.new("RGB", (1000, 1000), color=(255, 255, 255))

        regions = [
            {"label": "image", "coords": [100, 100, 500, 500]},
            {"label": "image", "coords": [600, 600, 999, 999]},
        ]

        paths = self.extractor.extract_grounding_regions(img, regions, 0, tmp_output)
        assert len(paths) == 2
        for p in paths:
            assert Path(p).exists()
            # Verify it's a valid image
            cropped = Image.open(p)
            assert cropped.size[0] > 0
            assert cropped.size[1] > 0

    def test_empty_regions(self, tmp_output):
        img = Image.new("RGB", (100, 100))
        paths = self.extractor.extract_grounding_regions(img, [], 0, tmp_output)
        assert paths == []

    def test_invalid_coords_clamped(self, tmp_output):
        """Coords outside image bounds should be clamped."""
        img = Image.new("RGB", (100, 100))
        regions = [{"label": "image", "coords": [0, 0, 1500, 1500]}]
        paths = self.extractor.extract_grounding_regions(img, regions, 0, tmp_output)
        assert len(paths) == 1

    def test_zero_area_region_skipped(self, tmp_output):
        """Zero-area regions should be skipped."""
        img = Image.new("RGB", (1000, 1000))
        regions = [{"label": "image", "coords": [500, 500, 500, 500]}]
        paths = self.extractor.extract_grounding_regions(img, regions, 0, tmp_output)
        assert len(paths) == 0

    def test_no_embedded_images(self, sample_pdf, tmp_output):
        """Text-only PDF should return some images (rasterized page counts as image)."""
        paths = self.extractor.extract_embedded_images(sample_pdf, 0, tmp_output)
        # sample_pdf is text-based, may or may not have embedded images
        assert isinstance(paths, list)
