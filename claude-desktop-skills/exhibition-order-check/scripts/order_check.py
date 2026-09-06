# -*- coding: utf-8 -*-
r"""전시 발주 검산기 — 맥앤윕 그래픽 파트.

출력소에 넘기기 전에 두 가지를 본다.
  1) 발주 치수가 사내 규칙에 맞는지 (order_size / check_row)
  2) 일러 파일에 라이브 텍스트가 남았는지 (check_ai)

규칙 정본: G:\내 드라이브\AUSURA\AI-Sessions\wiki\reference\octanorm-booth-order-specs.md
정답지: test_order_check.py (실제 발주파일 3건에서 뽑은 19케이스)

사용:
    python order_check.py sizes 항목표.csv
    python order_check.py ai "<폴더 또는 .ai 경로>"
"""
import csv
import os
import sys
import re

# ── 옥타 발주표 (폭 m → (2.5m이하, 2.5m초과)) ───────────────────────────
# 0.5m 만 발주값(450)과 3D·시공값(455)이 다르다.
OCTA = {
    0.5: (450, 450),
    1.0: (950, 950),
    1.5: (1445, 1445),
    2.0: (1940, 1950),
    2.5: (2435, 2435),
    3.0: (2930, 2940),
    4.0: (3920, 3930),
    5.0: (4910, 4920),
}
OCTA_3D = {0.5: 455}          # 3D 모델링·실제 시공에서만 쓰는 값
PLUS10_MIN_W = 2.0            # 폭 2m 이상만 +10 대상
PLUS10_MIN_H = 2480           # 세로 2480 이상만 +10 대상

# 마감 → 치수 체계
BAR = ("상하단", "바미싱", "상하단바미싱")      # 옥타표 + 조건부 +10
ROUND = ("둥글게", "양면", "둥글게양면")         # 옥타표, +10 없음, 양면은 세로 2배
FIRE = ("불칼질",)                              # 실측 자유치수 + 상하좌우 100
FLEX = ("후렉스", "플렉스")                      # 실측. 한 면당 20 확장

FIRE_MARGIN = 100      # 불칼질: 한 변당 100 (상하좌우 총 200)
FLEX_MARGIN = 20       # 후렉스: 한 면당 20 (상하좌우 총 40)
PLYWOOD_MARGIN = 100   # 목공 합판: 상하좌우 100씩

# 공감 단가표 (2024-12-27 기준, 원/m²) — 주 거래처. 다른 출력소는 단가가 다르다.
GAMGAM_UNIT = {
    "간판현수막": 4000, "현수막": 4000, "줄미싱현수막": 4500,
    "밀러": 7000, "텐트천": 7000,
    "유포지": 15000, "캘지": 15000, "켈지": 15000, "그레이": 15000,
    "후렉스": 18000, "시트": 18000, "솔벤": 18000,
    "폼보드": 25000, "시공현수막": 8000,
}


def _finish_kind(finish):
    """마감 문자열 → 'bar' | 'round' | 'fire' | 'flex' | None"""
    f = (finish or "").replace(" ", "")
    if any(k in f for k in FIRE):
        return "fire"
    if any(k in f for k in FLEX):
        return "flex"
    if any(k in f for k in ROUND):
        return "round"
    if any(k in f for k in BAR):
        return "bar"
    return None


def parse_width(value):
    u"""폭 입력을 m 실수로 바꾼다.

    order_label.jsx 가 '3m' · '2m(+10)' · '0.5m' 같은 라벨로 써 주므로 그것도 받는다.
    숫자만 오면 그대로 m 로 본다.
    """
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    m = re.match(r"^\s*([0-9]*\.?[0-9]+)\s*m", s, re.I)
    if m:
        return float(m.group(1))
    return float(s)          # 실패하면 ValueError 가 그대로 올라간다


def order_size(width_m, height_mm, finish, double_sided=False):
    """발주 치수를 계산한다.

    width_m    : 옥타 폭(0.5/1/1.5/2/2.5/3/4/5). 불칼질·후렉스는 mm 실측을 넣는다.
    height_mm  : 세로 mm
    finish     : '현수막 상하단 바미싱' / '둥글게 양면' / '불칼질' / '후렉스' 등
    double_sided: 양면이면 세로 2배

    반환: (가로mm, 세로mm, 근거문자열)
    """
    kind = _finish_kind(finish)
    h = int(height_mm)

    if kind in ("fire", "flex"):
        # 옥타표를 쓰지 않는다. 실측 자유치수다.
        # ★ 입력값에 여유가 이미 포함됐는지 알 방법이 없어 자동으로 더하지 않는다.
        #   (실제 발주 '2200x4200 불칼질'이 여유 전인지 후인지 문서에 없음)
        #   더했다가 이중으로 붙으면 출력 후 못 되돌리므로, 그대로 통과시키고 알린다.
        m = FIRE_MARGIN if kind == "fire" else FLEX_MARGIN
        w = int(width_m)  # 이 경우 width_m 은 mm 실측값
        why = ("불칼질 — 옥타표 미적용. 여유 한 변 %d(총 %d) 포함됐는지 직접 확인"
               if kind == "fire" else
               "후렉스 — 옥타표 미적용. 여유 한 면 %d(총 %d) 포함됐는지 직접 확인") % (m, m * 2)
        return w, h, why

    if kind is None:
        raise ValueError("마감을 알 수 없습니다: %r (상하단/둥글게/불칼질/후렉스)" % finish)

    key = parse_width(width_m)
    if key not in OCTA:
        raise ValueError("옥타 폭이 표에 없습니다: %rm (%s)"
                         % (key, "/".join(str(k) for k in OCTA)))

    base, over = OCTA[key]
    plus10 = (kind == "bar" and key >= PLUS10_MIN_W and h >= PLUS10_MIN_H)
    w = over if plus10 else base

    if plus10:
        why = "상하단 바미싱 + 폭 %gm(≥2m) + 세로 %d(≥%d) → +10" % (key, h, PLUS10_MIN_H)
    elif kind == "round":
        why = "둥글게 양면 — 마감이 달라 +10 없음"
    elif key < PLUS10_MIN_W:
        why = "폭 %gm < 2m → +10 없음" % key
    else:
        why = "세로 %d < %d → +10 없음" % (h, PLUS10_MIN_H)

    if key == 0.5:
        why += " · 발주 450 / 3D·시공 %d" % OCTA_3D[0.5]

    return w, (h * 2 if double_sided else h), why


