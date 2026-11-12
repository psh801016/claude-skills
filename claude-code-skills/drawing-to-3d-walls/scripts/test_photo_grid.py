"""test_photo_grid.py — photo_grid.py 회귀 테스트.

사고 배경(2026-11-09): 이미지 좌표를 눈대중으로 읽어 상자를 놓다 틀린 INWEPF 사례 → 무카 CAD 의
'격자 숫자로 읽기'를 들여옴. 이 테스트는 (1) 확대(crop)해도 격자 라벨이 원본 픽셀 값인지
(2) mm/px 가 치수 ÷ 픽셀거리로 맞는지 (3) 표식이 결과 그림의 올바른 위치에 찍히는지 잡는다.
실행: python test_photo_grid.py  → 마지막 줄 TEST_PHOTO_GRID_OK
"""
import json, os, subprocess, sys, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import photo_grid  # noqa: E402


def run(*args):
    r = subprocess.run([sys.executable, os.path.join(HERE, "photo_grid.py"), *args], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def main():
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "src.png")
        Image.new("RGB", (2000, 1500), (240, 240, 240)).save(src)

        # (2) mm/px: 두 점 거리 600px 가 500mm → 0.83333
        info = run(src, "--measure", "100,100", "700,100", "--mm", "500")
        assert abs(info["mm_per_px"] - 500 / 600) < 1e-4, info
        assert info["px_dist"] == 600.0

        # (1) crop 확대: 격자 간격·crop 이 원본 px 로 보고되고, 그림은 최대 6배 안
        out = os.path.join(td, "g.png")
        info = run(src, "-o", out, "--crop", "300", "300", "500", "450", "--step", "50", "--mark", "400,375,A")
        assert info["crop"] == [300, 300, 500, 450] and info["step"] == 50, info
        assert info["image_scale"] <= 6
        im = Image.open(out)
        assert im.size == (round(200 * info["image_scale"]), round(150 * info["image_scale"])), im.size

        # (3) 표식: 노란 + 가 (400,375) → 그림 좌표 ((400-300)*k, (375-300)*k) 에 있어야
        k = info["image_scale"]
        X, Y = round(100 * k), round(75 * k)
        r, g, b = im.getpixel((X + 9, Y))[:3]
        assert r > 200 and g > 180 and b < 80, (r, g, b)  # 노란색

        # 자동 간격: 2000px 폭 → 약 14칸 → 100 또는 200
        _, gi = photo_grid.grid_image(Image.open(src))
        assert gi["step"] in (100, 200), gi
    print("TEST_PHOTO_GRID_OK")


if __name__ == "__main__":
    main()
