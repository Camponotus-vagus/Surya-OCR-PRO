"""Structured logging configuration."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO

    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers: list[logging.Handler] = []

    # Console handler
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(level)
    console.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    handlers.append(console)

    # File handler (optional)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
        handlers.append(file_handler)

    # Configure root logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    for h in root.handlers[:]:
        root.removeHandler(h)
    for h in handlers:
        root.addHandler(h)

    # Silence noisy libraries
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
