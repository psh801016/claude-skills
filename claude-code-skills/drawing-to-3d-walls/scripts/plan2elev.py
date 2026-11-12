#!/usr/bin/env python
"""plan2elev.py — plan.json 의 벽을 펼친 입면(전개도) 바탕 + 실 면적표를 DXF 로 만든다.

배경(2026-11-09): 휴플로우 스튜디오 무료 리습 HUEFLOW_ELEV2(HF2 입면 왁구)·HF_AREA(HFA 면적표)를 분석해
우리 plan.json 위에 다시 구현. HF2 는 외곽 폴리라인 변마다 '길이×천장고' 사각형을 옆으로 이어 그리고
벽 폭·천장고·총폭 치수와 꺾임 ▽ 마커를 넣는다(개구부 없음). 우리는 plan.json 에 개구부가 있으므로
문(바닥~2100)·창(창대 900~2100)을 같이 뚫는다. HFA 는 닫힌 폴리라인마다 "㎡ / PY" 글자와 합계표를 넣는다.
1 PY = 3.305785 ㎡ · 글자 높이 = 가장 좁은 실 폭/15 (최소 50mm) — 리습 관행 그대로.

사용:
  python plan2elev.py plan.json -o elev.dxf                    # 모든 벽을 번호순으로 펼침 + 실 면적표
  python plan2elev.py plan.json -o elev.dxf --walls 3,4,5,6    # 한 실을 이루는 벽을 돌아가는 순서로
  python plan2elev.py plan.json -o elev.dxf --h 2.7 --no-area  # 층고 강제(m), 면적표 생략
단위 mm. 레이어 A-ELEV(벽 외곽)·A-ELEV-OPEN(개구부)·A-ELEV-DIM(치수)·A-ELEV-MRK(꺾임 ▽)·A-AREA-TXT·A-AREA-TBL.
마지막 줄에 JSON 요약(벽 수·총폭·실 면적)을 찍는다.
"""
import argparse, json, math, sys
import ezdxf

PY_M2 = 3.305785          # 1평
DOOR_H, SILL, HEAD = 2100, 900, 2100   # 개구부 높이 기본(mm) — plan.json 에 h/sill/head 가 있으면 그 값
GAP = 300                 # 벽 사이 띄움(mm) — 0 이면 HF2 처럼 붙여 그림


def poly_area(p):
    return abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2


def ensure_layers(doc):
    for name, color in (("A-ELEV", 2), ("A-ELEV-OPEN", 4), ("A-ELEV-DIM", 1), ("A-ELEV-MRK", 1), ("A-AREA-TXT", 7), ("A-AREA-TBL", 7)):
        if name not in doc.layers:
            doc.layers.add(name, color=color)


def rect(msp, x0, y0, x1, y1, layer):
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        msp.add_line(a, b, dxfattribs={"layer": layer})


def tri_down(msp, cx, ty, size, layer):
    hw = size / 2
    msp.add_solid([(cx - hw, ty + size), (cx + hw, ty + size), (cx, ty), (cx, ty)], dxfattribs={"layer": layer})


def dim_h(msp, x0, x1, y, yt, layer):
    d = msp.add_linear_dim(base=(0, yt), p1=(x0, y), p2=(x1, y), dxfattribs={"layer": layer}); d.render()


def dim_v(msp, x, y0, y1, xt, layer):
    d = msp.add_linear_dim(base=(xt, 0), p1=(x, y0), p2=(x, y1), angle=90, dxfattribs={"layer": layer}); d.render()


def mtext(msp, text, pt, h, layer, attach=5):
    m = msp.add_mtext(text, dxfattribs={"layer": layer, "char_height": h, "attachment_point": attach})
    m.set_location(pt)
    return m


