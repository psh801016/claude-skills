# extract_pdf.py — 벡터 PDF 평면도에서 벽 중심선 추출 → walls.json + preview.png
# 실행: python extract_pdf.py <도면.pdf> <작업폴더> [건물폭m] [사선컷비율]
#   건물폭m = 도면 가로 실치수(축척의 유일한 근거). 생략 시 50m 가정(임의).
#   사선컷비율(0~1, 선택) = 이 비율(y 상단 기준) 아래의 사선을 제거(주차 램프 빗금 등 특정 도면용).
#     생략하면 사선을 제거하지 않는다 — 기본 동작이 임의 도면에 안전하도록 opt-in.
import sys, os, math, json
import pdfplumber, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
import networkx as nx

PDF = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "."
BUILDING_W = float(sys.argv[3]) if len(sys.argv) > 3 else 50.0
DIAG_YCUT = float(sys.argv[4]) if len(sys.argv) > 4 else None
os.makedirs(OUT, exist_ok=True)

pdf = pdfplumber.open(PDF); p = pdf.pages[0]; H = p.height
def is_black(l):
    c = l.get('stroking_color'); return c == 0 or c == (0,0,0) or (isinstance(c,(int,float)) and c < 0.2)
def length(l): return math.hypot(l['x1']-l['x0'], l['y1']-l['y0'])
lines = [l for l in p.lines if is_black(l) and length(l) > 12]

Hl=[]; Vl=[]; Dl=[]; ANG=3
for l in lines:
    dx=l['x1']-l['x0']; dy=l['y1']-l['y0']; a=math.degrees(math.atan2(abs(dy),abs(dx)))
    if a < ANG: y=(l['y0']+l['y1'])/2; xa,xb=sorted([l['x0'],l['x1']]); Hl.append([y,xa,xb])
    elif a > 90-ANG: x=(l['x0']+l['x1'])/2; ya,yb=sorted([l['y0'],l['y1']]); Vl.append([x,ya,yb])
    else: Dl.append([l['x0'],l['y0'],l['x1'],l['y1'],length(l)])
# 사선: 짧은 조각(<=30)만 노이즈로 제거. 위치 기반 제거는 opt-in(DIAG_YCUT) —
# 무조건 하단 사선을 지우면 다른 도면의 하단 사선 벽이 조용히 소실된다(fail-loud 원칙 위배).
Dl=[d for d in Dl if d[4]>30]
if DIAG_YCUT is not None:
    allys=[l[0] for l in Hl]+[(l[1]+l[2])/2 for l in Vl]
    ycut=min(allys)+(max(allys)-min(allys))*DIAG_YCUT
    before=len(Dl)
    Dl=[d for d in Dl if (d[1]+d[3])/2 < ycut]
    print("diag ycut %.2f: %d -> %d (제거 %d)" % (DIAG_YCUT, before, len(Dl), before-len(Dl)))

THK_MIN, THK_MAX, OVL = 1.0, 9.0, 5.0
def pair(items):
    used=[False]*len(items); idx=sorted(range(len(items)),key=lambda i:items[i][0]); res=[]
    for ii in range(len(idx)):
        i=idx[ii]
        if used[i]: continue
        best=None; bg=1e9; bo=None
        for jj in range(ii+1,len(idx)):
            j=idx[jj]
            if used[j]: continue
            gap=items[j][0]-items[i][0]
            if gap>THK_MAX: break
            if gap<THK_MIN: continue
            a0=max(items[i][1],items[j][1]); a1=min(items[i][2],items[j][2])
            if (a1-a0)>OVL and gap<bg:
                best=j; bg=gap; bo=(min(items[i][1],items[j][1]),max(items[i][2],items[j][2]))
        if best is not None:
            used[i]=used[best]=True; c=(items[i][0]+items[best][0])/2; res.append((c,bo[0],bo[1],bg))
    return res, used
Hr,Hu = pair(Hl); Vr,Vu = pair(Vl)
walls=[]
for c,a0,a1,g in Hr: walls.append([a0,c,a1,c,g])
for c,a0,a1,g in Vr: walls.append([c,a0,c,a1,g])
DEF=2.5
for i,l in enumerate(Hl):
    if not Hu[i] and (l[2]-l[1])>25: walls.append([l[1],l[0],l[2],l[0],DEF])
for i,l in enumerate(Vl):
    if not Vu[i] and (l[2]-l[1])>25: walls.append([l[0],l[1],l[0],l[2],DEF])
for x0,y0,x1,y1,ln in Dl: walls.append([x0,y0,x1,y1,DEF])

# graph: snap + 큰 컴포넌트만(총길이 기준) → 고립 잡선 제거
SNAP=5.0
def sn(x,y): return (round(x/SNAP)*SNAP, round(y/SNAP)*SNAP)
G=nx.Graph(); ed=[]
for w in walls:
    n0=sn(w[0],w[1]); n1=sn(w[2],w[3])
    if n0==n1: continue
    L=math.hypot(w[2]-w[0],w[3]-w[1]); G.add_edge(n0,n1,L=L); ed.append((n0,n1,w))
keep=set()
for c in nx.connected_components(G):
    sub=G.subgraph(c); tot=sum(d['L'] for *_,d in sub.edges(data=True))
    if tot>80: keep|=set(c)
kept=[w for n0,n1,w in ed if n0 in keep and n1 in keep]
print("raw:",len(lines),"H:",len(Hl),"V:",len(Vl),"D:",len(Dl),"| walls:",len(walls),"-> iso제거후:",len(kept))

# 스케일: 건물 가로폭 = BUILDING_W (m)
xs=[c for w in kept for c in (w[0],w[2])]; ys=[c for w in kept for c in (w[1],w[3])]
bx0,bx1,by0,by1=min(xs),max(xs),min(ys),max(ys); sf=BUILDING_W/(bx1-bx0)
segs=[]
for x0,y0,x1,y1,thk in kept:
    X0=(x0-bx0)*sf; Y0=(by1-y0)*sf; X1=(x1-bx0)*sf; Y1=(by1-y1)*sf
    t=max(0.08,min(0.5,thk*sf)); segs.append([round(X0,3),round(Y0,3),round(X1,3),round(Y1,3),round(t,3)])
outjson=os.path.join(OUT,"walls.json")
json.dump({"unit":"m","wall_height":3.0,"count":len(segs),"segments":segs}, open(outjson,"w"))

# 검증 프리뷰 2단(raw vs 중심선)
fig,ax=plt.subplots(1,2,figsize=(20,14))
for l in p.lines:
    if is_black(l): ax[0].plot([l['x0'],l['x1']],[H-l['y0'],H-l['y1']],'0.6',lw=0.5)
ax[0].set_title("raw black lines"); ax[0].set_aspect('equal'); ax[0].axis('off')
for x0,y0,x1,y1,thk in kept:
    ax[1].plot([x0,x1],[H-y0,H-y1],'r-',lw=max(1.0,thk*0.6))
ax[1].set_title(f"CENTERLINES ({len(kept)})  scale={BUILDING_W}m"); ax[1].set_aspect('equal'); ax[1].axis('off')
plt.tight_layout(); plt.savefig(os.path.join(OUT,"preview.png"),dpi=120,bbox_inches='tight')
pdf.close()
print("saved:", outjson, "| building %.1fx%.1fm" % (BUILDING_W, (by1-by0)*sf))