def check_row(row):
    """발주 표 한 줄을 검산한다. row = dict(구역,폭,세로,마감,수량[,적힌가로,적힌세로,양면])

    반환: dict(ok, 계산가로, 계산세로, 근거, 문제[list])
    """
    problems = []
    double = str(row.get("양면", "")).strip() in ("1", "Y", "y", "양면", "True")
    try:
        w, h, why = order_size(row["폭"], row["세로"], row["마감"], double)
    except ValueError as e:
        return {"ok": False, "문제": [str(e)], "근거": "", "계산가로": "", "계산세로": ""}

    for label, calc, key in (("가로", w, "적힌가로"), ("세로", h, "적힌세로")):
        written = str(row.get(key, "")).strip()
        if written and written.isdigit() and int(written) != calc:
            problems.append("%s: 적힌 %s ≠ 계산 %d" % (label, written, calc))

    return {"ok": not problems, "계산가로": w, "계산세로": h,
            "근거": why, "문제": problems}


def price_gamgam(width_mm, height_mm, qty, material):
    """공감 단가표로 예상 금액. 주 거래처가 공감일 때만 의미가 있다."""
    unit = None
    for k, v in GAMGAM_UNIT.items():
        if k in (material or ""):
            unit = v
            break
    if unit is None:
        return None
    m2 = (width_mm / 1000.0) * (height_mm / 1000.0) * int(qty)
    return int(round(m2 * unit))


# ── 일러 파일 검사 ────────────────────────────────────────────────────
def check_ai(path):
    """.ai 를 PDF 호환으로 열어 라이브 텍스트가 남았는지 본다.

    폰트가 하나라도 잡히면 글자깨기(Ctrl+Shift+O)가 안 된 것이다.
    ponytail: 아트보드 치수는 발주 치수와 무관해(작업 판) 참고로만 낸다.
              오브젝트 단위 실측이 필요해지면 Illustrator COM 을 붙인다.
    """
    import fitz  # PyMuPDF
    d = fitz.open(path)
    fonts, chars = set(), 0
    for pg in d:
        for f in pg.get_fonts():
            fonts.add(f[3])
        chars += len(pg.get_text().strip())
    r = d[0].rect
    d.close()
    return {
        "파일": os.path.basename(path),
        "아트보드": "%.1f x %.1f mm" % (r.width / 72 * 25.4, r.height / 72 * 25.4),
        "폰트": sorted(fonts),
        "글자수": chars,
        "ok": not fonts,
    }


def _cmd_sizes(csv_path):
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    bad = 0
    print("구역 | 폭 | 세로 | 마감 | 발주치수 | 판정")
    print("-" * 78)
    for r in rows:
        res = check_row(r)
        mark = "OK" if res["ok"] else "!! " + " / ".join(res["문제"])
        print("%s | %s | %s | %s | %s x %s | %s"
              % (r.get("구역", ""), r.get("폭", ""), r.get("세로", ""),
                 r.get("마감", ""), res["계산가로"], res["계산세로"], mark))
        if not res["ok"]:
            bad += 1
    print("-" * 78)
    print("총 %d건 / 문제 %d건" % (len(rows), bad))
    return 1 if bad else 0


def _cmd_ai(target):
    paths = []
    if os.path.isdir(target):
        for n in sorted(os.listdir(target)):
            if n.lower().endswith(".ai"):
                paths.append(os.path.join(target, n))
    else:
        paths = [target]
    bad = 0
    for p in paths:
        try:
            r = check_ai(p)
        except Exception as e:
            print("%-40s 읽기 실패: %s" % (os.path.basename(p)[:40], e))
            bad += 1
            continue
        if r["ok"]:
            print("%-40s OK  (아트보드 %s)" % (r["파일"][:40], r["아트보드"]))
        else:
            print("%-40s !! 라이브 텍스트 — 글자깨기 안 됨. 폰트: %s"
                  % (r["파일"][:40], ", ".join(r["폰트"][:4])))
            bad += 1
    print("-" * 78)
    print("총 %d개 / 문제 %d개" % (len(paths), bad))
    return 1 if bad else 0


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    cmd, target = argv[1], argv[2]
    if cmd == "sizes":
        return _cmd_sizes(target)
    if cmd == "ai":
        return _cmd_ai(target)
    print("알 수 없는 명령: %s (sizes | ai)" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
