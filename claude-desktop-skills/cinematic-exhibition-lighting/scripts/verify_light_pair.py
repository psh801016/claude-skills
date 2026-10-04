"""Verify saved lighting-pair pixels against retained layers, never success flags.

Needs Pillow and NumPy. Read-only; physical lighting and graphic residue still
require visual review. Mask support is declared from the selected lighting plan.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


def verify(manifest_path):
    manifest_path = Path(manifest_path).resolve()
    d = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    canvas = d['canvas']
    if (not isinstance(canvas, list) or len(canvas) != 2
            or any(type(v) is not int or v <= 0 for v in canvas)):
        raise ValueError('invalid canvas')
    mode = d['mode']
    if mode not in ('add', 'screen'):
        raise ValueError('mode must be add or screen')

    def path(name):
        if not isinstance(name, str) or not name:
            raise ValueError('invalid asset path')
        return (manifest_path.parent / name).resolve()

    def digest(name):
        return hashlib.sha256(path(name).read_bytes()).hexdigest()

    def pixels(name, mask=False):
        with Image.open(path(name)) as im:
            if list(im.size) != canvas:
                raise ValueError('dimensions: ' + name)
            if mask:
                a = np.asarray(im.convert('L'))
                if not np.all((a == 0) | (a == 255)):
                    raise ValueError('mask must be binary: ' + name)
                return a == 255
            if np.any(np.asarray(im.convert('RGBA'))[:, :, 3] != 255):
                raise ValueError('non-opaque RGB asset: ' + name)
            return np.asarray(im.convert('RGB')).astype(np.int32)

    def blend(b, p):
        return np.minimum(255, b + p) if mode == 'add' else b + (255 - b) * p // 255

    base_name, composite_name, plate_name = d['base'], d['composite'], d['plate']
    outputs = {path(composite_name), path(plate_name)}
    if len(outputs) != 2:
        raise ValueError('composite and plate must be separate files')
    layers = d['source_layers']
    if not isinstance(layers, list) or not layers:
        raise ValueError('retained source layers required')
    effects = d['required_effects']
    if not isinstance(effects, list) or not effects:
        raise ValueError('required effect support masks required')
    sources = [base_name] + layers + [d['unlit_mask']] + [e['mask'] for e in effects]
    for name in sources:
        if path(name) in outputs:
            raise ValueError('output reused as source: ' + name)
        if digest(name) != d['sha256'][name]:
            raise ValueError('source hash mismatch: ' + name)
    base, composite, plate = [pixels(n) for n in (base_name, composite_name, plate_name)]
    unlit = pixels(d['unlit_mask'], mask=True)
    if np.any(plate[unlit] != 0):
        raise ValueError('unlit pixels contain light or residue')
    retained = np.zeros_like(base)
    for name in layers:
        retained = blend(retained, pixels(name))
    layer_error = int(np.max(np.abs(retained - plate)))
    if layer_error > 1:
        raise ValueError('retained layer mismatch: max RGB error=' + str(layer_error))
    counts = {}
    for effect in effects:
        support = pixels(effect['mask'], mask=True)
        if not np.any(support) or np.any(support & unlit):
            raise ValueError('empty or conflicting effect support: ' + effect['name'])
        minimum = effect.get('min_value', 1)
        if type(minimum) is not int or not 1 <= minimum <= 255:
            raise ValueError('effect min_value must be an integer from 1 to 255')
        missing = int(np.count_nonzero(support & (np.max(plate, axis=2) < minimum)))
        if missing:
            raise ValueError('missing effect: ' + effect['name'] + '; pixels=' + str(missing))
        counts[effect['name']] = int(np.count_nonzero(support))
    composite_error = int(np.max(np.abs(blend(base, plate) - composite)))
    if composite_error > 1:
        raise ValueError('composite mismatch: max RGB error=' + str(composite_error))
    return {
        'status': 'NUMERIC_PASS', 'canvas': canvas, 'mode': mode,
        'retained_layer_max_rgb_error': layer_error,
        'composite_max_rgb_error': composite_error, 'required_effect_pixels': counts,
        'sha256': {n: digest(n) for n in sources + [composite_name, plate_name]},
        'visual_review': 'NOT_ASSESSED: check graphic/geometry residue, beam paths and continuity',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.manifest)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'FAIL', 'reason': str(exc)}, ensure_ascii=True))
        return 1
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
