"""Image extraction from PDFs and model grounding output."""

from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image

log = logging.getLogger(__name__)


class ImageExtractor:
    """Extract images from PDF pages and model-detected regions."""

    def extract_embedded_images(self, pdf_path: str, page_num: int, output_dir: str) -> list[str]:
        """Extract all embedded images from a specific PDF page.

        Args:
            pdf_path: Path to the PDF.
            page_num: 0-indexed page number.
            output_dir: Directory to save extracted images.

        Returns:
            List of saved image file paths.
        """
        import fitz

        saved = []
        doc = fitz.open(pdf_path)

        try:
            page = doc[page_num]
            images = page.get_images(full=True)

            if not images:
                return saved

            images_dir = Path(output_dir) / "images"
            images_dir.mkdir(parents=True, exist_ok=True)

            for img_idx, img_info in enumerate(images):
                try:
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    if base_image is None:
                        continue

                    image_bytes = base_image["image"]
                    ext = base_image.get("ext", "png")

                    filename = f"page_{page_num + 1:03d}_embedded_{img_idx + 1:03d}.{ext}"
                    filepath = images_dir / filename

                    with open(filepath, "wb") as f:
                        f.write(image_bytes)

                    saved.append(str(filepath))
                    log.debug(f"Extracted embedded image: {filename}")

                except Exception as e:
                    log.warning(f"Failed to extract image {img_idx} from page {page_num}: {e}")

        finally:
            doc.close()

        return saved

    def extract_grounding_regions(
        self,
        source_image: Image.Image,
        regions: list[dict],
        page_num: int,
        output_dir: str,
    ) -> list[str]:
        """Crop and save image regions detected by the model's grounding.

        Args:
            source_image: The full page image used for OCR.
            regions: List of dicts with 'label' and 'coords' [x1,y1,x2,y2] (0-999 normalized).
            page_num: Page number for filename.
            output_dir: Directory to save cropped images.

        Returns:
            List of saved image file paths.
        """
        if not regions:
            return []

        saved = []
        images_dir = Path(output_dir) / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        w, h = source_image.size

        for idx, region in enumerate(regions):
            try:
                coords = region["coords"]
                # Coords are normalized to 0-999 range
                x1 = int(coords[0] / 999 * w)
                y1 = int(coords[1] / 999 * h)
                x2 = int(coords[2] / 999 * w)
                y2 = int(coords[3] / 999 * h)

                # Clamp to image bounds
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                if x2 <= x1 or y2 <= y1:
                    log.debug(f"Skipping invalid region: ({x1},{y1})-({x2},{y2})")
                    continue

                cropped = source_image.crop((x1, y1, x2, y2))

                filename = f"page_{page_num + 1:03d}_region_{idx + 1:03d}.png"
                filepath = images_dir / filename
                cropped.save(str(filepath), "PNG")

                saved.append(str(filepath))
                log.debug(f"Saved grounding region: {filename} ({x2-x1}x{y2-y1})")

            except Exception as e:
                log.warning(f"Failed to extract region {idx} from page {page_num}: {e}")

        return saved
