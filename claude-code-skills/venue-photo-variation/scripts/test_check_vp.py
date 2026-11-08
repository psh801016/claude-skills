"""check_vp 회귀 테스트.
사고 배경(2026-11-06 성과보고회 로비 등록데스크): rebg 배경의 천장·벽 깊이선이 부스와 다른 소실점(2360 vs 3301)으로 모였는데
눈으로 통과시켜 납품 → 사용자 "공간 각도가 지금 부스 각도랑 안 맞아 / 천장에서 공간깊이에 각을 봐".
합성 이미지로: 배경선이 물건과 같은 소실점이면 VP_OK, 다른 소실점이면 VP_FAIL 이어야 한다.
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
W, H = 1600, 900


def scene(bg_vp, obj_vp=(3000, 470)):
    im = Image.new("RGB", (W, H), (235, 235, 232)); dr = ImageDraw.Draw(im)
    for y in list(range(-900, 300, 70)) + list(range(700, 2600, 110)):   # 배경 깊이선(천장·바닥)
        dr.line([(0, y), bg_vp], fill=(90, 90, 90), width=3)
    mask = Image.new("L", (W, H), 0); dm = ImageDraw.Draw(mask)
    def ln(x, y):  # obj_vp 로 가는 직선 위의 y
        return y + (obj_vp[1] - y) * (x / obj_vp[0])
    poly = [(500, 330), (1200, ln(1200, 330) + (330 - ln(0, 330)) * 0), (1200, 0), (500, 0)]
    # 물건: 위·아래 모서리가 obj_vp 로 모이는 판
    top = lambda x: 330 + (obj_vp[1] - 330) * (x - 500) / (obj_vp[0] - 500)
    bot = lambda x: 640 + (obj_vp[1] - 640) * (x - 500) / (obj_vp[0] - 500)
    quad = [(500, 330), (1200, top(1200)), (1200, bot(1200)), (500, 640)]
    dr.polygon(quad, fill=(20, 60, 160)); dm.polygon(quad, fill=255)
    quad2 = [(560, 420), (1100, top(1100) + 90), (1100, bot(1100) - 60), (560, 580)]
    dr.polygon(quad2, fill=(30, 90, 190)); dm.polygon(quad2, fill=255)
    return im, mask


def run(td, name, bg_vp):
    im, mask = scene(bg_vp)
    im.save(f"{td}/{name}.png"); mask.save(f"{td}/{name}_m.png")
    r = subprocess.run([sys.executable, str(HERE / "check_vp.py"), "--img", f"{td}/{name}.png", "--obj-mask", f"{td}/{name}_m.png"],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout.strip()


def main():
    with tempfile.TemporaryDirectory() as td:
        rc, out = run(td, "same", (3000, 470))
        assert rc == 0 and out.startswith("VP_OK"), out
        rc, out = run(td, "off", (2100, 430))
        assert rc == 1 and out.startswith("VP_FAIL"), out
    # 2026-11-06 2차 사고: 정면선(오른쪽 소실점)과 측면선(왼쪽 소실점)을 한 무리로 최소제곱 → 3527 이 3326 으로 치우쳐
    #   배경을 틀린 카메라로 그렸다(로비 2.19°). RANSAC 은 두 소실점을 각각 2% 안으로 찾아야 한다.
    sys.path.insert(0, str(HERE)); import check_vp as c
    VR, VL = np.array([3527.0, 716.0]), np.array([-1078.0, 716.0])
    lines = []
    for y0 in (330, 360, 620, 640, 1090, 1100, 900, 950, 300, 1000, 700):
        lines.append([700, y0, 1500, y0 + (VR[1] - y0) * 800 / (VR[0] - 700)])
    for y0 in (330, 1096, 600):
        lines.append([700, y0, 780, y0 + (VL[1] - y0) * 80 / (VL[0] - 700)])
    got = sorted([v for v, n in c.ransac_vps(lines) if n >= 2], key=lambda v: v[0])
    assert len(got) == 2, got
    assert abs(got[0][0] - VL[0]) / abs(VL[0]) < 0.02 and abs(got[1][0] - VR[0]) / VR[0] < 0.02, got
    mixed = c.vanish(lines)
    assert abs(mixed[0] - VR[0]) / VR[0] > 0.02  # 섞어 맞추면 치우친다는 사실 자체도 고정
    print("TEST_OK test_check_vp")


if __name__ == "__main__":
    main()
