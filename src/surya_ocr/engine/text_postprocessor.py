"""Post-processing of OCR output text."""

from __future__ import annotations

import re
import logging

log = logging.getLogger(__name__)


def clean_ocr_text(raw_text: str) -> str:
    """Clean raw OCR output for plain text usage.

    marker-pdf output is already clean markdown, so this mostly handles
    whitespace normalization and minor cleanup.
    """
    text = raw_text

    # Remove markdown formatting for plain text output
    # Headers: ## Title -> Title
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Bold/italic markers
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)

    # Horizontal rules
    text = re.sub(r"^---+\s*$", "", text, flags=re.MULTILINE)

    # Image references
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

    # Normalize multiple blank lines to at most 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip trailing whitespace per line
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    return text.strip()


def clean_for_markdown(raw_text: str) -> str:
    """Clean raw OCR output while preserving markdown formatting.

    marker-pdf already outputs clean markdown, so this is minimal cleanup.
    """
    text = raw_text

    # Normalize multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip trailing whitespace per line
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    return text.strip()


def extract_grounding_regions(raw_text: str) -> list[dict]:
    """Extract image region coordinates from grounding tags.

    marker-pdf doesn't use grounding tags, so this returns an empty list.
    Kept for API compatibility.
    """
    return []
