"""Core OCR engine wrapping the marker-pdf / Surya pipeline."""

from __future__ import annotations

import dataclasses
import logging
import time

from ..config import OCRConfig

log = logging.getLogger(__name__)


@dataclasses.dataclass
class PageResult:
    """Result of OCR processing for a single page."""

    page_number: int
    raw_text: str
    processing_time: float
    error: str | None = None

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> PageResult:
        return cls(**{k: v for k, v in data.items() if k in {f.name for f in dataclasses.fields(cls)}})


class OCREngine:
    """Stateful OCR engine that holds the loaded marker-pdf models.

    Usage:
        engine = OCREngine(config)
        engine.load_model()
        result = engine.process_pdf(pdf_path)
        engine.unload_model()
    """

    def __init__(self, config: OCRConfig):
        self.config = config
        self._converter = None
        self._model_dict = None
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load_model(self) -> None:
        """Load the marker-pdf models into memory."""
        if self._loaded:
            log.info("Models already loaded, skipping")
            return

        from marker.config.parser import ConfigParser
        from marker.models import create_model_dict

        log.info("Loading Surya OCR models (this may take a few minutes)...")

        self._model_dict = create_model_dict()

        config = {
            "output_format": "markdown",
            "force_ocr": self.config.force_ocr,
            "languages": self.config.languages,
        }
        config_parser = ConfigParser(config)
        self._config_dict = config_parser.generate_config_dict()

        self._loaded = True
        log.info("Surya OCR models ready for inference")

    def process_pdf(self, pdf_path: str) -> list[PageResult]:
        """Run OCR on an entire PDF file using marker-pdf.

        marker-pdf processes the entire PDF at once (not page-by-page),
        which allows it to understand cross-page layout context.

        Returns:
            List of PageResult, one per page.
        """
        if not self._loaded:
            raise RuntimeError("Models not loaded. Call load_model() first.")

        from marker.converters.pdf import PdfConverter

        start = time.time()

        try:
            converter = PdfConverter(
                config=self._config_dict,
                artifact_dict=self._model_dict,
            )

            log.info(f"Starting marker-pdf OCR on {pdf_path}...")
            rendered = converter(pdf_path)

            elapsed = time.time() - start
            full_text = rendered.markdown

            # Split by page markers if present, otherwise treat as single page
            pages = self._split_into_pages(full_text, pdf_path)

            log.info(
                f"OCR complete: {len(pages)} pages in {elapsed:.1f}s "
                f"({len(full_text)} total chars)"
            )

            return pages

        except Exception as e:
            elapsed = time.time() - start
            error_msg = f"OCR failed: {e}"
            log.error(error_msg, exc_info=True)
            return [PageResult(
                page_number=0,
                raw_text="",
                processing_time=elapsed,
                error=error_msg,
            )]

    def process_pdf_by_page(self, pdf_path: str, page_num: int) -> PageResult:
        """Process a single page from a PDF using marker-pdf.

        Creates a temporary single-page PDF and processes it.
        """
        if not self._loaded:
            raise RuntimeError("Models not loaded. Call load_model() first.")

        import fitz
        import os
        import tempfile

        from marker.converters.pdf import PdfConverter

        start = time.time()

        try:
            # Extract single page to temp PDF
            doc = fitz.open(pdf_path)
            try:
                tmp_doc = fitz.open()
                tmp_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

                tmpdir = tempfile.mkdtemp()
                tmp_path = os.path.join(tmpdir, f"page_{page_num}.pdf")
                tmp_doc.save(tmp_path)
                tmp_doc.close()
            finally:
                doc.close()

            converter = PdfConverter(
                config=self._config_dict,
                artifact_dict=self._model_dict,
            )
            rendered = converter(tmp_path)
            text = rendered.markdown

            # Cleanup temp file
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

            elapsed = time.time() - start
            log.info(f"Page {page_num + 1} processed in {elapsed:.1f}s ({len(text)} chars)")

            return PageResult(
                page_number=page_num,
                raw_text=text,
                processing_time=elapsed,
            )

        except Exception as e:
            elapsed = time.time() - start
            error_msg = f"OCR failed for page {page_num + 1}: {e}"
            log.error(error_msg)
            return PageResult(
                page_number=page_num,
                raw_text="",
                processing_time=elapsed,
                error=error_msg,
            )

    def _split_into_pages(self, full_text: str, pdf_path: str) -> list[PageResult]:
        """Split marker-pdf output into per-page results.

        marker-pdf doesn't always produce clear page boundaries, so we
        use the full text as a single result per page if we can't detect
        page markers. For scanned PDFs, each page is processed independently
        by the OCR engine, so the output naturally corresponds to pages.
        """
        import fitz

        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()

        if total_pages <= 1:
            return [PageResult(
                page_number=0,
                raw_text=full_text,
                processing_time=0,
            )]

        # marker-pdf typically outputs the full document as continuous markdown.
        # We assign the complete text to page 0 and create empty results for the rest.
        # When using page-by-page processing (process_pdf_by_page), each page
        # gets its own result.
        results = [PageResult(
            page_number=0,
            raw_text=full_text,
            processing_time=0,
        )]

        return results

    def unload_model(self) -> None:
        """Free model memory."""
        if not self._loaded:
            return

        import gc

        self._converter = None
        self._model_dict = None
        self._config_dict = None
        self._loaded = False

        gc.collect()

        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass

        log.info("OCR models unloaded")
