"""Entry point for `python -m surya_ocr` and PyInstaller bundles."""

import sys

try:
    from .cli import main
except ImportError:
    from surya_ocr.cli import main

sys.exit(main())
