"""plan2dxf - 평면도 JSON -> DXF 베이스 도면.

배경: 2026-09-15. "GPT한테 캐드 그려달라니까 도면이 엉망" 문제.
원인은 LLM에게 기하(좌표/DXF 텍스트)를 직접 쓰게 한 것.
해법: LLM은 '읽기'만 해서 JSON을 채우고, 선은 이 결정론적 스크립트가 긋는다.

사용:
  python plan2dxf.py plan.json -o out.dxf     # 검산 후 DXF 생성
  python plan2dxf.py plan.json --check        # 검산만
단위는 mm, 원점은 좌하단.
"""
import json, math, sys, argparse
import ezdxf

LAYERS = {  # 이름: (AutoCAD 색인색, 선종류)
    "A-WALL":   (7,  "CONTINUOUS"),
    "A-WALL-C": (8,  "CENTER"),
    "A-DOOR":   (3,  "CONTINUOUS"),
    "A-WIND":   (4,  "CONTINUOUS"),
    "A-ROOM":   (2,  "CONTINUOUS"),
    "A-AREA":   (9,  "CONTINUOUS"),
    "A-EQPT":   (5,  "CONTINUOUS"),   # 스테이지/LED/데스크 등 장비·가구
    "A-MARK":   (1,  "CONTINUOUS"),   # 원도의 빨간 마킹(X배너 등)
    "A-PATH":   (1,  "DASHED"),       # 동선
}


