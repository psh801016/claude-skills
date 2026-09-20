"""plan.json -> Blender 3D (벽/개구부/바닥/장비/재질/조명) + 아이소·탑뷰 렌더.

2026-09-15 이력:
  v1 - drawing-to-3d-walls 스킬 기본 경로. VERTS 200 / FACES 150 '매스 덩어리'라 반려.
  v2 - 바닥 슬래브 / 문 위 인방 / 창대 / 문짝 / 유리 / 장비 / 재질 / EEVEE 추가.
  v3 - JOYCG 채널 'GPT6 Astra + 3dsmax' 영상(2026-09-15) 참고. 그쪽이 AI로 3ds Max를
       몰아 만든 씬의 레이어 체계를 받아왔다: camera / ceiling / equipment /
       fix_furniture / floor / furniture / graphics / lighting_fixtures / lights /
       props / wall / wall_finish / wall_door.
       + 완성 사진이 있으면 그 색을 plan["materials"] 로 덮어쓰는 경로(사진은 선택).

천장은 만들지 않는다 - 아이소/탑뷰에서 내부가 전부 가려진다(돌하우스 방식).

실행: blender --background --python build3d.py -- <plan.json> <출력폴더>
"""
import bpy, bmesh, math, mathutils, os, sys, json

argv = sys.argv[sys.argv.index("--") + 1:]
PLAN, OUT = argv[0], argv[1]
os.makedirs(OUT, exist_ok=True)
plan = json.load(open(PLAN, encoding="utf-8"))

MM = 0.001
LINTEL = 2.1   # 문 상부 인방 하단
SILL   = 0.9   # 창대
HEAD   = 2.4   # 창 상단

# 씬 레이어 표준(컬렉션). 비어 있어도 만들어 둬서 다음 사람이 어디에 뭘 넣을지 알게 한다.
LAYERS = ["camera", "ceiling", "ceiling_mesh", "equipment", "fix_furniture", "floor",
          "furniture", "glazing", "graphics", "lighting_fixtures", "lights", "props",
          "wall", "wall_door", "wall_finish"]

# 장비 이름 키워드 -> (레이어, 재질키). 위에서부터 먼저 걸리는 것을 쓴다.
BLOCK_RULES = [
    ("STAGE",  "fix_furniture", "stage"),
    ("LED",    "equipment",     "led"),
    ("SCREEN", "equipment",     "led"),
    ("BANNER", "graphics",      "banner"),
    ("데스크",  "furniture",     "wood"),
    ("다과",    "furniture",     "wood"),
    ("포토월",  "fix_furniture", "photo"),
    ("E/V",    "equipment",     "metal"),
]

# ── 재질·조명 프로파일 (data/profiles.json) ───────────────────────────
# 코드에 박아두면 현장 종류가 바뀔 때마다 스크립트를 고쳐야 한다. 데이터로 뺀다.
# 우선순위: plan["materials"](사진에서 뽑은 색) > meta.profile > neutral
_PROF = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "data", "profiles.json"), encoding="utf-8"))
meta = plan.get("meta", {})
MPROF = meta.get("profile", "neutral")
LPROF = meta.get("lighting", "studio_neutral")
PALETTE = {k: dict(v) for k, v in _PROF["material_profiles"]
           .get(MPROF, _PROF["material_profiles"]["neutral"]).items() if not k.startswith("_")}
LIGHT = _PROF["lighting_profiles"].get(LPROF, _PROF["lighting_profiles"]["studio_neutral"])
for k, v in (plan.get("materials") or {}).items():      # 사진에서 뽑은 색이 최우선
    PALETTE.setdefault(k, {}).update(v)


def unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    return (dx / L, dy / L), L


# ── 벽: 평면에서 자르고, 개구부 구간은 높이로 다시 채운다 ────────────────
def _pt_seg_dist(p, a, b):
    ax_, ay_ = a; bx_, by_ = b
    dx, dy = bx_ - ax_, by_ - ay_
    L2 = dx * dx + dy * dy
    tt = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - ax_) * dx + (p[1] - ay_) * dy) / L2))
    return math.hypot(p[0] - (ax_ + tt * dx), p[1] - (ay_ + tt * dy))


# 각 벽의 양끝이 '다른 벽과 만나는 코너'인지 먼저 판정한다(mm 좌표 기준).
JUNC = {}
for _w in plan["walls"]:
    ends = []
    for _p in (_w["a"], _w["b"]):
        touch = any(_o is not _w and _pt_seg_dist(_p, _o["a"], _o["b"]) < 30
                    for _o in plan["walls"])
        ends.append(touch)
    JUNC[id(_w)] = tuple(ends)

