# -*- coding: utf-8 -*-
"""reel_wipe 회귀 테스트.
사고 배경(2026-11-10): 릴스 시안이 검은 틀·슬라이드형으로 반려되어 '같은 각도 와이프 반전' 틀로 고정했다.
이 테스트는 (1) 세로 자르기가 9:16 인지 (2) 임시 폴더에서 실제 mp4 가 나오고 REEL_OK 가 찍히는지 확인한다.
운영 파일은 건드리지 않는다(모든 입출력은 임시 폴더).
"""
import os, subprocess, sys, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reel_wipe  # noqa: E402


def test_vcrop_is_9_16():
    im = Image.new("RGB", (2688, 1520))
    w, h = reel_wipe.vcrop(im, 0.9).size
    assert h == 1520 and abs(w / h - 9 / 16) < 0.01


def test_render_makes_mp4():
    tmp = tempfile.mkdtemp(prefix="reeltest_")
    assert "Drive" not in tmp and "AI-작업기록" not in tmp  # 파수꾼: 운영 폴더로 새지 않음
    clay = os.path.join(tmp, "c.png"); photo = os.path.join(tmp, "p.png"); fl = os.path.join(tmp, "f.png")
    Image.new("RGB", (640, 360), (200, 200, 200)).save(clay)
    Image.new("RGB", (640, 360), (120, 90, 60)).save(photo)
    Image.new("RGB", (300, 500), (255, 255, 255)).save(fl)
    out = os.path.join(tmp, "r.mp4")
    r = subprocess.run([sys.executable, os.path.join(HERE, "reel_wipe.py"), "--clay", clay, "--photo", photo,
                        "--flash", fl, "--out", out, "--sec", "3"], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    assert "REEL_OK" in r.stdout and os.path.getsize(out) > 10000


if __name__ == "__main__":
    test_vcrop_is_9_16(); test_render_makes_mp4(); print("TEST_OK")