def _vec(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    if L == 0:
        raise ValueError(f"길이 0인 벽: {a}->{b}")
    return (dx / L, dy / L), L


def shoelace(poly):
    """폴리곤 면적(mm^2). 자기교차 폴리곤은 값이 작게 나오므로 검산에서 걸린다."""
    s = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def wall_runs(wall):
    """벽 중심선을 개구부로 잘라 '실제 벽이 있는 구간' 목록으로 반환."""
    _, L = _vec(wall["a"], wall["b"])
    cuts = []
    for op in wall.get("_ops", []):
        s = op["at"] - op["w"] / 2.0
        e = op["at"] + op["w"] / 2.0
        cuts.append((max(0.0, s), min(L, e)))
    cuts.sort()
    runs, pos = [], 0.0
    for s, e in cuts:
        if s > pos:
            runs.append((pos, s))
        pos = max(pos, e)
    if pos < L:
        runs.append((pos, L))
    return runs


def validate(plan):
    """치명(errors)과 경고(warns)를 나눠 돌려준다. 치명이 있으면 DXF를 만들지 않는다."""
    errors, warns = [], []
    walls = plan.get("walls", [])
    if not walls:
        errors.append("walls 가 비어 있음")

    for i, w in enumerate(walls):
        try:
            d, L = _vec(w["a"], w["b"])
        except ValueError as e:
            errors.append(str(e))
            continue
        ang = abs(math.degrees(math.atan2(d[1], d[0]))) % 90
        if min(ang, 90 - ang) > 0.5:
            warns.append(f"W{i} 직각 아님 ({ang:.1f}도 기울어짐) - 사선벽이 맞는지 확인")
        if not 60 <= w.get("t", 0) <= 500:
            warns.append(f"W{i} 벽두께 {w.get('t')}mm - 실무 범위(60~500) 밖")
        for op in w.get("_ops", []):
            if op["at"] - op["w"] / 2 < -1 or op["at"] + op["w"] / 2 > L + 1:
                errors.append(f"W{i} 개구부({op['kind']} {op['w']}mm @{op['at']})가 벽 길이 {L:.0f}mm 를 벗어남")

    for op in plan.get("openings", []):
        if not 0 <= op["wall"] < len(walls):
            errors.append(f"개구부가 없는 벽 인덱스 {op['wall']} 를 참조")
        if op["kind"] == "door" and not 600 <= op["w"] <= 2400:
            # 2400까지는 호텔/전시장 양개문·회전문이라 정상. 그 밖이면 판독 오류로 본다.
            warns.append(f"문 폭 {op['w']}mm - 실무 범위(600~2400) 벗어남")

    # 개구부 자리에 직교벽이 서 있으면 문이 그 폭으로 안 열린다.
    # 3D 로 세우고 나서야 보이는 결함이라 여기서 잡는다(2026-09-15 아파트 예제에서 발견:
    # 벽이 3300·4200 에 있는데 그 사이에 1000mm 문을 넣어 실유효폭이 750mm 였다).
    for op in plan.get("openings", []):
        if not 0 <= op["wall"] < len(walls):
            continue
        w = walls[op["wall"]]
        try:
            (ux, uy), L = _vec(w["a"], w["b"])
        except ValueError:
            continue
        ax, ay = w["a"]
        s0, e0 = op["at"] - op["w"] / 2, op["at"] + op["w"] / 2
        for j, o in enumerate(walls):
            if o is w:
                continue
            for pt in (o["a"], o["b"]):
                # 그 끝점이 이 벽 위에 있는가, 있다면 개구부 구간 안인가
                proj = (pt[0] - ax) * ux + (pt[1] - ay) * uy
                perp = abs(-(pt[0] - ax) * uy + (pt[1] - ay) * ux)
                if perp < 30 and s0 - o.get("t", 150) / 2 < proj < e0 + o.get("t", 150) / 2:
                    errors.append(
                        f"W{op['wall']} 개구부({op['kind']} {op['w']}mm @{op['at']}) 자리에 "
                        f"W{j} 벽이 서 있음(@{proj:.0f}) - 그 폭으로 열리지 않는다")

    rooms = plan.get("rooms", [])
    total = sum(shoelace(r["poly"]) for r in rooms) / 1e6  # m^2
    ref = plan.get("meta", {}).get("exclusive_area_m2")
    if ref:
        err = abs(total - ref) / ref * 100
        msg = f"실면적 합 {total:.2f}㎡ vs 전용면적 {ref:.2f}㎡ (차이 {err:.1f}%)"
        # 벽 두께가 실 폴리곤에서 빠지므로 실측은 전용면적보다 5~12% 작은 게 정상이다.
        if err > 20:
            errors.append(msg + " - 스케일 환산(px->mm)이 틀렸을 가능성이 큼")
        elif err > 15:
            warns.append(msg + " - 스케일 재확인 권장")
    return errors, warns, total


def build(plan, path):
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4  # mm
    for name, (color, lt) in LAYERS.items():
        doc.layers.add(name, color=color, linetype=lt)
    # 한글 실명이 AutoCAD에서 깨지지 않도록 TrueType 스타일을 따로 만든다(txt.shx는 한글 불가).
    doc.styles.add("HANGUL", font="malgun.ttf")
    msp = doc.modelspace()

    for w in plan["walls"]:
        (ux, uy), _ = _vec(w["a"], w["b"])
        nx, ny = -uy, ux            # 좌측 법선
        h = w.get("t", 150) / 2.0
        ax, ay = w["a"]
        msp.add_line(w["a"], w["b"], dxfattribs={"layer": "A-WALL-C"})
        for s, e in wall_runs(w):
            p0 = (ax + ux * s, ay + uy * s)
            p1 = (ax + ux * e, ay + uy * e)
            msp.add_lwpolyline(
                [(p0[0] + nx * h, p0[1] + ny * h), (p1[0] + nx * h, p1[1] + ny * h),
                 (p1[0] - nx * h, p1[1] - ny * h), (p0[0] - nx * h, p0[1] - ny * h)],
                close=True, dxfattribs={"layer": "A-WALL"})

    for op in plan.get("openings", []):
        w = plan["walls"][op["wall"]]
        (ux, uy), _ = _vec(w["a"], w["b"])
        nx, ny = -uy, ux
        h = w.get("t", 150) / 2.0
        ax, ay = w["a"]
        s, e = op["at"] - op["w"] / 2, op["at"] + op["w"] / 2
        j0 = (ax + ux * s, ay + uy * s)
        j1 = (ax + ux * e, ay + uy * e)
        if op["kind"] == "door":
            hinge = j1 if op.get("hinge") == "b" else j0
            leaf_dir = -1 if op.get("hinge") == "b" else 1
            tip = (hinge[0] + ux * op["w"] * leaf_dir, hinge[1] + uy * op["w"] * leaf_dir)
            side = -1 if op.get("swing") == "out" else 1
            open_pt = (hinge[0] + nx * op["w"] * side, hinge[1] + ny * op["w"] * side)
            msp.add_line(hinge, open_pt, dxfattribs={"layer": "A-DOOR"})
            a0 = math.degrees(math.atan2(open_pt[1] - hinge[1], open_pt[0] - hinge[0]))
            a1 = math.degrees(math.atan2(tip[1] - hinge[1], tip[0] - hinge[0]))
            if side * leaf_dir > 0:
                a0, a1 = a1, a0
            msp.add_arc(hinge, op["w"], a0, a1, dxfattribs={"layer": "A-DOOR"})
        else:  # window: 창틀 3선
            for f in (-1, 0, 1):
                o = f * h
                msp.add_line((j0[0] + nx * o, j0[1] + ny * o),
                             (j1[0] + nx * o, j1[1] + ny * o),
                             dxfattribs={"layer": "A-WIND"})
        for j in (j0, j1):  # 문선/창선 (개구부 끝막이)
            msp.add_line((j[0] + nx * h, j[1] + ny * h), (j[0] - nx * h, j[1] - ny * h),
                         dxfattribs={"layer": "A-WALL"})

    for r in plan.get("rooms", []):
        poly = r["poly"]
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": "A-ROOM"})
        msp.add_text(r["name"], height=250, dxfattribs={"layer": "A-ROOM", "style": "HANGUL"}) \
           .set_placement((cx, cy + 180), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
        msp.add_text(f"{shoelace(poly)/1e6:.2f}m2", height=180, dxfattribs={"layer": "A-AREA", "style": "HANGUL"}) \
           .set_placement((cx, cy - 180), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

    for b in plan.get("blocks", []):
        x, y, w, h = b["rect"]
        msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                           close=True, dxfattribs={"layer": "A-EQPT"})
        msp.add_text(b["name"], height=b.get("th", 200),
                     dxfattribs={"layer": "A-EQPT", "style": "HANGUL"})            .set_placement((x + w / 2, y + h / 2), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

    DIRS = {"left": (-1, 0), "right": (1, 0), "up": (0, 1), "down": (0, -1)}
    for m in plan.get("marks", []):
        x, y = m["at"]
        r = m.get("r", 450)
        msp.add_circle((x, y), r, dxfattribs={"layer": "A-MARK"})
        dx, dy = DIRS[m.get("dir", "left")]
        msp.add_line((x - dx * r * 0.6, y - dy * r * 0.6), (x + dx * r * 0.6, y + dy * r * 0.6),
                     dxfattribs={"layer": "A-MARK"})
        for sgn in (1, -1):                       # 화살촉 두 선
            hx, hy = -dy * sgn, dx * sgn
            msp.add_line((x + dx * r * 0.6, y + dy * r * 0.6),
                         (x + dx * r * 0.2 + hx * r * 0.3, y + dy * r * 0.2 + hy * r * 0.3),
                         dxfattribs={"layer": "A-MARK"})
        msp.add_text(m["label"], height=250, dxfattribs={"layer": "A-MARK", "style": "HANGUL"})            .set_placement((x, y - r - 350), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

    for rt in plan.get("routes", []):
        msp.add_lwpolyline(rt["pts"], dxfattribs={"layer": "A-PATH"})
        msp.add_text(rt["name"], height=300, dxfattribs={"layer": "A-PATH", "style": "HANGUL"})            .set_placement(rt["pts"][0], align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

    doc.saveas(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("-o", "--out", default="out.dxf")
    ap.add_argument("--check", action="store_true", help="검산만 하고 DXF는 만들지 않음")
    a = ap.parse_args()

    plan = json.loads(open(a.plan, encoding="utf-8").read())
    for op in plan.get("openings", []):          # 개구부를 벽에 매달아 둔다
        plan["walls"][op["wall"]].setdefault("_ops", []).append(op)

    errors, warns, total = validate(plan)
    for w in warns:
        print("  [경고]", w)
    for e in errors:
        print("  [오류]", e)
    print(f"  블록 {len(plan.get('blocks', []))}개 / 마킹 {len(plan.get('marks', []))}개 / 동선 {len(plan.get('routes', []))}개")
    print(f"  벽 {len(plan['walls'])}개 / 개구부 {len(plan.get('openings', []))}개 / 실 {len(plan.get('rooms', []))}개 / 실면적합 {total:.2f}m2")
    if errors:
        print("검산 실패 - DXF를 만들지 않습니다. JSON을 고치세요.")
        return 1
    if a.check:
        print("검산 통과.")
        return 0
    build(plan, a.out)
    print(f"생성 완료: {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