wall_boxes, leaves, glazing = [], [], []
for w in plan["walls"]:
    a_m = [w["a"][0] * MM, w["a"][1] * MM]              # mm -> m
    b_m = [w["b"][0] * MM, w["b"][1] * MM]
    (ux, uy), L = unit(a_m, b_m)
    ax, ay = a_m
    t = w.get("t", 150) * MM
    h = w.get("h", 3.0)
    ops = sorted([o for o in plan.get("openings", []) if plan["walls"][o["wall"]] is w],
                 key=lambda o: o["at"])

    def seg(s, e, z0, z1, ext0=False, ext1=False):
        # ext0/ext1 = 그 끝을 t/2 만큼 늘릴지. 벽끼리 만나는 코너만 늘린다.
        # 개구부로 잘린 문선까지 늘리면 900mm 문이 (900-t)mm 로 좁아진다.
        if e - s < 0.05 or z1 - z0 < 0.02:
            return
        wall_boxes.append((ax + ux * s, ay + uy * s, ax + ux * e, ay + uy * e,
                           t, z0, z1, ext0, ext1))

    pos = 0.0
    j0, j1 = JUNC[id(w)]                      # 이 벽의 시작/끝이 다른 벽과 만나는가
    for o in ops:
        s = (o["at"] - o["w"] / 2) * MM
        e = (o["at"] + o["w"] / 2) * MM
        seg(pos, s, 0.0, h, ext0=(pos == 0.0 and j0), ext1=False)
        ang = math.atan2(uy, ux)
        if o["kind"] == "door":
            seg(s, e, min(LINTEL, h), h)                        # 인방
            hs = e if o.get("hinge") == "b" else s
            leaves.append((ax + ux * hs, ay + uy * hs, e - s,
                           ang + (math.pi / 2 if o.get("swing") != "out" else -math.pi / 2)))
        else:
            seg(s, e, 0.0, min(SILL, h))                        # 창대
            seg(s, e, min(HEAD, h), h)                          # 창 상부
            glazing.append((ax + ux * (s + e) / 2, ay + uy * (s + e) / 2,
                            e - s, t * 0.5, ang, min(SILL, h), min(HEAD, h)))
        pos = e
    seg(pos, L, 0.0, h, ext0=(pos == 0.0 and j0), ext1=j1)

slabs = [[(p[0] * MM, p[1] * MM) for p in r["poly"]] for r in plan.get("rooms", [])]

# ── Blender ───────────────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)
cols = {}
for name in LAYERS:
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    cols[name] = c

_mats = {}


def M(key):
    if key in _mats:
        return _mats[key]
    p = PALETTE.get(key, PALETTE["props"])
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    r, g, bl = p["rgb"]
    b.inputs["Base Color"].default_value = (r, g, bl, 1)
    b.inputs["Roughness"].default_value = p.get("rough", 0.7)
    b.inputs["Metallic"].default_value = p.get("metal", 0.0)
    if p.get("emit"):
        b.inputs["Emission Color"].default_value = (r, g, bl, 1)
        b.inputs["Emission Strength"].default_value = p["emit"]
    if p.get("alpha", 1.0) < 1.0:
        b.inputs["Alpha"].default_value = p["alpha"]
        m.blend_method = 'BLEND'
    _mats[key] = m
    return m


def new_obj(name, mat_key, layer):
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    cols[layer].objects.link(ob)
    ob.data.materials.append(M(mat_key))
    return ob, bmesh.new()


