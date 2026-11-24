#!/usr/bin/env python3
"""Hapus latar belakang gambar hasil Flow menjadi PNG transparan menggunakan rembg."""

import argparse
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove background from Flow image using rembg.")
    parser.add_argument("--input", required=True, help="Path to raw input image")
    parser.add_argument("--output", required=True, help="Path to transparent PNG output")
    parser.add_argument("--alpha-matting", action="store_true", help="Enable alpha matting for cleaner edges")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        return 1

    try:
        from rembg import remove
    except ImportError:
        print(
            "ERROR: Paket 'rembg' belum terpasang. Jalankan: pip install rembg pillow onnxruntime",
            file=sys.stderr,
        )
        return 2

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    with open(args.input, "rb") as inp:
        raw_bytes = inp.read()

    out_bytes = remove(raw_bytes, alpha_matting=args.alpha_matting)

    with open(args.output, "wb") as out:
        out.write(out_bytes)

    print(f"OK: Saved transparent PNG -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
