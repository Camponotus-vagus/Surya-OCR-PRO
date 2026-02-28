"""Checkpoint/resume system for long OCR jobs."""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
from pathlib import Path

from ..engine.ocr_engine import PageResult

log = logging.getLogger(__name__)


class CheckpointManager:
    """Manages per-page checkpoints for resumable OCR processing.

    Each processed page is saved as a JSON file. On resume, already-processed
    pages are loaded from disk and skipped.
    """

    def __init__(self, pdf_path: str, output_dir: str):
        pdf_name = Path(pdf_path).stem
        self._pdf_path = pdf_path
        self._checkpoint_dir = Path(output_dir) / pdf_name / ".checkpoint"
        self._meta_path = self._checkpoint_dir / "meta.json"
        self._pdf_hash = self._hash_file(pdf_path)

    @staticmethod
    def _hash_file(path: str) -> str:
        """Fast identity hash: SHA-256 of first 1MB + file size."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            h.update(f.read(1024 * 1024))
        h.update(str(Path(path).stat().st_size).encode())
        return h.hexdigest()[:16]

    def init(self, total_pages: int, config_summary: str) -> None:
        """Initialize checkpoint metadata for a new job."""
        self._checkpoint_dir.mkdir(parents=True, exist_ok=True)
        meta = {
            "pdf_hash": self._pdf_hash,
            "total_pages": total_pages,
            "config_summary": config_summary,
            "version": "2.0",
        }
        self._meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        log.info(f"Checkpoint initialized: {self._checkpoint_dir}")

    def is_valid(self, total_pages: int) -> bool:
        """Check if an existing checkpoint matches the current job."""
        if not self._meta_path.exists():
            return False
        try:
            meta = json.loads(self._meta_path.read_text(encoding="utf-8"))
            return (
                meta.get("pdf_hash") == self._pdf_hash
                and meta.get("total_pages") == total_pages
                and meta.get("version") == "2.0"
            )
        except (json.JSONDecodeError, KeyError):
            return False

    def get_completed_pages(self) -> set[int]:
        """Return set of page numbers already processed."""
        if not self._checkpoint_dir.exists():
            return set()
        completed = set()
        for f in self._checkpoint_dir.glob("page_*.json"):
            try:
                page_num = int(f.stem.split("_")[1])
                completed.add(page_num)
            except (IndexError, ValueError):
                continue
        return completed

    def save_page(self, result: PageResult) -> None:
        """Save a single page result to checkpoint."""
        self._checkpoint_dir.mkdir(parents=True, exist_ok=True)
        page_file = self._checkpoint_dir / f"page_{result.page_number:04d}.json"
        page_file.write_text(
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_page(self, page_num: int) -> PageResult:
        """Load a previously saved page result."""
        page_file = self._checkpoint_dir / f"page_{page_num:04d}.json"
        data = json.loads(page_file.read_text(encoding="utf-8"))
        return PageResult.from_dict(data)

    def cleanup(self) -> None:
        """Remove checkpoint directory after successful completion."""
        if self._checkpoint_dir.exists():
            shutil.rmtree(self._checkpoint_dir)
            log.info("Checkpoint cleaned up")

    @property
    def checkpoint_dir(self) -> Path:
        return self._checkpoint_dir
