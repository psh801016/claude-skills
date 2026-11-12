"""check_verticals 회귀 테스트.
사고 배경(2026-11-11): 건축사진가 레퍼런스(@hanskim_studio)는 세로선 0°. AI 실사화가 수직을 모으면 렌더 티.
지킬 것: 곧은 세로선 그림 → VERT_OK, 3° 기운 세로선 그림 → VERT_FAIL.
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, cv2
from PIL import Image

HERE = Path(__file__).parent


def draw(tilt_deg, path):
    im = np.full((900, 1600, 3), 40, np.uint8)
    for x in range(200, 1500, 120):
        dx = int(np.tan(np.radians(tilt_deg)) * 600)
        cv2.line(im, (x, 150), (x + dx, 750), (230, 230, 230), 3)
    Image.fromarray(im).save(path)


def run(p):
    r = subprocess.run([sys.executable, str(HERE / "check_verticals.py"), "--img", p], capture_output=True, text=True, encoding="utf-8")
    return r.stdout


def main():
    with tempfile.TemporaryDirectory() as td:
        draw(0, f"{td}/ok.png"); draw(3, f"{td}/bad.png")
        a, b = run(f"{td}/ok.png"), run(f"{td}/bad.png")
    assert a.startswith("VERT_OK"), a
    assert b.startswith("VERT_FAIL"), b
    print("TEST_OK test_check_verticals")


if __name__ == "__main__":
    main()
