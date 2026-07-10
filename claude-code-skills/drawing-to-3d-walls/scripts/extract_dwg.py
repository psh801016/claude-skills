# -*- coding: utf-8 -*-
"""한국 건축 특화 DWG/DXF 레이어 자동분류·벽 추출 → walls.json (최정밀 경로 A)
실행: python extract_dwg.py <도면.dxf> <작업폴더>
  .dwg는 먼저 DXF로 변환 필요(ODA File Converter 등). pip install ezdxf.
"""
import sys, os, math, json, re
from collections import defaultdict
import ezdxf

DXF = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "."
os.makedirs(OUT, exist_ok=True)

# ===== 한국 건축 레이어 분류 사전 (키워드 한/영 + ACI 색상) =====
RX_WALL = re.compile(r'(?i)(^A[ASXZ]?-?WA|wall|^wal\b|벽|벽체|옹벽|조적|내력|비내력|drywall|^cw$|partition|^par)')
RX_COL  = re.compile(r'(?i)(^A[ASXZ]?-?CL|col(?!or)|column|기둥|pillar|^c\d)')
RX_DOOR = re.compile(r'(?i)(^A.?-?DW|door|^dr$|문|출입|gate)')
RX_WIN  = re.compile(r'(?i)(win(?!d_)|window|창|창호|sash|glaz|winf|^gl$)')
RX_EXCL = re.compile(r'(?i)(dim|치수|^7?dim|grid|axis|통심|주열|축|center|^cen$|level|레벨|elev|text|txt|문자|note|anno|^tot|toto|위생|sanit|^sl?an|fur|가구|furn|hatch|해치|^pat$|^hid|숨은|dash|leader|인출|defpoint|평면|단면|입면|symbol|^sym|bound|영역|^el\b|\dele$|^fin|void|^wd\d|^dry|^box$|^h$|^deim)')
STD_THK = [90,100,120,150,180,200,250,300]

def classify(name, color):
    if name == "0": return "WALL"
    if RX_EXCL.search(name): return 'EXCLUDE'
    if RX_WALL.search(name): return 'WALL'
    if RX_COL.search(name):  return 'COLUMN'
    if RX_DOOR.search(name): return 'DOOR'
    if RX_WIN.search(name):  return 'WINDOW'
    if color == 2: return 'WALL'
    if color == 3: return 'WALL'
    return 'UNKNOWN'

doc = ezdxf.readfile(DXF); msp = doc.modelspace()
stat = defaultdict(lambda: {"n":0, "len":0.0, "color":7})
def elen(e):
    t = e.dxftype()
    try:
        if t == "LINE": return e.dxf.start.distance(e.dxf.end)
        if t == "LWPOLYLINE":
            pts=[(x[0],x[1]) for x in e.get_points()]; return sum(math.dist(pts[i],pts[i+1]) for i in range(len(pts)-1))
    except: return 0
    return 0
for e in msp:
    l=e.dxf.layer; s=stat[l]; s["n"]+=1; s["len"]+=elen(e)
    try: s["color"]=doc.layers.get(l).color
    except: pass
cat_layers=defaultdict(list)
for l,s in sorted(stat.items(), key=lambda kv:-kv[1]["len"]):
    cat_layers[classify(l, s["color"])].append(l)
wall_layers=set(cat_layers['WALL']); col_layers=set(cat_layers['COLUMN'])
print("분류: WALL",len(cat_layers['WALL']),"COL",len(cat_layers['COLUMN']),
      "DOOR",len(cat_layers['DOOR']),"WIN",len(cat_layers['WINDOW']),
      "EXCL",len(cat_layers['EXCLUDE']),"UNK",len(cat_layers['UNKNOWN']))

def lines_of(layers):
    out=[]
    for e in msp:
        if e.dxf.layer not in layers: continue
        t=e.dxftype()
        if t=="LINE": out.append((e.dxf.start.x,e.dxf.start.y,e.dxf.end.x,e.dxf.end.y))
        elif t=="LWPOLYLINE":
            pts=[(x[0],x[1]) for x in e.get_points()]; rng=range(len(pts)) if e.closed else range(len(pts)-1)
            for i in rng: a=pts[i]; b=pts[(i+1)%len(pts)]; out.append((a[0],a[1],b[0],b[1]))
    return out
