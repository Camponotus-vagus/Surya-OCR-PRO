"""Entry point for `python -m deepseek_ocr` and PyInstaller bundles."""

import sys

try:
    from .cli import main
except ImportError:
    from deepseek_ocr.cli import main

sys.exit(main())