def box(bm, cx, cy, hl, ht, z0, z1, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    corners = [(-hl, -ht, z0), (hl, -ht, z0), (hl, ht, z0), (-hl, ht, z0),
               (-hl, -ht, z1), (hl, -ht, z1), (hl, ht, z1), (-hl, ht, z1)]
    vs = [bm.verts.new((cx + lx * ca - ly * sa, cy + lx * sa + ly * ca, lz)) for lx, ly, lz in corners]
    for f in [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass


def finish(pair):
    ob, bm = pair
    bm.normal_update(); bm.to_mesh(ob.data); bm.free()


p = new_obj("wall", "wall", "wall")
for (x0, y0, x1, y1, t, z0, z1, e0, e1) in wall_boxes:
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 0.05:
        continue
    ux_, uy_ = dx / L, dy / L
    a0 = t / 2 if e0 else 0.0            # 코너만 채운다
    a1 = t / 2 if e1 else 0.0
    sx, sy = x0 - ux_ * a0, y0 - uy_ * a0
    ex, ey = x1 + ux_ * a1, y1 + uy_ * a1
    box(p[1], (sx + ex) / 2, (sy + ey) / 2, (L + a0 + a1) / 2, t / 2, z0, z1,
        math.atan2(dy, dx))
finish(p)

p = new_obj("floor", "floor", "floor")
for poly in slabs:
    top = [p[1].verts.new((x, y, 0.0)) for x, y in poly]
    bot = [p[1].verts.new((x, y, -0.2)) for x, y in poly]
    p[1].faces.new(top)
    p[1].faces.new(list(reversed(bot)))
    for i in range(len(poly)):
        j = (i + 1) % len(poly)
        try:
            p[1].faces.new([top[i], top[j], bot[j], bot[i]])
        except ValueError:
            pass
finish(p)

p = new_obj("wall_door", "door", "wall_door")
for (hx, hy, ow, ang) in leaves:
    box(p[1], hx + math.cos(ang) * ow / 2, hy + math.sin(ang) * ow / 2, ow / 2, 0.02, 0.0, LINTEL, ang)
finish(p)

p = new_obj("glazing", "glass", "glazing")
for (gx, gy, ow, gt, ang, z0, z1) in glazing:
    box(p[1], gx, gy, ow / 2, gt / 2, z0, z1, ang)
finish(p)

groups = {}
for b in plan.get("blocks", []):
    layer, mkey = "props", "props"
    for kw, lyr, mk in BLOCK_RULES:
        if kw in b["name"]:
            layer, mkey = lyr, mk
            break
    key = (layer, mkey)
    if key not in groups:
        groups[key] = new_obj(f"{layer}_{mkey}", mkey, layer)
    x, y, w, d = [c * MM for c in b["rect"]]
    z0 = b.get("z", 0.0)
    box(groups[key][1], x + w / 2, y + d / 2, w / 2, d / 2, z0, z0 + b.get("h", 1.0), 0.0)
for g in groups.values():
    finish(g)

# ── 정리 패스 ─────────────────────────────────────────────────────────
# 박스를 쌓아놓기만 하면 (1) 벽 코너에서 박스끼리 겹쳐 내부 면이 살아 있고
# (2) UV 가 없어 재질 작업을 못 한다. 둘 다 여기서 해결한다.
def cleanup(ob):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    # self-union(Boolean EXACT)은 쓰지 않는다 - 2026-09-15 측정에서 비매니폴드 엣지를
    # 0개 -> 582개로 늘렸다. 박스별로 닫힌 현 상태가 더 낫다.
    # remove_doubles 는 쓰지 않는다 - 맞붙은 벽 박스를 용접해 한 엣지에 면 4장이 모이는
    # T자 접합(비매니폴드)을 만든다. 2026-09-15 측정: 0개 -> 33개. 박스별로 닫힌 편이 낫다.
    bpy.ops.mesh.normals_make_consistent(inside=False)
    try:
        bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.002)
    except Exception as e:
        print("UV 전개 실패:", ob.name, e)
    bpy.ops.object.mode_set(mode='OBJECT')
    ob.select_set(False)


for _o in [o for o in bpy.data.objects if o.type == 'MESH' and o.data.polygons]:
    cleanup(_o)

# ── 조명·카메라 ────────────────────────────────────────────────────────
xs = [c for b in wall_boxes for c in (b[0], b[2])]
ys = [c for b in wall_boxes for c in (b[1], b[3])]
mnx, mxx, mny, mxy = min(xs), max(xs), min(ys), max(ys)
cx, cy = (mnx + mxx) / 2, (mny + mxy) / 2
W, D = mxx - mnx, mxy - mny

world = bpy.data.worlds.new("W"); bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = tuple(LIGHT["world_rgb"]) + (1,)
world.node_tree.nodes["Background"].inputs[1].default_value = LIGHT["world_strength"]

ld = bpy.data.lights.new("sun", "SUN")
ld.energy = LIGHT["sun_energy"]; ld.angle = math.radians(LIGHT["sun_angle_deg"])
ld.color = tuple(LIGHT["sun_rgb"])
sun = bpy.data.objects.new("sun", ld); cols["lights"].objects.link(sun)
sun.rotation_euler = tuple(math.radians(a) for a in LIGHT["sun_rot_deg"])

fd = bpy.data.lights.new("fill", "AREA")
fd.energy = LIGHT["fill_energy"]; fd.size = max(W, D); fd.color = tuple(LIGHT["fill_rgb"])
fill = bpy.data.objects.new("fill", fd); cols["lights"].objects.link(fill)
fill.location = (cx, cy, LIGHT["fill_z"])

cd = bpy.data.cameras.new("cam"); cd.type = 'ORTHO'
cam = bpy.data.objects.new("cam", cd); cols["camera"].objects.link(cam)
bpy.context.scene.camera = cam

sc = bpy.context.scene
for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'):
    try:
        sc.render.engine = eng
        break
    except TypeError:
        continue
sc.render.resolution_x, sc.render.resolution_y = 2560, 1440
try:
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Base Contrast'
except TypeError:
    sc.view_settings.view_transform = 'Filmic'
sc.view_settings.exposure = LIGHT["exposure"]

for name, (az, el) in {"iso": (-55, 40), "top": (-90, 89.5)}.items():
    r = max(W, D) * 2.2
    a, e = math.radians(az), math.radians(el)
    cam.location = (cx + r * math.cos(e) * math.cos(a), cy + r * math.cos(e) * math.sin(a), r * math.sin(e))
    cam.rotation_euler = (mathutils.Vector((cx, cy, 1.5)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    inv = cam.matrix_world.inverted()       # ortho_scale 은 가로에만 걸린다 - 16:9 세로 잘림 방지
    us, vs = [], []
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        for c in o.bound_box:
            q = inv @ (o.matrix_world @ mathutils.Vector(c))
            us.append(q.x); vs.append(q.y)
    cd.ortho_scale = max(max(us) - min(us),
                         (max(vs) - min(vs)) * sc.render.resolution_x / sc.render.resolution_y) * 1.08
    sc.render.filepath = os.path.join(OUT, f"render_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", name)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "model.blend"))

# ── 교환 포맷 내보내기 ────────────────────────────────────────────────
# 3ds Max·SketchUp은 .blend 를 못 읽는다. 실무는 여기서 받아 쓰므로 FBX/OBJ 가 본 산출물이다.
# 축: Blender(Z-up) = 3ds Max(Z-up) 이라 변환 없이 forward=Y / up=Z 로 내보낸다.
# 오브젝트 이름이 곧 레이어다(wall / floor / wall_door / glazing / equipment_led ...) —
# FBX 에는 컬렉션 개념이 없어 이름으로 넘어간다. Max 에서 이름별로 선택·정리하면 된다.
exported = []
try:
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(OUT, "model.fbx"),
        use_selection=False, object_types={'MESH'},
        apply_unit_scale=True, global_scale=1.0,
        apply_scale_options='FBX_SCALE_NONE',
        axis_forward='Y', axis_up='Z',
        use_mesh_modifiers=True, mesh_smooth_type='FACE',
        bake_space_transform=False, path_mode='COPY')
    exported.append("model.fbx")
