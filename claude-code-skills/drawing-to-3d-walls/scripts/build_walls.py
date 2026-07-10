# build_walls.py — walls.json(세그먼트) 또는 rooms.json(방+제원)을 3D 벽체로 압출·렌더.
# 실행: blender --background --python build_walls.py -- <workdir> <input.json>
# 포맷 자동감지: {"rooms":[...]} → 경로 C(방별 높이) / {"segments":[...]} → 경로 A·B(단일 높이)
import bpy, bmesh, math, mathutils, os, sys, json

argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
WORKDIR = argv[0] if len(argv) > 0 else os.getcwd()
INPUT = argv[1] if len(argv) > 1 else os.path.join(WORKDIR, "walls.json")
data = json.load(open(INPUT, encoding="utf-8"))

# ── 세그먼트 수집: 각 벽 = (x0,y0,x1,y1, 두께t, 높이h) ──
segs = []
def add_wall(x0, y0, x1, y1, t, h):
    segs.append((x0, y0, x1, y1, t, h))

def rot_pt(px, py, cx, cy, deg):
    a = math.radians(deg); ca = math.cos(a); sa = math.sin(a)
    dx = px - cx; dy = py - cy
    return (cx + dx*ca - dy*sa, cy + dx*sa + dy*ca)

def room(r):
    cx, cy = r["cx"], r["cy"]; w, d = r["w"], r["d"]; h = r["h"]
    t = r.get("t", 0.3); rot = r.get("rot", 0.0); door = r.get("door")
    hw, hd = w/2, d/2
    edges = {
        'S': ((-hw, -hd), ( hw, -hd)), 'E': (( hw, -hd), ( hw,  hd)),
        'N': (( hw,  hd), (-hw,  hd)), 'W': ((-hw,  hd), (-hw, -hd)),
    }
    for side, (p0, p1) in edges.items():
        ax, ay = p0[0]+cx, p0[1]+cy; bx, by = p1[0]+cx, p1[1]+cy
        ax, ay = rot_pt(ax, ay, cx, cy, rot); bx, by = rot_pt(bx, by, cx, cy, rot)
        if door and door[0] == side:
            dw = door[1]; L = math.hypot(bx-ax, by-ay); ux = (bx-ax)/L; uy = (by-ay)/L
            g0 = (L-dw)/2; g1 = (L+dw)/2
            add_wall(ax, ay, ax+ux*g0, ay+uy*g0, t, h)
            add_wall(ax+ux*g1, ay+uy*g1, bx, by, t, h)
        else:
            add_wall(ax, ay, bx, by, t, h)

if "rooms" in data or "polylines" in data:
    for r in data.get("rooms", []): room(r)
    for pl in data.get("polylines", []):
        pts = pl["pts"]; t = pl.get("t", 0.2); h = pl.get("h", 3.0)
        for a, b in zip(pts[:-1], pts[1:]): add_wall(a[0], a[1], b[0], b[1], t, h)
else:
    h_default = data.get("wall_height", 3.0)
    for s in data["segments"]:
        t = s[4] if len(s) > 4 else 0.15
        h = s[5] if len(s) > 5 else h_default   # 세그먼트별 높이(선택) — 방마다 다른 층고
        add_wall(s[0], s[1], s[2], s[3], t, h)

# ── Blender 빌드 ──
bpy.ops.wm.read_factory_settings(use_empty=True)
mesh = bpy.data.meshes.new("Walls"); obj = bpy.data.objects.new("Walls", mesh)
bpy.context.collection.objects.link(obj)
bm = bmesh.new()
for (x0, y0, x1, y1, t, h) in segs:
    dx, dy = x1-x0, y1-y0; length = math.hypot(dx, dy)
    if length < 0.05: continue
    cx, cy = (x0+x1)/2, (y0+y1)/2; ang = math.atan2(dy, dx)
    hl = length/2 + t/2; ht = t/2; ca = math.cos(ang); sa = math.sin(ang)  # +t/2: 코너 메우기
    corners = [(-hl,-ht,0),(hl,-ht,0),(hl,ht,0),(-hl,ht,0),
               (-hl,-ht,h),(hl,-ht,h),(hl,ht,h),(-hl,ht,h)]
    vs = [bm.verts.new((cx+lx*ca-ly*sa, cy+lx*sa+ly*ca, lz)) for lx,ly,lz in corners]
    for f in [(0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
        try: bm.faces.new([vs[i] for i in f])
        except: pass
bm.normal_update(); bm.to_mesh(mesh); bm.free()

# 바닥 플레이트
xs = [v for s in segs for v in (s[0], s[2])]; ys = [v for s in segs for v in (s[1], s[3])]
minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
cx, cy = (minx+maxx)/2, (miny+maxy)/2; w, d = maxx-minx, maxy-miny
bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, cy, -0.02))
fl = bpy.context.active_object; fl.scale = (w*1.2, d*1.2, 1)

# 카메라(아이소) + 태양광
cd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cd)
bpy.context.collection.objects.link(cam)
dist = max(w, d)
cam.location = (cx + w*0.55, cy - d*1.05, dist*0.95)
dirv = mathutils.Vector((cx, cy, 0)) - cam.location
cam.rotation_euler = dirv.to_track_quat('-Z', 'Y').to_euler(); cd.lens = 40
bpy.context.scene.camera = cam
ld = bpy.data.lights.new("Sun", "SUN"); ld.energy = 4
sun = bpy.data.objects.new("Sun", ld); bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(48), math.radians(18), math.radians(35))

# 렌더(Workbench) + 저장
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'
sc.display.shading.show_shadows = True; sc.display.shading.show_cavity = True
sc.render.resolution_x = 1800; sc.render.resolution_y = 1200
sc.render.filepath = os.path.join(WORKDIR, "render.png")
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(WORKDIR, "model.blend"))
print("SEGMENTS", len(segs), "VERTS", len(mesh.vertices), "FACES", len(mesh.polygons),
      "SIZE %.1fx%.1fm" % (w, d), "DONE")
