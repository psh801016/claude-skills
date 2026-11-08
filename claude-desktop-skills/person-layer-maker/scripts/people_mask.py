# 사람 마스크 — 사람 몸에만 딱 맞게. lock_booth.py 의 --people 로 넘긴다.
# 배경: 2026-11-06 Kofpi "모서리 안 보이냐". 사물까지 잡는 분할(BiRefNet)·크기보정 저장 마스크를 그대로 쓰면 옆 카운터 모서리·기둥까지
#   사람으로 잡혀 그 자리에 AI 가 그린 부스가 남았다(두 겹 모서리). 반대로 사람 전용 분할(u2net_human_seg)은 카운터 뒤 사람·
#   다리 일부를 놓친다(팔·몸 덮임). 그래서: 사람 전용 분할을 기본으로, 놓친 사람만 박스로 지정해 그 박스 안에서만 BiRefNet.
# 사용: python people_mask.py --img AI사진.png --out 사람마스크.png [--box x0,y0,x1,y1 ...] [--canvas 2560x1440]
#   --box 는 오버레이(<out>_overlay.jpg)를 보고 '빠진 사람'에만 준다. 박스는 사람 몸만 감싸게(옆 카운터가 들어가지 않게) 좁게.
# 출력: PEOPLE_MASK_OK <경로> people=<n>  + <out>_overlay.jpg (청록 = 사람으로 본 곳)
import argparse, sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--box", action="append", default=[]); ap.add_argument("--canvas", default="2560x1440")
    ap.add_argument("--plate", help="같은 AI 사진에서 사람만 지운 판(정합본). 주면 '박스별 분할 ∩ 판 차이'로 사람만 정확히 — 권장(2026-11-06)")
    a = ap.parse_args()
    W, H = map(int, a.canvas.split("x"))
    im = Image.open(a.img).convert("RGB").resize((W, H), Image.LANCZOS); A = np.asarray(im)
    from rembg import remove, new_session
    m = (np.asarray(remove(im, session=new_session("u2net_human_seg"), only_mask=True)) > 100).astype(np.uint8)
    if a.box and not a.plate:
        sess = new_session("birefnet-general")
        for b in a.box:
            x0, y0, x1, y1 = map(int, b.split(","))
            seg = np.asarray(remove(Image.fromarray(A[y0:y1, x0:x1]), session=sess, only_mask=True)) > 110
            m[y0:y1, x0:x1] |= seg.astype(np.uint8)
    if a.plate:
        # 판 차이 = 사람(+그 그림자·AI가 다시 그린 벽). 박스별 분할 = 사람(+옆 카운터). 둘이 겹치는 곳 = 사람만.
        #   손 박스·u2net 만으로는 스태프 다리·남성 머리/다리가 빠지거나 카운터 모서리가 섞였다(2026-11-06 반려 3회).
        P = np.asarray(Image.open(a.plate).convert("RGB").resize((W, H), Image.LANCZOS)).astype(np.float32); C = A.astype(np.float32)
        P = P + cv2.GaussianBlur(C - P, (0, 0), 30)
        d = np.abs(cv2.GaussianBlur(C, (0, 0), 1.5) - cv2.GaussianBlur(P, (0, 0), 1.5)).max(2)
        diff = cv2.dilate((d > 18).astype(np.uint8), np.ones((9, 9), np.uint8))
        boxes = [tuple(map(int, b.split(","))) for b in a.box]
        if not boxes:   # 판 차이의 큰 세로 덩어리에서 자동 박스
            dd = cv2.morphologyEx(cv2.morphologyEx((d > 28).astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)), cv2.MORPH_CLOSE, np.ones((15, 9), np.uint8))
            n0, l0, s0, _ = cv2.connectedComponentsWithStats(dd)
            for j in range(1, n0):
                x, y, bw, bh, ar = s0[j]
                if ar > 1500 and bh > 60: boxes.append((max(0, x - 15), max(0, y - 15), min(W, x + bw + 15), min(H, y + bh + 15)))
        sess = new_session("birefnet-general"); pm = np.zeros((H, W), np.uint8)
        for x0, y0, x1, y1 in boxes:
            seg = (np.asarray(remove(Image.fromarray(A[y0:y1, x0:x1]), session=sess, only_mask=True)) > 110).astype(np.uint8)
            pm[y0:y1, x0:x1] |= seg & diff[y0:y1, x0:x1]
        pm = cv2.morphologyEx(pm, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        m = np.maximum(m, pm)
        cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); f = np.zeros_like(m); cv2.drawContours(f, cnts, -1, 1, -1); m = f
    m = cv2.dilate(m, np.ones((3, 3), np.uint8))
    out = Path(a.out); Image.fromarray(m * 255).save(out)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    people = [list(map(int, st[j][:4])) for j in range(1, n) if st[j][4] > 2000]
    V = A.copy(); V[m > 0] = (V[m > 0] * 0.45 + np.array([0, 255, 255]) * 0.55).astype(np.uint8)
    for x, y, w, h in people: cv2.rectangle(V, (x, y), (x + w, y + h), (255, 0, 0), 2)
    Image.fromarray(V).resize((W // 2, H // 2)).save(out.with_name(out.stem + "_overlay.jpg"), quality=85)
    print(f"PEOPLE_MASK_OK {out} people={len(people)} boxes={people}")


if __name__ == "__main__":
    main()
