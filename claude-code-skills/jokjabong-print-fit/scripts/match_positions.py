"""원본 대지(측면 판)를 요청서 슬라이드 그림과 비교해 좌측1/좌측2/정면/우측1/우측2 위치를 정한다.
아래 jobs 딕셔너리(슬라이드 번호 → 원본 대지 목록)는 행사마다 고쳐 쓴다. 1/10 축척 소형 대지는 썸네일이 작아 오판할 수 있으니 눈으로 한 번 더 본다.
사용: python -X utf8 match_positions.py "<요청서.pptx>""""
import sys, io, fitz, numpy as np
from pptx import Presentation
from PIL import Image
P = Presentation(sys.argv[1]); S="C:/jjb/src/"
def thumb(im): return np.asarray(im.convert("L").resize((24,32)),float)
def walk(shs):
    for s in shs:
        if s.shape_type==6: yield from walk(s.shapes)
        else: yield s
def slide_pics(n):
    s=P.slides[n-1]; pics=[]; labels=[]
    for x in walk(s.shapes):
        if x.shape_type==13: pics.append((x.left+x.width/2, Image.open(io.BytesIO(x.image.blob))))
        elif x.has_text_frame and x.text_frame.text.strip() in ('좌측','정면','우측','좌측 1','좌측 2','우측 1','우측 2'): labels.append((x.left+x.width/2, x.text_frame.text.strip()))
    return pics, labels
def pages(f, ab=None):
    d=fitz.open(S+f, filetype="pdf"); out=[]
    for i,p in enumerate(d):
        if ab and i+1 not in ab: continue
        pix=p.get_pixmap(matrix=fitz.Matrix(0.3,0.3) if p.rect.width<2000 else fitz.Matrix(0.05,0.05))
        out.append((f"{f}#{i+1}", Image.frombytes("RGB",(pix.width,pix.height),pix.samples)))
    return out
jobs = {3:pages("sparrow_s1.ai")+pages("sparrow_s2.ai"), 7:pages("somansa.ai"), 8:pages("woori.pdf"), 9:pages("nnsp.ai"),
        10:sum([pages(f"wins_s{i}.ai") for i in range(1,5)],[]), 13:pages("secure_side.ai"), 15:sum([pages(f"igloo_{i}.ai") for i in range(1,4)],[])}
for n,srcs in jobs.items():
    pics, labels = slide_pics(n)
    pics=[p for p in pics if p[1].width/p[1].height < 1]  # portrait side panels only
    print(f"slide {n}: labels {sorted(labels)}")
    for name, im in srcs:
        t=thumb(im); best=min(pics, key=lambda p: ((thumb(p[1])-t)**2).mean())
        lab=min(labels, key=lambda l: abs(l[0]-best[0]))[1]
        err=((thumb(best[1])-t)**2).mean()
        print(f"   {name:18s} -> {lab}  (x={best[0]/36000:.0f}mm, err={err:.0f})")
