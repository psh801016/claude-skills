#!/usr/bin/env python3
"""Composite a pre-cut RGBA layer only inside an allowed mask while preserving source alpha exactly."""
import argparse
from pathlib import Path
from PIL import Image, ImageChops

p=argparse.ArgumentParser(); p.add_argument('--source',required=True); p.add_argument('--layer',required=True); p.add_argument('--mask',required=True); p.add_argument('--output',required=True); a=p.parse_args()
src=Image.open(a.source).convert('RGBA'); layer=Image.open(a.layer).convert('RGBA'); mask=Image.open(a.mask).convert('L')
if layer.size!=src.size or mask.size!=src.size: raise SystemExit('source, layer, and mask must have identical canvas sizes')
allowed=mask.point(lambda x: 255 if x else 0)
layer_alpha=layer.getchannel('A')
forbidden=ImageChops.multiply(layer_alpha, ImageChops.invert(allowed))
if forbidden.getbbox(): raise SystemExit('Layer has non-transparent pixels outside allowed mask.')
out=Image.alpha_composite(src, layer)
# Source alpha is contractual; RGB may only be added on opaque source floor pixels.
out.putalpha(src.getchannel('A'))
Path(a.output).parent.mkdir(parents=True,exist_ok=True); out.save(a.output)
print(a.output)
