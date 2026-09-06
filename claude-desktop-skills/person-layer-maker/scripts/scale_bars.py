#!/usr/bin/env python3
"""붉은 스케일 막대를 에이전트가 먼저 계산해서 그려 주는 도구.

배경 (2026-09-01): 인물 합성에서 스케일이 반복해서 틀렸다. ASURA님이 붉은 세로 막대를
직접 그려 주시는 방식으로 고쳤는데, 매번 손으로 그리는 게 번거로워 역할을 뒤집었다.
이제 에이전트가 화면 안의 치수 아는 요소(옥타 폴 2480 등)로 스케일 필드를 계산해
막대를 그려 보여주고, ASURA님은 맞다/틀리다만 판정한다.

원리: 평지에서 발 접지점 y와 화면상 키는 직선 관계다.
    h(y) = k * (y - y_h)          # y는 화면 위->아래 증가, y_h = 수평선
같은 실제 높이의 수직 기준물 2개를 주면 상단끼리 이은 선과 하단끼리 이은 선이
수평선에서 만난다. 그 교점으로 y_h 를 얻고, 기준물 하나로 k 를 얻는다.

사용:
  python scale_bars.py --image booth.png --out bars.png \
      --ref 320,180,320,900 --ref 1450,430,1450,780 --ref-mm 2480 \
      --person-mm 1700 --feet 500,880 --feet 1100,820 --feet 1700,770

  --ref  x_top,y_top,x_bot,y_bot   같은 실제 높이인 수직 기준물 (2개 필요)
  --feet x,y                       막대를 찍을 발 접지점 (여러 개)
  --horizon Y                      수평선을 이미 알면 --ref 1개만으로도 가능

출력: 투명 배경 위 붉은 막대만 있는 PNG + 계산값을 stdout 으로.
"""
import argparse
import sys

from PIL import Image, ImageDraw

RED = (255, 0, 0, 255)


def solve_field(refs, ref_mm, person_mm, horizon=None):
    """기준물들로 (y_h, k) 를 푼다. k 는 person_mm 높이 기준."""
    if horizon is None:
        if len(refs) < 2:
            raise ValueError("기준물이 1개면 수평선을 확정할 수 없습니다. "
                             "--ref 를 하나 더 주거나 --horizon 을 주세요.")
        (ax_t, ay_t, ax_b, ay_b), (bx_t, by_t, bx_b, by_b) = refs[0], refs[1]
        horizon = _line_intersection_y((ax_t, ay_t), (bx_t, by_t),
                                       (ax_b, ay_b), (bx_b, by_b))

    x_t, y_t, x_b, y_b = refs[0]
    if y_b <= horizon:
        raise ValueError("기준물 발끝이 수평선 위에 있습니다. 좌표나 수평선을 확인하세요.")
    person_px_at_ref = (y_b - y_t) * (person_mm / ref_mm)
    k = person_px_at_ref / (y_b - horizon)
    return horizon, k


def _line_intersection_y(p1, p2, p3, p4):
    """두 직선(p1p2, p3p4)의 교점 y. 평행이면 정사영으로 보고 예외."""
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = p1, p2, p3, p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:
        raise ValueError("상단선과 하단선이 평행합니다 — 아이소/정사영 렌더로 보입니다. "
                         "이 경우 깊이에 따른 축소가 없으니 막대 길이를 모두 같게 씁니다.")
    d1 = x1 * y2 - y1 * x2
    d2 = x3 * y4 - y3 * x4
    return (d1 * (y3 - y4) - (y1 - y2) * d2) / den


def bar_height(y_foot, horizon, k):
    return k * (y_foot - horizon)


