#!/usr/bin/env python3
"""Convert the visible 2500 mm Octanorm height to a person sprite height."""
import argparse, json
p=argparse.ArgumentParser(); p.add_argument('--octa-px',type=float,required=True); p.add_argument('--octa-mm',type=float,default=2500); p.add_argument('--adult-mm',type=float,default=1700); a=p.parse_args()
if a.octa_px<=0 or a.octa_mm<=0 or a.adult_mm<=0: raise SystemExit('All dimensions must be positive.')
print(json.dumps({'octa_px':a.octa_px,'octa_mm':a.octa_mm,'adult_mm':a.adult_mm,'adult_px':round(a.octa_px*a.adult_mm/a.octa_mm,2),'ratio':round(a.adult_mm/a.octa_mm,4)},indent=2))
