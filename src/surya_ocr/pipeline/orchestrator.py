"""Pipeline orchestrator: coordinates PDF processing with checkpoint and output."""

from __future__ import annotations

import gc
import logging
from pathlib import Path
from typing import Callable, Optional

from ..config import OCRConfig
from ..engine.ocr_engine import OCREngine, PageResult
from ..engine.pdf_handler import PDFHandler
from ..output.writer_txt import write_txt, write_txt_per_page
from ..output.writer_docx import write_docx
from ..output.writer_markdown import write_markdown
from .checkpoint import CheckpointManager
from .progress import ProgressReporter

log = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrates the full OCR pipeline for one or more PDFs.

    Processes each page individually via marker-pdf, with:
    - Checkpoint/resume support
    - Multiple output format generation
    - Image extraction from PDF
    """

    def __init__(
        self,
        config: OCRConfig,
        engine: OCREngine,
        progress_callback: Optional[Callable[[int, int, float], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ):
        self.config = config
        self.engine = engine
        self.pdf_handler = PDFHandler()
        self._progress_cb = progress_callback
        self._status_cb = status_callback
        self._cancel_check = cancel_check

    def run_all(self) -> None:
        """Process all PDFs in the config."""
        for i, pdf_path in enumerate(self.config.pdf_paths):
            log.info(f"Processing PDF {i + 1}/{len(self.config.pdf_paths)}: {pdf_path}")
            if self._status_cb:
                self._status_cb(f"Processing: {Path(pdf_path).name}")
            self.run_single(pdf_path)

    def run_single(self, pdf_path: str) -> None:
        """Process a single PDF file through the full pipeline."""
        pdf_name = Path(pdf_path).name
        total_pages = self.pdf_handler.get_page_count(pdf_path)

        if total_pages == 0:
            log.error(f"Could not read PDF or PDF is empty: {pdf_path}")
            return

        log.info(f"PDF '{pdf_name}': {total_pages} pages")

        # Setup output directory
        output_subdir = Path(self.config.output_dir) / Path(pdf_path).stem
        output_subdir.mkdir(parents=True, exist_ok=True)

        # Setup checkpoint
        checkpoint = CheckpointManager(pdf_path, self.config.output_dir)
        completed_pages: set[int] = set()

        if self.config.resume and checkpoint.is_valid(total_pages):
            completed_pages = checkpoint.get_completed_pages()
            log.info(f"Resuming: {len(completed_pages)}/{total_pages} pages already done")
        else:
            checkpoint.init(total_pages, "marker-pdf")

        # Setup progress
        progress = ProgressReporter(
            total_pages=total_pages,
            pdf_name=pdf_name,
            progress_callback=self._progress_cb,
            status_callback=self._status_cb,
        )

        # Collect results (load cached + process remaining)
        results: dict[int, PageResult] = {}

        for page_num in completed_pages:
            try:
                results[page_num] = checkpoint.load_page(page_num)
                progress.report_skipped(page_num)
            except Exception as e:
                log.warning(f"Failed to load checkpoint for page {page_num}: {e}")
                completed_pages.discard(page_num)

        # Process remaining pages one by one
        pages_to_process = [p for p in range(total_pages) if p not in completed_pages]

        for page_num in pages_to_process:
            if self._is_cancelled():
                log.info("Processing cancelled by user")
                return

            progress.report_page_start(page_num)

            # Process single page with marker-pdf
            result = self.engine.process_pdf_by_page(pdf_path, page_num)
            results[page_num] = result
            checkpoint.save_page(result)

            # Extract embedded images if requested
            if self.config.extract_images and not result.error:
                self._extract_page_images(pdf_path, page_num, str(output_subdir))

            if result.error:
                progress.report_error(page_num, result.error)
            else:
                progress.report_page_done(page_num, result.processing_time)

            # Free memory between pages
            gc.collect()

        # Check cancellation
        if self._is_cancelled():
            log.info("Processing cancelled by user")
            return

        progress.report_complete()

        # Generate final outputs
        ordered_results = [results.get(i) for i in range(total_pages)]
        ordered_results = [r for r in ordered_results if r is not None]

        self._write_outputs(ordered_results, pdf_path, str(output_subdir))

        # Cleanup checkpoint
        checkpoint.cleanup()
        log.info(f"Completed: {pdf_name}")

    def _extract_page_images(self, pdf_path: str, page_num: int, output_dir: str) -> None:
        """Extract embedded images from a PDF page."""
        try:
            from ..engine.image_extractor import ImageExtractor
            extractor = ImageExtractor()
            extractor.extract_embedded_images(pdf_path, page_num, output_dir)
        except Exception as e:
            log.warning(f"Image extraction failed for page {page_num}: {e}")

    def _write_outputs(
        self, results: list[PageResult], pdf_path: str, output_dir: str
    ) -> None:
        """Generate all requested output formats."""
        if not results:
            log.warning("No results to write")
            return

        pdf_stem = Path(pdf_path).stem

        for fmt in self.config.formats:
            try:
                if fmt == "txt":
                    write_txt(results, output_dir, pdf_stem)
                elif fmt == "txt_pages":
                    write_txt_per_page(results, output_dir, pdf_stem)
                elif fmt == "docx":
                    write_docx(results, output_dir, pdf_stem)
                elif fmt == "markdown":
                    write_markdown(results, output_dir, pdf_stem)
                log.info(f"Output written: {fmt}")
            except Exception as e:
                log.error(f"Failed to write {fmt} output: {e}")

    def _is_cancelled(self) -> bool:
        return self._cancel_check is not None and self._cancel_check()
