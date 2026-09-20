"""빌드된 .blend 에서 문·창 개구부의 실제 유효폭을 재서 plan.json 설계치와 대조한다.

배경(2026-09-15): 모든 벽 조각을 양끝에서 t/2 씩 늘리고 있어서, 개구부로 잘린 문선(jamb)까지
늘어나 900mm 문이 실제로는 (900 - 벽두께)mm 로 좁아져 있었다. 렌더로는 절대 안 보이는 결함이라
'그럴듯한 틀린 모델'이 그대로 납품될 뻔했다. 이 검사가 그걸 잡는다.

측정 방법 주의: 벽과 **평행한** 방향으로 레이를 쏘면 판정이 불안정하다(같은 날 이 실수로
멀쩡한 개구부를 NG 로 오판했다). 반드시 **벽에 수직으로** 쏴서 벽 재료가 있는지 본다.

실행: blender --background --python check_openings.py -- <model.blend> <plan.json>
종료코드 1 = 설계치와 어긋난 개구부가 있다.
"""
import bpy, json, sys, mathutils

args = sys.argv[sys.argv.index("--") + 1:]
BLEND, PLAN = args[0], args[1]
TOL_MM = 60          # 측정 스텝(5mm)과 모델링 반올림을 고려한 허용오차
STEP = 0.005

bpy.ops.wm.open_mainfile(filepath=BLEND)
plan = json.load(open(PLAN, encoding="utf-8"))
wall = bpy.data.objects.get("wall")
if wall is None:
    print("wall 오브젝트가 없습니다"); sys.exit(1)
dg = bpy.context.evaluated_depsgraph_get()
MM = 0.001


def has_wall(p, n, t):
    """점 p 에서 벽 수직방향 n 으로 짧게 쏴서 벽 재료가 있는지."""
    origin = mathutils.Vector((p.x - n.x * t, p.y - n.y * t, p.z))
    ok, loc, _, _ = wall.ray_cast(origin, mathutils.Vector((n.x, n.y, 0)),
                                  distance=2 * t, depsgraph=dg)
    return ok and (loc - p).length <= t * 1.2


print("%-5s %-7s %8s %8s %6s" % ("wall", "kind", "설계mm", "실측mm", "판정"))
bad = []
for o in plan.get("openings", []):
    w = plan["walls"][o["wall"]]
    a = mathutils.Vector((w["a"][0] * MM, w["a"][1] * MM, 0))
    b = mathutils.Vector((w["b"][0] * MM, w["b"][1] * MM, 0))
    u = (b - a).normalized()
    n = mathutils.Vector((-u.y, u.x, 0))          # 벽 수직
    t = w.get("t", 150) * MM
    z = 1.0 if o["kind"] == "door" else 1.5       # 인방 아래 / 창대와 상부 사이
    c = a + u * (o["at"] * MM) + mathutils.Vector((0, 0, z))

    widths = []
    for sgn in (-1, 1):
        d = 0.0
        while d < 8.0:
            d += STEP
            if has_wall(c + u * (sgn * d), n, t):
                break
        widths.append(d)
    meas = (widths[0] + widths[1]) * 1000
    ok = abs(meas - o["w"]) <= TOL_MM
    if not ok:
        bad.append((o, meas))
    print("%-5d %-7s %8d %8.0f %6s" % (o["wall"], o["kind"], o["w"], meas,
                                       "OK" if ok else "**NG**"))

print("결과: %d/%d 통과" % (len(plan.get("openings", [])) - len(bad),
                          len(plan.get("openings", []))))
if bad:
    print("어긋난 개구부가 있습니다. 벽 연장(ext) 로직과 개구부 좌표를 확인하세요.")
sys.exit(1 if bad else 0)
