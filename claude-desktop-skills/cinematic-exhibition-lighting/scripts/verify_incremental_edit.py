"""Reject an incremental raster edit that changes pixels outside its approved box."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--box", nargs=4, type=int, metavar=("X", "Y", "W", "H"), required=True)
    args = parser.parse_args()

    before = Image.open(args.before).convert("RGBA")
    after = Image.open(args.after).convert("RGBA")
    if before.size != after.size:
        print(f"FAIL dimensions: {before.size} != {after.size}")
        return 1

    x, y, w, h = args.box
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > before.width or y + h > before.height:
        print("FAIL invalid box")
        return 1

    changed_outside = 0
    for yy in range(before.height):
        for xx in range(before.width):
            if x <= xx < x + w and y <= yy < y + h:
                continue
            if before.getpixel((xx, yy)) != after.getpixel((xx, yy)):
                changed_outside += 1

    print(f"outside_changed_pixels={changed_outside}")
    return 0 if changed_outside == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
