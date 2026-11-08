"""place_people 회귀 테스트.
사고 배경(2026-11-06 성과보고회 포토존): 생성 모델이 포즈 쌍을 판 오른쪽에 크게 세웠고("가운데가 아니잖아 / 막대 아직도 커"),
뒤에 선 사람은 접지 그림자가 없었다. 지킬 것:
 ① --target-feet / --target-height 로 무리의 발 중심·키가 정확히 그 값이 된다(±3px)
 ② 박스 밖 픽셀은 원본(base) 그대로
 ③ --keep 이면 자리·크기 불변, 사람마다(덩어리마다) 발밑이 어두워진다
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).parent
W, H = 800, 500


def run(td, *args):
    r = subprocess.run([sys.executable, str(HERE / "place_people.py"), "--base", f"{td}/base.png", "--cand", f"{td}/cand.png",
                        "--mask", f"{td}/mask.png", *args], capture_output=True, text=True, encoding="utf-8")
    assert "PLACE_OK" in r.stdout, r.stdout + r.stderr
    return np.asarray(Image.open(args[args.index("--out") + 1]).convert("RGB")).astype(int)


def main():
    base = np.full((H, W, 3), 200, np.uint8)
    cand = base.copy(); mask = np.zeros((H, W), np.uint8)
    # 사람 A(500..540, 150..400), 사람 B(620..650, 250..420) — B 는 뒤가 아니라 다른 깊이
    cand[150:400, 500:540] = (30, 30, 60); mask[150:400, 500:540] = 255
    cand[400:410, 470:570] = 120  # A 발밑 그림자(생성본)
    cand[250:420, 620:650] = (40, 40, 40); mask[250:420, 620:650] = 255
    cand[420:428, 600:670] = 120  # B 발밑 그림자
    with tempfile.TemporaryDirectory() as td:
        for n, a in (("base", base), ("cand", cand), ("mask", mask)):
            Image.fromarray(a).save(f"{td}/{n}.png")
        # ① 무리 A 만 옮기고 줄이기
        out = run(td, "--box", "480,100,560,420", "--target-feet", "300,450", "--target-height", "200", "--out", f"{td}/o1.png")
        dark = (out.sum(2) < 300)
        ys, xs = np.where(dark)
        assert abs(ys.max() - 450) <= 3 and abs((ys.max() - ys.min()) - 200) <= 4, (ys.min(), ys.max())
        assert abs(xs.mean() - 300) <= 3, xs.mean()
        # ② 박스 밖(사람 B 자리)은 원본 그대로
        assert np.abs(out[250:420, 620:650] - 200).max() == 0
        # ③ keep: 두 사람 모두 그 자리, 둘 다 발밑 그림자
        out2 = run(td, "--box", "0,0,800,500", "--keep", "--out", f"{td}/o2.png")
        assert out2[300, 520].sum() < 300 and out2[300, 635].sum() < 300
        assert out2[404, 520].mean() < 195, out2[404, 520]   # A 발밑
        assert out2[423, 635].mean() < 195, out2[423, 635]   # B 발밑(옛 코드는 무리 발 하나만 → B 그림자 없음)
        # ④ 2026-11-06 "사진 찍는 사람 다리 그림자 이상해": 생성본 바닥 전체가 35% 어두우면 그 차이는 옮기지 않는다.
        #    옛 코드는 발 주변 타원이 통째로 어두워져(≈150) 얼룩이 됐다. 밑창 바로 아래 접지선은 진하게 남아야 한다.
        dark = (cand.astype(float) * 0.65).astype(np.uint8); dark[mask > 0] = cand[mask > 0]
        dark[400:403, 505:535] = 40                                                    # A 밑창 접지선
        Image.fromarray(dark).save(f"{td}/cand.png")
        out3 = run(td, "--box", "480,100,560,420", "--keep", "--out", f"{td}/o3.png")
        assert out3[401, 520].mean() < 150, out3[401, 520]            # 접지선 살아 있음
        for y, x in ((415, 520), (405, 462), (390, 485), (420, 555)):  # 생성본 원래 그림자(400..410, 470..570) 밖
            assert out3[y, x].mean() > 190, ((y, x), out3[y, x])     # 주변 바닥은 원본 밝기(얼룩 없음)
        # ⑤ 2026-11-06 "반사가 신발만 되냐고 끊어져 보이잖아": --reflect 면 다리까지 뒤집힌 반사가 밑창 아래로 이어지고
        #    멀어질수록 옅어진다. 옵션이 없으면 반사 없음(카펫·무광 바닥).
        Image.fromarray(cand).save(f"{td}/cand.png")
        o4 = run(td, "--box", "480,100,560,420", "--keep", "--reflect", "0.3", "--out", f"{td}/o4.png")
        near, far, end = o4[430, 520].mean(), o4[470, 520].mean(), o4[495, 520].mean()
        assert near < 185 and near < far < 199, (near, far)                 # 신발 아래로 이어지고 옅어짐
        assert o4[470, 520, 2] > o4[470, 520, 0], o4[470, 520]               # 사람 색(남색)이 비친다
        assert abs(end - 200) < 2, end                                       # 키×0.35 넘으면 끝
        assert abs(out2[430, 520].mean() - 200) < 2, out2[430, 520]      # 옵션 없으면 반사 없음
    print("TEST_OK test_place_people")


if __name__ == "__main__":
    main()
