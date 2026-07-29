#!/usr/bin/env python3
"""Inspect an RGBA source without modifying it."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image

p=argparse.ArgumentParser(); p.add_argument('source'); a=p.parse_args()
path=Path(a.source)
with Image.open(path) as im:
    rgba=im.convert('RGBA')
    alpha=rgba.getchannel('A')
    hist=alpha.histogram()
    result={
        'path':str(path), 'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'size':list(rgba.size), 'mode':im.mode,
        'transparent_pixels':hist[0], 'partial_alpha_pixels':sum(hist[1:255]), 'opaque_pixels':hist[255],
        'alpha_min':min(i for i,n in enumerate(hist) if n), 'alpha_max':max(i for i,n in enumerate(hist) if n)
    }
print(json.dumps(result, ensure_ascii=False, indent=2))
