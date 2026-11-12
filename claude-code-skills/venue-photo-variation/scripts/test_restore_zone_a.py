"""restore_zone_a 회귀 테스트.
사고 배경(2026-11-06 오디토리움 무대 실사화):
 1) 바닥에 밝기만 옮기고 물건 둘레 21px 를 후보로 채워 무대 바닥이 노랑/보라 얼룩 → --color-gain, --obj-margin
 2) 바닥선 아래 전체에 색비를 옮겨 객석 평균차 16 → --floor-y-end
 3) 그래픽 박스에 후보 밝기 ±20% 가 곱해져 디자인 파랑이 밝아짐(구조차 5.1) → --lock-graphics
"""
import subprocess, sys, tempfile, numpy as np
from pathlib import Path
from PIL import Image
HERE = Path(__file__).parent

def run(td, *extra):
    out = Path(td) / f"out{len(list(Path(td).glob('out*.png')))}.png"
    r = subprocess.run([sys.executable, str(HERE / "restore_zone_a.py"), "--src", f"{td}/src.png", "--cand", f"{td}/cand.png",
                        "--plate", f"{td}/plate.png", "--boxes", "100,40,220,100", "--floor-y", "110", "--size", "320x180",
                        "--out", str(out), *extra], capture_output=True, text=True, encoding="utf-8")
    assert "RESTORE_OK" in r.stdout, r.stdout + r.stderr
    return np.asarray(Image.open(out).convert("RGB")).astype(float)

def main():
    rng = np.random.default_rng(0)
    plate = (rng.integers(0, 255, (180, 320, 3))).astype(np.uint8)          # 특징점 많은 배경
    src = plate.copy(); src[40:100, 100:220] = (30, 60, 200)                  # 그래픽(LED)
    src[50:60, 120:200] = 255                                                 # 글자
    cand = src.astype(float).copy(); cand[40:100, 100:220] *= 1.25            # 후보: 그래픽 더 밝게
    cand[110:180] = cand[110:180] * (0.7, 0.8, 1.4)                           # 후보: 바닥 파란 번짐(객석 포함)
    with tempfile.TemporaryDirectory() as td:
        for n, a in [("plate", plate), ("src", src), ("cand", np.clip(cand, 0, 255).astype(np.uint8))]:
            Image.fromarray(a).save(f"{td}/{n}.png")
        r = run(td, "--color-gain", "--floor-y-end", "130", "--lock-graphics", "--obj-margin", "5")
        g = np.abs(r[45:95, 105:215] - src[45:95, 105:215]).mean()
        assert g < 1.5, f"그래픽 색이 바뀜 {g:.2f}"
        seats = np.abs(r[150:] - src[150:]).mean()
        assert seats < 1.5, f"띠 끝 아래(객석)가 바뀜 {seats:.2f}"
        band = r[112:124, :, 2].mean() - src[112:124, :, 2].mean()
        assert band > 5, f"바닥 띠에 파란 번짐이 안 옮겨짐 {band:.2f}"
        old = run(td)                                                        # 기존 동작은 그대로(그래픽 밝기 얹힘)
        assert np.abs(old[45:95, 105:215] - src[45:95, 105:215]).mean() > 3
        # 4) 2026-11-09 레이더 워크숍: --obj-mask 경로에서 후보 의자가 원본보다 밝으면 그 밝기가 바닥비에 섞여
        #    의자 밑 카펫이 하얗게 번졌고, 바닥비를 물건 빼고 재게 고친 첫 판은 물건 속 0/0 → 검은 사각형이 났다.
        obj = np.zeros((180, 320), np.uint8); obj[120:175, 20:80] = 255           # 큰 3D 물건(의자 무리)
        src2 = plate.copy(); src2[110:] = 150; src2[120:175, 20:80] = (20, 20, 90)
        cand2 = src2.copy(); cand2[120:175, 20:80] = (90, 90, 220)                # 후보 의자가 훨씬 밝다
        for n, a in [("src", src2), ("cand", cand2)]:
            Image.fromarray(a).save(f"{td}/{n}.png")
        Image.fromarray(obj).save(f"{td}/obj.png")
        out = Path(td) / "o4.png"
        r4 = subprocess.run([sys.executable, str(HERE / "restore_zone_a.py"), "--src", f"{td}/src.png", "--cand", f"{td}/cand.png",
                             "--obj-mask", f"{td}/obj.png", "--boxes", "200,10,240,30", "--floor-y", "110", "--size", "320x180",
                             "--out", str(out)], capture_output=True, text=True, encoding="utf-8")
        assert "RESTORE_OK" in r4.stdout, r4.stdout + r4.stderr
        o4 = np.asarray(Image.open(out).convert("RGB")).astype(float)
        near = o4[125:170, 85:100].mean()                                         # 물건 바로 옆 바닥
        assert near < 152, f"물건 옆 바닥이 밝아짐 {near:.1f}"
        assert o4[130:165, 30:70].min() > 5, "물건 속에 검은 픽셀(0/0)"
    print("TEST_OK test_restore_zone_a")

if __name__ == "__main__":
    main()
