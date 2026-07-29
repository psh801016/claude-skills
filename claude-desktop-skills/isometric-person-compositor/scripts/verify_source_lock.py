#!/usr/bin/env python3
"""Verify that only the allowed region changed and alpha is byte-exact."""
import argparse, json
from PIL import Image, ImageChops

p=argparse.ArgumentParser(); p.add_argument('--source',required=True); p.add_argument('--output',required=True); p.add_argument('--allowed-mask',required=True); a=p.parse_args()
src=Image.open(a.source).convert('RGBA'); out=Image.open(a.output).convert('RGBA'); mask=Image.open(a.allowed_mask).convert('L')
if src.size!=out.size or src.size!=mask.size: raise SystemExit('Canvas size mismatch')
alpha_exact=src.getchannel('A').tobytes()==out.getchannel('A').tobytes()
diff=ImageChops.difference(src.convert('RGB'),out.convert('RGB'))
outside=ImageChops.multiply(diff.convert('L'),ImageChops.invert(mask.point(lambda x:255 if x else 0)))
changed=sum(1 for v in outside.getdata() if v)
result={'ALPHA_EXACT':alpha_exact,'OUTSIDE_CHANGED_PIXELS':changed,'CANVAS_EXACT':src.size==out.size,'PASS':bool(alpha_exact and changed==0)}
print(json.dumps(result,indent=2))
raise SystemExit(0 if result['PASS'] else 1)