wall=lines_of(wall_layers); col=lines_of(col_layers)
print("구조형식:", "라멘(기둥식)" if len(col)>len(wall)*0.5 else "벽식", f"(벽선 {len(wall)} vs 기둥선 {len(col)})")

# 평행쌍 중심선 병합
def rep(s):
    x0,y0,x1,y1=s; dx=x1-x0; dy=y1-y0; L=math.hypot(dx,dy)
    if L<1: return None
    th=math.atan2(dy,dx)%math.pi; cux,cuy=math.cos(th),math.sin(th); nxs,nys=-cuy,cux
    return th, x0*nxs+y0*nys, min(x0*cux+y0*cuy,x1*cux+y1*cuy), max(x0*cux+y0*cuy,x1*cux+y1*cuy)
TB=math.radians(2.5); RB=20
clusters=defaultdict(list)
for s in wall:
    r=rep(s)
    if r: clusters[(round(r[0]/TB),round(r[1]/RB))].append((r[2],r[3]))
merged=[]
for (tk,rk),rng in clusters.items():
    th=tk*TB; rho=rk*RB; rng.sort(); cur=list(rng[0])
    for a,b in rng[1:]:
        if a<=cur[1]+60: cur[1]=max(cur[1],b)
        else: merged.append([th,rho,cur[0],cur[1]]); cur=[a,b]
    merged.append([th,rho,cur[0],cur[1]])
def to_xy(th,rho,t0,t1):
    cux,cuy=math.cos(th),math.sin(th); nxs,nys=-cuy,cux
    return (cux*t0+nxs*rho,cuy*t0+nys*rho),(cux*t1+nxs*rho,cuy*t1+nys*rho)
byth=defaultdict(list)
for i,m in enumerate(merged): byth[round(m[0]/TB)].append(i)
used=[False]*len(merged); walls=[]; thicks=[]
for tk,idxs in byth.items():
    idxs.sort(key=lambda i:merged[i][1])
    for ii in range(len(idxs)):
        i=idxs[ii]
        if used[i]: continue
        th_i,rho_i,t0_i,t1_i=merged[i]; best=None; bg=1e9
        for jj in range(ii+1,len(idxs)):
            j=idxs[jj]
            if used[j]: continue
            gap=abs(merged[j][1]-rho_i)
            if gap>400: break
            if gap<40: continue
            ov=min(t1_i,merged[j][3])-max(t0_i,merged[j][2])
            if ov>60 and gap<bg: best=j; bg=gap
        if best is not None:
            used[i]=used[best]=True; mj=merged[best]; rho_c=(rho_i+mj[1])/2
            p0,p1=to_xy(th_i,rho_c,min(t0_i,mj[2]),max(t1_i,mj[3])); walls.append([p0[0],p0[1],p1[0],p1[1],bg]); thicks.append(bg)
for i,m in enumerate(merged):
    if not used[i] and (m[3]-m[2])>200:
        p0,p1=to_xy(*m); walls.append([p0[0],p0[1],p1[0],p1[1],150])
for s in col: walls.append([s[0],s[1],s[2],s[3],200])
def nearest_std(t): return min(STD_THK,key=lambda x:abs(x-t))
matched=sum(1 for t in thicks if abs(t-nearest_std(t))<=30)
print(f"벽두께 표준(±30mm) 일치 {matched}/{len(thicks)}")

SF=0.001  # mm → m
xs=[c for s in walls for c in (s[0],s[2])]; ys=[c for s in walls for c in (s[1],s[3])]
mnx=min(xs); mny=min(ys)
out=[[round((x0-mnx)*SF,3),round((y0-mny)*SF,3),round((x1-mnx)*SF,3),round((y1-mny)*SF,3),round(max(0.08,min(0.5,thk*SF)),3)] for x0,y0,x1,y1,thk in walls]
outjson=os.path.join(OUT,"walls.json")
json.dump({"unit":"m","wall_height":3.0,"count":len(out),"segments":out}, open(outjson,"w"))
print(f"최종 {len(out)}세그먼트, 건물 {(max(xs)-min(xs))*SF:.1f}x{(max(ys)-min(ys))*SF:.1f}m -> {outjson}")
