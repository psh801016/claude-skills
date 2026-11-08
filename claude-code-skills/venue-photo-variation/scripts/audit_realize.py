# 재실사화 납품 전 자동 검사 — 반려 점검표(배경 틀어짐·글자 깨짐·없던 물건·해상도)를 숫자로 잡는다.
# 배경: 2026-10-27 "배경이 왜 틀어져"(천장 평균차 14.5), 글자 "for" 누락, 2026-11-05 "이거 왜 자꾸 스킬대로 안 나오냐".
# 사용: python audit_realize.py --src 합성본.png --final 최종.png (--plate 클린.png | --obj-mask 물건.png) --boxes "x1,y1,x2,y2;..." --floor-y 812
# 성공 토큰: REALIZE_AUDIT_PASS   실패: REALIZE_AUDIT_FAIL <사유> (exit 1)
import argparse, sys
import numpy as np, cv2
from PIL import Image


def load(p, size=None):
    im = Image.open(p).convert("RGB")
    if size and im.size != size:
        im = im.resize(size, Image.LANCZOS)
    return np.asarray(im).astype(np.float32)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="합성본(3D 올린 원본)")
    ap.add_argument("--final", required=True, help="납품 후보")
    ap.add_argument("--plate"); ap.add_argument("--obj-mask")
    ap.add_argument("--boxes", default="", help="그래픽 박스(합성본 픽셀)")
    ap.add_argument("--floor-y", type=int, required=True)
    ap.add_argument("--size", default="2560x1440")
    a = ap.parse_args()
    fails, info = [], []
    fin = Image.open(a.final)
    W, Hh = map(int, a.size.split("x"))
    if fin.size != (W, Hh):
        fails.append(f"해상도 {fin.size} ≠ {W}x{Hh}")
    final = load(a.final); src = load(a.src, (final.shape[1], final.shape[0]))
    H, Wd = final.shape[:2]; sx = Wd / Image.open(a.src).size[0]; sy = H / Image.open(a.src).size[1]
    if a.plate:
        plate = load(a.plate, (Wd, H)); obj = np.abs(src - plate).max(2) > 25
    elif a.obj_mask:
        obj = np.asarray(Image.open(a.obj_mask).convert("L").resize((Wd, H))) > 127
    else:
        print("REALIZE_AUDIT_FAIL --plate 또는 --obj-mask 필요"); sys.exit(1)
    obj = cv2.dilate(obj.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    yy = np.mgrid[0:H, 0:Wd][0]; fy = int(a.floor_y * sy)
    diff = np.abs(final - src).mean(2)
    # ① 배경(바닥선 위, 물건 밖) 픽셀 불변
    bg = (yy < fy) & ~obj
    if bg.sum() > 1000:
        d = float(diff[bg].mean()); info.append(f"bg diff={d:.2f}")
        if d > 1.0:
            fails.append(f"배경이 바뀜(천장·벽 평균차 {d:.2f} > 1.0) — restore_zone_a 로 배경을 원본 픽셀로")
    # ② 그래픽 박스 안 불변
    # 그래픽은 밝기(조명 얼룩)만 바뀌고 구조(글자·로고)는 원본이어야 한다 → 저주파 밝기 비를 나눈 뒤 비교
    L = lambda x: cv2.GaussianBlur(x.mean(2), (0, 0), 25) + 1
    ratio = (L(final) / L(src))[..., None]
    sdiff = np.abs(final - np.clip(src * ratio, 0, 255)).mean(2)
    for b in [b for b in a.boxes.split(";") if b.strip()]:
        x1, y1, x2, y2 = map(int, b.split(","))
        reg = sdiff[int(y1 * sy):int(y2 * sy), int(x1 * sx):int(x2 * sx)]
        m = float(reg.mean()); info.append(f"box{b} sdiff={m:.2f}")
        if m > 4.0:
            fails.append(f"그래픽 박스 {b} 의 글자·로고가 바뀜(구조차 {m:.2f} > 4) — 원본 픽셀 복원")
    # ③ 3D 물건은 실제로 바뀌어야 한다(실사화가 됐는지)
    ob = obj & (yy >= fy)
    if ob.sum() > 1000:
        d = float(diff[ob].mean()); info.append(f"obj diff={d:.2f}")
        if d < 3.0:
            fails.append(f"3D 물건이 거의 안 바뀜(평균차 {d:.2f} < 3) — 후보가 반영되지 않았다")
    # ④ 물건 밖 바닥은 밝기만 바뀌고 무늬는 유지(채도·색상 급변 없음)
    fl = (yy >= fy) & ~obj
    if fl.sum() > 1000:
        hs, hf = [cv2.cvtColor(x.astype(np.uint8), cv2.COLOR_RGB2HSV)[..., 0].astype(np.float32) for x in (src, final)]
        hd = float(np.minimum(np.abs(hs - hf), 180 - np.abs(hs - hf))[fl].mean()); info.append(f"floor hue diff={hd:.1f}")
        if hd > 8:
            fails.append(f"바닥 색상이 바뀜(색상차 {hd:.1f} > 8) — 바닥은 밝기 비만 옮긴다")
    if fails:
        print("REALIZE_AUDIT_FAIL " + " | ".join(fails) + "  [" + ", ".join(info) + "]"); sys.exit(1)
    print("REALIZE_AUDIT_PASS " + ", ".join(info))


if __name__ == "__main__":
    main()
