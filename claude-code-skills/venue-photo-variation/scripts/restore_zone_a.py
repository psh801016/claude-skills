# 재실사화 후보 위에 원본 합성본의 그래픽(ZONE A: LED 화면·현수막·글자·로고)을 되돌린다.
# 배경: 2026-10-27 INWEPF 연회장 재실사화 — GPT 결과가 실사감은 좋지만 작은 글자·로고가 깨지고("for" 누락,
#       주최 로고 뭉개짐) 해상도도 1672x941 로 줄어 나왔다. exhibition-pixel-preservation 규칙대로
#       후보를 원본에 정합(ORB 호모그래피) → 그래픽 마스크(= 박스 ∩ 합성본-플레이트 차이) 안만 원본 픽셀로 복원.
#       원본 그래픽에는 후보의 저주파 밝기(조명 얼룩)만 곱해 붙여 '붙여넣은 티'를 줄인다.
# 배경(천장·벽·무대·카펫)도 원본 픽셀로 되돌리고 후보에서는 3D 물건만 가져온다(바닥 그림자는 밝기 비로 옮김).
# 사용:
#   python restore_zone_a.py --src 합성본.png --cand GPT후보.png (--plate 클린플레이트.png | --obj-mask 물건.png) \
#       --boxes "x1,y1,x2,y2;x1,y1,x2,y2" --floor-y 720 --out 최종.png [--size 2560x1440]
#   박스 좌표는 합성본(--src) 픽셀 기준. 그래픽 앞을 가리는 의자·사람이 박스에 들어가지 않게 잡는다.
# 성공 토큰: RESTORE_OK <경로> inliers=<n> rms=<px>   실패: RESTORE_FAIL <사유> (exit 1)
# PIL 로 입출력한다(cv2.imread 는 한글 경로를 못 읽는다).
import argparse, sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image


def load(p):
    return np.asarray(Image.open(p).convert("RGB"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--cand", required=True)
    ap.add_argument("--plate")
    ap.add_argument("--obj-mask", help="플레이트가 없을 때: 3D 물건 영역을 흰색으로 칠한 PNG(합성본 크기)")
    ap.add_argument("--boxes", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", default="2560x1440")
    ap.add_argument("--floor-y", type=int, required=True,
                    help="합성본 픽셀 기준 바닥이 시작되는 y. 이 아래만 후보의 그림자·빛 번짐(저주파 밝기)을 배경에 옮긴다")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        print(f"RESTORE_FAIL 출력이 이미 있음(덮어쓰기 금지): {out}"); sys.exit(1)

    src = load(a.src); h, w = src.shape[:2]
    cand = cv2.resize(load(a.cand), (w, h), interpolation=cv2.INTER_CUBIC)
    if not (a.plate or a.obj_mask):
        print("RESTORE_FAIL --plate 또는 --obj-mask 중 하나가 필요"); sys.exit(1)

    # 1) 후보 → 원본 정합
    g1, g2 = cv2.cvtColor(cand, cv2.COLOR_RGB2GRAY), cv2.cvtColor(src, cv2.COLOR_RGB2GRAY)
    orb = cv2.ORB_create(8000)
    k1, d1 = orb.detectAndCompute(g1, None); k2, d2 = orb.detectAndCompute(g2, None)
    ms = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d1, d2), key=lambda m: m.distance)[:2000]
    if len(ms) < 50:
        print(f"RESTORE_FAIL 정합 특징점 부족({len(ms)})"); sys.exit(1)
    p1 = np.float32([k1[m.queryIdx].pt for m in ms]); p2 = np.float32([k2[m.trainIdx].pt for m in ms])
    H, inl = cv2.findHomography(p1, p2, cv2.RANSAC, 3.0)
    inl = inl.ravel().astype(bool)
    rms = float(np.sqrt(np.mean(np.sum((cv2.perspectiveTransform(p1[inl][None], H)[0] - p2[inl]) ** 2, 1))))
    warped = cv2.warpPerspective(cand, H, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # 2) 그래픽 마스크 = 박스 ∩ (합성본이 플레이트와 다른 곳)
    if a.plate:
        plate = cv2.resize(load(a.plate), (w, h), interpolation=cv2.INTER_AREA)
        added = (np.abs(src.astype(int) - plate.astype(int)).max(2) > 25).astype(np.uint8)
    else:  # 2026-10-28: 플레이트 없는 합성본 — 3D 물건 마스크를 직접 받는다
        added = (cv2.resize(np.asarray(Image.open(a.obj_mask).convert("L")), (w, h)) > 127).astype(np.uint8)
    box = np.zeros((h, w), np.uint8)
    for b in a.boxes.split(";"):
        x1, y1, x2, y2 = map(int, b.split(","))
        box[y1:y2, x1:x2] = 1
    m = cv2.morphologyEx(added & box, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)) & box
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2)[..., None]

    # 3) 배경도 원본으로 (2026-10-27 반려: "배경 같은 곳인데 왜 틀어져" — GPT 는 천장·샹들리에·벽까지 다시 그린다)
    #    후보에서 가져오는 건 3D 물건(합성본-플레이트 차이 영역, 가장자리 여유 포함)뿐이다.
    obj = cv2.dilate(added, np.ones((21, 21), np.uint8)).astype(np.float32)
    obj = cv2.GaussianBlur(obj, (0, 0), 3)[..., None]
    keep = np.maximum(m, 1 - obj)  # 1 = 원본 픽셀
    L = lambda x: cv2.GaussianBlur(cv2.cvtColor(x, cv2.COLOR_RGB2GRAY).astype(np.float32) + 1, (0, 0), 25)
    ratio = L(warped) / L(src)
    ramp = np.clip((np.arange(h, dtype=np.float32) - a.floor_y) / 30 + 0.5, 0, 1)[:, None]  # 바닥 위 = 1(밝기 그대로)
    gain_bg = 1 + (np.clip(ratio, 0.55, 1.25) - 1) * ramp  # 바닥: 접지 그림자·LED 스필
    gain_g = np.clip(ratio, 0.8, 1.2)                       # 그래픽: 조명 얼룩만 약하게
    gain = (gain_g * m[..., 0] + gain_bg * (1 - m[..., 0]))[..., None]
    res = warped * (1 - keep) + np.clip(src * gain, 0, 255) * keep

    W, Hh = map(int, a.size.split("x"))
    res = Image.fromarray(res.astype(np.uint8)).resize((W, Hh), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    res.save(out)
    Image.blend(res, Image.fromarray(src).resize((W, Hh), Image.LANCZOS), 0.5).save(out.with_name(out.stem + "_overlay50.png"))
    Image.fromarray((m[..., 0] * 255).astype(np.uint8)).save(out.with_name(out.stem + "_mask.png"))
    print(f"RESTORE_OK {out} inliers={int(inl.sum())} rms={rms:.2f}px")


if __name__ == "__main__":
    main()
