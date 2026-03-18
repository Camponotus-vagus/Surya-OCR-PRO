#!/usr/bin/env python3
"""Pre-download Surya OCR models for offline use.

marker-pdf/Surya downloads models automatically on first run.
This script allows pre-downloading them for offline environments.
"""

import sys


def main():
    try:
        print("Pre-downloading Surya OCR models...")
        print("Models will be cached in the default HuggingFace cache directory.")
        print()

        from marker.models import create_model_dict

        print("Downloading and loading models...")
        model_dict = create_model_dict()
        model_dict.clear()

        print("\nModels downloaded successfully!")
        print("They are cached and will be used automatically by deepseek-ocr.")
        return 0

    except ImportError:
        print("Error: marker-pdf not installed. Run: pip install marker-pdf")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
