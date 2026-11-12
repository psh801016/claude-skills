"""hall_underlay 회귀 테스트.
사고 배경(2026-11-11 Kofpi): 홀 천장이 부스와 다른 소실점 → "전체 공간 소실점이 기본 아니냐".
지킬 것: 밑그림의 천장·바닥 격자선이 주어진 두 소실점으로 모인다(RANSAC 2% 안).
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, cv2
from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import check_vp as c


def main():
    W, H = 2560, 1440
    rgba = np.zeros((H, W, 4), np.uint8); rgba[600:1250, 1150:1400] = (200, 200, 200, 255)   # 부스 자리
    with tempfile.TemporaryDirectory() as td:
        Image.fromarray(rgba).save(f"{td}/b.png")
        r = subprocess.run([sys.executable, str(HERE / "hall_underlay.py"), "--render", f"{td}/b.png", "--vp-left=-1359,719",
                            "--vp-right=3653,718", "--f", "2502", "--anchor", "1272,1258", "--hc", "1.44", "--out", f"{td}/u.png"],
                           capture_output=True, text=True, encoding="utf-8")
        assert "HALL_UNDERLAY_OK" in r.stdout, r.stdout + r.stderr
        g = cv2.cvtColor(np.asarray(Image.open(f"{td}/u.png").convert("RGB")), cv2.COLOR_RGB2GRAY)
    ex = np.zeros((H, W), bool); ex[:, 1100:1450] = True
    vps = sorted([v for v, n in c.ransac_vps(c.seg_lines(g, ex, 150, 90)) if n >= 3], key=lambda v: v[0])
    assert len(vps) == 2, vps
    assert abs(vps[0][0] + 1359) / 1359 < 0.02 and abs(vps[1][0] - 3653) / 3653 < 0.02, vps
    print("TEST_OK test_hall_underlay")


if __name__ == "__main__":
    main()
