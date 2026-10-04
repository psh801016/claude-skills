"""2026-09-30: LED protection erased foreground haze; a hardcoded PASS hid it.

Use temporary images only; never rewrite the selected composite or operational assets.
"""
import hashlib
import json
from pathlib import Path
import tempfile
import subprocess
import sys

import numpy as np
from PIL import Image

from verify_light_pair import verify


def self_check():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        shape = (8, 12, 3)
        base = np.full(shape, 60, dtype=np.uint8)
        layer = np.zeros(shape, dtype=np.uint8)
        layer[2:6, 4:8] = [50, 60, 70]
        required = np.zeros(shape[:2], dtype=np.uint8)
        required[2:6, 4:8] = 255
        unlit = np.zeros_like(required)
        unlit[0] = 255

        def save(name, a):
            Image.fromarray(a).save(root / name)

        save('base.png', base)
        save('layer.png', layer)
        save('plate.png', layer)
        save('required.png', required)
        save('unlit.png', unlit)
        missing = np.zeros_like(required)
        missing[1, 1] = 255
        save('missing.png', missing)
        manifest = {
            'canvas': [12, 8], 'mode': 'add', 'base': 'base.png',
            'composite': 'final.png', 'plate': 'plate.png',
            'source_layers': ['layer.png'],
            'sha256': {n: hashlib.sha256((root / n).read_bytes()).hexdigest()
                       for n in ['base.png', 'layer.png', 'unlit.png', 'required.png', 'missing.png']},
            'required_effects': [{'name': 'LED foreground haze', 'mask': 'required.png'}],
            'unlit_mask': 'unlit.png',
        }

        def run():
            (root / 'pair.json').write_text(json.dumps(manifest), encoding='utf-8')
            return verify(root / 'pair.json')

        def reject(fragment):
            try:
                run()
            except ValueError as exc:
                assert fragment in str(exc), str(exc)
            else:
                raise AssertionError('Accepted invalid pair: ' + fragment)

        save('final.png', (base.astype(int) + layer).astype(np.uint8))
        assert run()['status'] == 'NUMERIC_PASS'
        cli = [sys.executable, str(Path(__file__).with_name('verify_light_pair.py')),
               str(root/'pair.json')]
        result = subprocess.run(cli, capture_output=True, text=True)
        assert result.returncode == 0 and json.loads(result.stdout)['status'] == 'NUMERIC_PASS'
        for mode in ['add', 'screen']:
            manifest['mode'] = mode
            b, p = base.astype(int), layer.astype(int)
            final = b + p if mode == 'add' else b + (255 - b) * p // 255
            save('final.png', final.astype(np.uint8))
            assert run()['status'] == 'NUMERIC_PASS'
            save('final.png', base)  # False success flag must not override real pixels.
            manifest['overlay_exact'] = True
            reject('composite mismatch')
            result = subprocess.run(cli, capture_output=True, text=True)
            assert result.returncode == 1 and json.loads(result.stdout)['status'] == 'FAIL'
            save('final.png', final.astype(np.uint8))

        manifest['mode'] = 'add'
        save('final.png', (base.astype(int) + layer).astype(np.uint8))
        save('plate.png', np.zeros(shape, dtype=np.uint8))
        reject('retained layer mismatch')
        save('plate.png', layer)
        manifest['required_effects'][0]['mask'] = 'missing.png'
        reject('missing effect')
        manifest['required_effects'][0]['mask'] = 'required.png'
        save('plate.png', np.ones(shape, dtype=np.uint8) * 20)
        reject('unlit pixels')
        save('plate.png', layer[:, :-1])
        reject('dimensions')
        save('plate.png', layer)
        manifest['sha256']['layer.png'] = '0' * 64
        reject('source hash')
        manifest['sha256']['layer.png'] = hashlib.sha256((root / 'layer.png').read_bytes()).hexdigest()
        manifest['required_effects'][0]['min_value'] = 80
        reject('missing effect')
        manifest['required_effects'][0]['min_value'] = 1
        save('required.png', np.zeros_like(required))
        reject('source hash')
        save('required.png', required)
        incremental = Path(__file__).with_name('verify_incremental_edit.py')
        save('incremental-before.png', base)
        edited = base.copy()
        edited[3, 5] = 90
        save('incremental-after.png', edited)
        command = [sys.executable, str(incremental), str(root/'incremental-before.png'),
                   str(root/'incremental-after.png'), '--box', '4', '2', '4', '4']
        assert subprocess.run(command, capture_output=True).returncode == 0
        edited[0, 0] = 90
        save('incremental-after.png', edited)
        assert subprocess.run(command, capture_output=True).returncode == 1
        manifest['source_layers'] = ['plate.png']
        reject('output reused as source')
        print('PASS: saved RGB pixels, Add/Screen, missing/faint haze, unlit residue, dimensions, hashes, incremental lock; isolated temporary files')


if __name__ == '__main__':
    self_check()