def draw_bars(size, feet, horizon, k, width):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    out = []
    for (fx, fy) in feet:
        h = bar_height(fy, horizon, k)
        top = fy - h
        d.rectangle([fx - width / 2, top, fx + width / 2, fy], fill=RED)
        out.append((fx, fy, h))
    return img, out


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--image", help="캔버스 크기를 읽어올 원본. --canvas 로 대체 가능")
    p.add_argument("--canvas", help="WxH (예: 2560x1440). 원본 파일이 없을 때 사용")
    p.add_argument("--out", required=True)
    p.add_argument("--ref", action="append", default=[],
                   help="x_top,y_top,x_bot,y_bot")
    p.add_argument("--ref-mm", type=float, default=2480.0)
    p.add_argument("--person-mm", type=float, default=1700.0)
    p.add_argument("--feet", action="append", default=[], help="x,y")
    p.add_argument("--horizon", type=float, default=None)
    p.add_argument("--bar-width", type=float, default=None)
    a = p.parse_args(argv)

    refs = [tuple(float(v) for v in r.split(",")) for r in a.ref]
    feet = [tuple(float(v) for v in f.split(",")) for f in a.feet]
    if not refs:
        p.error("--ref 가 최소 1개 필요합니다.")
    if not feet:
        p.error("--feet 가 최소 1개 필요합니다.")

    if a.canvas:
        w, h = a.canvas.lower().split("x")
        size = (int(w), int(h))
    elif a.image:
        with Image.open(a.image) as im:
            size = im.size
    else:
        p.error("--image 또는 --canvas 중 하나가 필요합니다.")
    horizon, k = solve_field(refs, a.ref_mm, a.person_mm, a.horizon)
    width = a.bar_width or max(4.0, size[0] * 0.008)
    img, rows = draw_bars(size, feet, horizon, k, width)
    img.save(a.out)

    print(f"canvas       : {size[0]}x{size[1]}")
    print(f"y_horizon    : {horizon:.1f}")
    print(f"k            : {k:.5f}   # h = k * (y_foot - y_horizon)")
    for fx, fy, h in rows:
        print(f"bar @({fx:.0f},{fy:.0f})  height={h:.1f}px  top_y={fy - h:.1f}")
    print(f"saved        : {a.out}")
    return 0


def demo():
    """자체검사: 합성 좌표로 수평선·막대 높이가 되짚어지는지 확인한다."""
    # 수평선 y=200, k=0.5 인 가상 장면. 실제 2480mm 기준물 2개를 만든다.
    y_h, k_true, ref_mm, person_mm = 200.0, 0.5, 2480.0, 1700.0
    k_ref = k_true * ref_mm / person_mm          # 기준물 높이용 계수
    refs = []
    for x, y_b in ((300.0, 900.0), (1400.0, 500.0)):
        h = k_ref * (y_b - y_h)
        refs.append((x, y_b - h, x, y_b))

    horizon, k = solve_field(refs, ref_mm, person_mm)
    assert abs(horizon - y_h) < 1e-6, horizon
    assert abs(k - k_true) < 1e-9, k

    # 임의 깊이에서 사람 높이가 직선식과 일치
    assert abs(bar_height(700.0, horizon, k) - k_true * (700.0 - y_h)) < 1e-9

    # 수평선을 직접 주면 기준물 1개로도 풀린다
    h2, k2 = solve_field(refs[:1], ref_mm, person_mm, horizon=y_h)
    assert abs(k2 - k_true) < 1e-9, k2

    # 기준물 1개 + 수평선 없음 -> 거부
    try:
        solve_field(refs[:1], ref_mm, person_mm)
    except ValueError:
        pass
    else:
        raise AssertionError("기준물 1개인데 통과했습니다")

    # 정사영(상단선·하단선 평행) -> 거부
    ortho = [(100.0, 100.0, 100.0, 500.0), (800.0, 100.0, 800.0, 500.0)]
    try:
        solve_field(ortho, ref_mm, person_mm)
    except ValueError:
        pass
    else:
        raise AssertionError("정사영인데 통과했습니다")

    print("demo OK")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        sys.exit(main())