def elevation(msp, plan, wall_ids, h_force=None, at=(0, 0)):
    walls, openings = plan["walls"], plan.get("openings", [])
    x, basey = at
    x0 = x
    summary = []
    for n, wi in enumerate(wall_ids):
        w = walls[wi]
        L = math.dist(w["a"], w["b"])
        H = (h_force or w.get("h") or plan.get("meta", {}).get("h") or 2.6) * 1000
        rect(msp, x, basey, x + L, basey + H, "A-ELEV")
        for op in (o for o in openings if o["wall"] == wi):
            ox0, ox1 = x + op["at"], x + op["at"] + op["w"]
            if op.get("kind") == "door":
                oy0, oy1 = basey, basey + op.get("h", DOOR_H)
            else:
                oy0, oy1 = basey + op.get("sill", SILL), basey + op.get("head", HEAD)
            rect(msp, ox0, oy0, ox1, oy1, "A-ELEV-OPEN")
            dim_h(msp, ox0, ox1, basey, basey - 600, "A-ELEV-DIM")
        dim_h(msp, x, x + L, basey + H, basey + H + 800, "A-ELEV-DIM")
        if n == 0:
            dim_v(msp, x, basey, basey + H, x - 800, "A-ELEV-DIM")
            tri_down(msp, x, basey + H, H * 0.045, "A-ELEV-MRK")
        tri_down(msp, x + L, basey + H, H * 0.045, "A-ELEV-MRK")
        mtext(msp, f"W{wi}", (x + L / 2, basey + H / 2), max(50, H / 20), "A-ELEV", 5)
        summary.append({"wall": wi, "w": round(L), "h": round(H)})
        x += L + GAP
    total = x - GAP - x0
    if len(wall_ids) > 1:
        Hmax = max(s["h"] for s in summary)
        dim_h(msp, x0, x0 + total, basey + Hmax, basey + Hmax + 1100, "A-ELEV-DIM")
    return summary, total


def area_table(msp, rooms, table_at):
    valid = [r for r in rooms if len(r.get("poly", [])) >= 3]
    if not valid:
        return []
    min_w = min(max(p[0] for p in r["poly"]) - min(p[0] for p in r["poly"]) for r in valid)
    th = max(50, min_w / 15)
    rows = []
    for i, r in enumerate(valid, 1):
        a_m2 = poly_area(r["poly"]) / 1e6
        rows.append((i, r.get("name", f"R{i}"), a_m2, a_m2 / PY_M2))
        xs, ys = [p[0] for p in r["poly"]], [p[1] for p in r["poly"]]
        mtext(msp, f"{a_m2:.2f}㎡ / {a_m2 / PY_M2:.2f}PY", (max(xs) - th / 2, min(ys) + th / 2), th, "A-AREA-TXT", 9)
    # 합계표: 선 + MTEXT (리습 v5.0 과 같은 이유로 TABLE 객체는 쓰지 않는다)
    tx, ty = table_at
    cw = [th * 6, th * 14, th * 8, th * 8]
    ch = th * 2.8
    nrows = len(rows) + 2
    for k in range(nrows + 1):
        msp.add_line((tx, ty - ch * k), (tx + sum(cw), ty - ch * k), dxfattribs={"layer": "A-AREA-TBL"})
    cx = tx
    for wdt in [0] + cw:
        cx += wdt
        msp.add_line((cx, ty), (cx, ty - ch * nrows), dxfattribs={"layer": "A-AREA-TBL"})
    centers = [tx + sum(cw[:j]) + cw[j] / 2 for j in range(4)]

    def row(k, cells):
        for c, t in zip(centers, cells):
            mtext(msp, t, (c, ty - ch * k - ch / 2), th * 0.9, "A-AREA-TBL", 5)
    row(0, ("NO", "실명", "AREA (㎡)", "AREA (PY)"))
    for k, (i, name, m2, py) in enumerate(rows, 1):
        row(k, (str(i), name, f"{m2:.2f}", f"{py:.2f}"))
    row(nrows - 1, ("", "TOTAL", f"{sum(r[2] for r in rows):.2f}", f"{sum(r[3] for r in rows):.2f}"))
    return [{"no": i, "name": n, "m2": round(m2, 2), "py": round(py, 2)} for i, n, m2, py in rows]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan"); ap.add_argument("-o", "--out", default="elev.dxf")
    ap.add_argument("--walls", help="펼칠 벽 번호, 돌아가는 순서로 (예 3,4,5,6). 생략 = 전부")
    ap.add_argument("--h", type=float, help="층고 강제(m)")
    ap.add_argument("--no-area", action="store_true", help="실 면적 글자·합계표 생략")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    plan = json.load(open(a.plan, encoding="utf-8"))
    ids = [int(s) for s in a.walls.split(",")] if a.walls else list(range(len(plan["walls"])))
    doc = ezdxf.new("R2010"); doc.header["$INSUNITS"] = 4; ensure_layers(doc); msp = doc.modelspace()
    # 입면은 평면 아래쪽에 놓는다 (평면 좌표와 안 겹치게)
    ys = [p for w in plan["walls"] for p in (w["a"][1], w["b"][1])]
    base = (0, min(ys) - 6000)
    summary, total = elevation(msp, plan, ids, a.h, base)
    areas = [] if a.no_area else area_table(msp, plan.get("rooms", []), (total + 3000, base[1] + 4000))
    doc.saveas(a.out)
    print(json.dumps({"out": a.out, "walls": summary, "total_w": round(total), "rooms": areas}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
