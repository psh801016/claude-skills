"""발주 치수 판정 — 시공·마감으로 체계를 가른 뒤 디자인 치수(실측 mm)를 발주 치수로 바꾼다.

정본: AUSURA wiki/reference/octanorm-booth-order-specs.md
  옥타(현수막 상하단 바미싱 / 둥글게 양면) → 옥타 발주표 (폭 m → mm, +10 은 폭 2m↑·세로 2480↑·바미싱 셋 다 맞을 때만)
  목공(현수막 불칼질)                      → 실측 + 상하좌우 100 (가로·세로 각 +200)
  후렉스                                   → 실측 + 한 면 20 (가로·세로 각 +40)
  켈지·패트지·폼보드·명패·X배너·족자봉·기타 → 정사이즈
실행:  python sizes.py 목공 9760 2440        → 9960 x 2640 / 현수막 불칼질
       python sizes.py 옥타 3 2480 바미싱    → 2940 x 2480 / 현수막 상하단 바미싱
"""
import sys

OCTA = {0.5: 450, 1: 950, 1.5: 1445, 2: 1940, 2.5: 2435, 3: 2930, 4: 3920, 5: 4910}
PLUS10 = {2, 3, 4, 5}


def octa(width_m, height, finish="바미싱"):
    """옥타 폭(m)·세로(mm)·마감 → (가로, 세로, 마감 표기)."""
    w = OCTA[float(width_m)]
    if finish.startswith("바미싱") and float(width_m) in PLUS10 and height >= 2480:
        w += 10
    label = "현수막 상하단 바미싱" if finish.startswith("바미싱") else "현수막 둥글게 양면"
    return w, int(height), label


def order_size(method, w, h, finish=None):
    """method: 목공 | 목공<한 변 여유mm> | 목공슬로프 | 옥타 | 후렉스 | 정사이즈(켈지·패트지·폼보드·명패·족자봉·기타). w,h = 디자인(실측) mm (옥타는 w=m).
    목공 불칼질 사내 기본 = 사방 100. 요청서에 여유가 적혀 오면 그 값 (예: "상하좌우 20" = 각 변 20cm → 목공200).
    슬로프가 있으면 위아래만 200씩 (ASURA님 2026-10-23)."""
    m = method.strip()
    if m == "목공슬로프":
        return int(w) + 200, int(h) + 400, "현수막 불칼질 (슬로프)"
    if m.startswith("목공"):
        e = int(m[2:] or 100)
        return int(w) + 2 * e, int(h) + 2 * e, "현수막 불칼질"
    if m == "옥타":
        return octa(w, h, finish or "바미싱")
    if m == "후렉스":
        return int(w) + 40, int(h) + 40, "후렉스 (사방 20 확장)"
    return int(w), int(h), finish or m


def test():
    # 2026-10-23 충남 청년정책 대토론회: 04 현장설치물\백월.ai 가 996x264·752x264 (= 3D 976x244·732x244 +100씩) 로 목공 불칼질 규칙 확인
    assert order_size("목공", 9760, 2440) == (9960, 2640, "현수막 불칼질")
    assert order_size("목공", 7320, 2440) == (7520, 2640, "현수막 불칼질")
    # 2026-10-23 충남: 요청서 "상하좌우 20씩" = 각 변 20cm(200mm). 20mm(9800x2480)·100(9960x2640) 둘 다 반려됐다
    assert order_size("목공200", 9760, 2440) == (10160, 2840, "현수막 불칼질")
    assert order_size("목공200", 500, 2440) == (900, 2840, "현수막 불칼질")
    assert order_size("목공슬로프", 7320, 2440) == (7520, 2840, "현수막 불칼질 (슬로프)")
    # 옥타 발주표 역산 19건 중 대표 (octanorm-booth-order-specs §2)
    assert octa(3, 2480) == (2940, 2480, "현수막 상하단 바미싱")
    assert octa(3, 2480, "둥글게") == (2930, 2480, "현수막 둥글게 양면")
    assert octa(2, 2480) == (1950, 2480, "현수막 상하단 바미싱")
    assert octa(3, 750) == (2930, 750, "현수막 상하단 바미싱")
    assert octa(1, 2480) == (950, 2480, "현수막 상하단 바미싱")
    assert octa(0.5, 3230) == (450, 3230, "현수막 상하단 바미싱")
    assert order_size("후렉스", 2000, 1500) == (2040, 1540, "후렉스 (사방 20 확장)")
    assert order_size("켈지", 1150, 1150) == (1150, 1150, "켈지")
    print("OK sizes")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "test":
        test()
    else:
        w, h, lab = order_size(a[0], float(a[1]), float(a[2]), a[3] if len(a) > 3 else None)
        print(f"{w} x {h} / {lab}")