except Exception as e:
    print("FBX 내보내기 실패:", e)
try:
    bpy.ops.wm.obj_export(
        filepath=os.path.join(OUT, "model.obj"),
        export_selected_objects=False, export_materials=True,
        forward_axis='Y', up_axis='Z', global_scale=1.0)
    exported.append("model.obj")
except Exception as e:
    print("OBJ 내보내기 실패:", e)
print("EXPORTED", ",".join(exported) if exported else "none")

used = [c.name for c in bpy.data.collections if c.objects]

# 등급은 '무엇이 실제로 들어갔는지'로 판정한다. 숨기면 받는 사람이 시공도면으로 오해한다.
if slabs and (leaves or glazing) and plan.get("blocks"):
    TIER = "T2"
elif slabs and (leaves or glazing):
    TIER = "T1"
else:
    TIER = "T0"
proof = {
    "tier": TIER,
    "tier_meaning": _PROF["quality_tiers"][TIER],
    "material_profile": MPROF, "lighting_profile": LPROF,
    "photo_colors_applied": bool(plan.get("materials")),
    "engine": sc.render.engine,
    "size_m": [round(W, 2), round(D, 2)],
    "counts": {"wall_segments": len(wall_boxes), "slabs": len(slabs), "doors": len(leaves),
               "glazing": len(glazing), "blocks": len(plan.get("blocks", [])),
               "meshes": len([o for o in bpy.data.objects if o.type == 'MESH'])},
    "layers_used": used,
    "uncertain": meta.get("uncertain", []),
    "scale_ref": meta.get("scale_ref", ""),
    "renders": ["render_iso.png", "render_top.png"],
    "exchange_files": exported,
    "unit": "meter (Blender scene). 3ds Max System Unit 이 mm 면 임포트 시 1 unit = 1000mm 로 맞춘다.",
    "object_names_are_layers": True,
}
json.dump(proof, open(os.path.join(OUT, "proof-log.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
tv = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')
tf = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH')
print(f"TIER {TIER} PROFILE {MPROF}/{LPROF}")
print(f"ENGINE {sc.render.engine} LAYERS {len(LAYERS)} USED {len(used)}: {','.join(used)}")
print(f"MESHES {len([o for o in bpy.data.objects if o.type=='MESH'])} VERTS {tv} FACES {tf} "
      f"WALLBOX {len(wall_boxes)} SLAB {len(slabs)} DOOR {len(leaves)} GLASS {len(glazing)} "
      f"BLOCK {len(plan.get('blocks', []))} PHOTO {'yes' if plan.get('materials') else 'no'} "
      f"SIZE {W:.1f}x{D:.1f}m DONE")
print(f"CHECK 3dsmax 임포트 후 건물 전체가 {W:.1f} x {D:.1f} m 로 들어왔는지 대조하라 "
      f"(Max System Unit 이 mm 면 {W*1000:.0f} x {D*1000:.0f} mm).")
