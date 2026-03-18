"""Path resolution utilities."""

from __future__ import annotations

from pathlib import Path


def resolve_model_path(model_path: str) -> Path:
    """Resolve model directory path, checking common locations."""
    p = Path(model_path)
    if p.exists() and (p / "config.json").exists():
        return p.resolve()

    # Check relative to the package directory
    pkg_dir = Path(__file__).resolve().parent.parent.parent.parent
    candidate = pkg_dir / "models"
    if candidate.exists() and (candidate / "config.json").exists():
        return candidate

    # Check relative to CWD
    cwd_candidate = Path.cwd() / "models"
    if cwd_candidate.exists() and (cwd_candidate / "config.json").exists():
        return cwd_candidate

    # Return original path (will fail at validation time)
    return p.resolve()


def ensure_output_dir(output_dir: str, pdf_name: str) -> Path:
    """Create and return the output subdirectory for a given PDF."""
    name = Path(pdf_name).stem
    out = Path(output_dir) / name
    out.mkdir(parents=True, exist_ok=True)
    return out
