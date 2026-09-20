"""plan.json -> drawing-to-3d-walls 스킬의 walls.json (경로 D 입력).

스킬의 extract_dwg.py 를 거치지 않는다. DXF에서 선을 다시 주워담는 대신
원천 데이터(중심선 + 두께 + 높이 + 개구부)를 그대로 넘긴다 — 추출 손실이 없다.

두 가지를 챙긴다:
  1) 개구부를 실제로 잘라낸다. 스킬 기본 경로는 벽을 통짜로 세워 문이 막힌다.
  2) 세그먼트별 높이 s[5] 를 채운다. build_walls.py 는 지원하는데
     어느 추출기도 안 쓰고 문서에도 없어서, 층고가 다른 건물이 전부 단일 높이로 나온다.

실행: python to_walls_json.py venue-crystal.json <작업폴더>
"""
import json, sys, os
from plan2dxf import wall_runs, _vec

src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)

plan = json.loads(open(src, encoding="utf-8").read())
for op in plan.get("openings", []):
    plan["walls"][op["wall"]].setdefault("_ops", []).append(op)

segs = []
for w in plan["walls"]:
    (ux, uy), _ = _vec(w["a"], w["b"])
    ax, ay = w["a"]
    t = w.get("t", 150) / 1000.0          # mm -> m
    h = w.get("h", 3.0)
    for s, e in wall_runs(w):             # 개구부로 잘린 '실제 벽이 있는 구간'만
        if e - s < 100:                   # 100mm 미만 조각은 버린다
            continue
        segs.append([round((ax + ux * s) / 1000, 3), round((ay + uy * s) / 1000, 3),
                     round((ax + ux * e) / 1000, 3), round((ay + uy * e) / 1000, 3),
                     round(t, 3), h])

out = os.path.join(outdir, "walls.json")
json.dump({"unit": "m", "wall_height": 3.0, "count": len(segs), "segments": segs},
          open(out, "w", encoding="utf-8"))

xs = [c for s in segs for c in (s[0], s[2])]
ys = [c for s in segs for c in (s[1], s[3])]
print(f"{len(segs)}세그먼트 / 건물 {max(xs)-min(xs):.1f} x {max(ys)-min(ys):.1f} m "
      f"/ 층고 {sorted(set(s[5] for s in segs))} -> {out}")
