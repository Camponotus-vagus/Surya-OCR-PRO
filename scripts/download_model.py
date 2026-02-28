#!/usr/bin/env python3
"""Download the DeepSeek-OCR model from HuggingFace Hub."""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Download DeepSeek-OCR model")
    parser.add_argument(
        "--output", "-o", default="./models",
        help="Directory to save the model (default: ./models)",
    )
    args = parser.parse_args()

    try:
        from huggingface_hub import snapshot_download

        print(f"Downloading DeepSeek-OCR model to {args.output}...")
        print("This will download approximately 6.2 GB of model weights.")
        print()

        snapshot_download(
            repo_id="deepseek-ai/DeepSeek-OCR",
            local_dir=args.output,
        )

        print(f"\nModel downloaded successfully to {args.output}")
        return 0

    except ImportError:
        print("Error: huggingface_hub not installed. Run: pip install huggingface_hub")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
