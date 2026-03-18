"""Model loading utilities for Surya/marker-pdf OCR engine.

This module provides helper functions for loading and unloading
the marker-pdf model pipeline.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def create_marker_models() -> dict:
    """Create and return the marker-pdf model dictionary.

    This loads all Surya sub-models (layout detection, text detection,
    text recognition) into memory.

    Returns:
        Dictionary of loaded models for use with PdfConverter.
    """
    from marker.models import create_model_dict

    log.info("Loading Surya OCR models...")
    model_dict = create_model_dict()
    log.info("All OCR models loaded successfully")

    return model_dict


def unload_models(model_dict: dict | None) -> None:
    """Free model memory."""
    import gc

    if model_dict is not None:
        model_dict.clear()

    gc.collect()

    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass

    log.info("Models unloaded")
