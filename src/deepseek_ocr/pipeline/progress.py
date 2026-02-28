"""Progress reporting for OCR pipeline."""

from __future__ import annotations

import time
import logging
from typing import Callable, Optional

log = logging.getLogger(__name__)


class ProgressReporter:
    """Reports progress for a multi-page OCR job.

    Supports both callback-based reporting (for GUI) and console-based
    reporting (for CLI).
    """

    def __init__(
        self,
        total_pages: int,
        pdf_name: str = "",
        progress_callback: Optional[Callable[[int, int, float], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None,
    ):
        """
        Args:
            total_pages: Total number of pages in the PDF.
            pdf_name: Name of the PDF being processed.
            progress_callback: Called with (current_page, total_pages, eta_seconds).
            status_callback: Called with status message string.
        """
        self.total_pages = total_pages
        self.pdf_name = pdf_name
        self._progress_cb = progress_callback
        self._status_cb = status_callback
        self._start_time = time.time()
        self._page_times: list[float] = []

    def report_page_start(self, page_num: int) -> None:
        """Report that processing of a page has started."""
        msg = f"Processing page {page_num + 1}/{self.total_pages}"
        if self.pdf_name:
            msg += f" of {self.pdf_name}"
        log.info(msg)
        if self._status_cb:
            self._status_cb(msg)

    def report_page_done(self, page_num: int, processing_time: float) -> None:
        """Report that a page has been processed."""
        self._page_times.append(processing_time)

        completed = page_num + 1
        elapsed = time.time() - self._start_time
        avg_time = elapsed / completed if completed > 0 else 0
        remaining = self.total_pages - completed
        eta = avg_time * remaining

        pct = int(completed / self.total_pages * 100)
        eta_str = self._format_time(eta)
        elapsed_str = self._format_time(elapsed)

        msg = f"Page {completed}/{self.total_pages} done ({pct}%) | Elapsed: {elapsed_str} | ETA: {eta_str}"
        log.info(msg)

        if self._progress_cb:
            self._progress_cb(completed, self.total_pages, eta)
        if self._status_cb:
            self._status_cb(msg)

    def report_skipped(self, page_num: int) -> None:
        """Report that a page was skipped (already in checkpoint)."""
        log.info(f"Page {page_num + 1}/{self.total_pages} skipped (cached)")

    def report_complete(self) -> None:
        """Report that all pages are done."""
        elapsed = time.time() - self._start_time
        elapsed_str = self._format_time(elapsed)
        avg = sum(self._page_times) / len(self._page_times) if self._page_times else 0

        msg = f"OCR complete: {self.total_pages} pages in {elapsed_str} (avg {avg:.1f}s/page)"
        log.info(msg)
        if self._status_cb:
            self._status_cb(msg)
        if self._progress_cb:
            self._progress_cb(self.total_pages, self.total_pages, 0)

    def report_error(self, page_num: int, error: str) -> None:
        """Report an error on a specific page."""
        msg = f"Error on page {page_num + 1}: {error}"
        log.error(msg)
        if self._status_cb:
            self._status_cb(msg)

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds as 'Xm Ys'."""
        minutes, secs = divmod(int(seconds), 60)
        if minutes > 0:
            return f"{minutes}m {secs}s"
        return f"{secs}s"
