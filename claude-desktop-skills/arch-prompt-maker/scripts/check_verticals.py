# 건축사진 수직선 검사 — 세로선이 정말 수직인가(시프트 렌즈 보정 사진의 기본 문법).
# 배경(2026-11-11): ASURA님 지정 레퍼런스 건축사진가 @hanskim_studio 의 준공 사진은 모두 세로선 0°(시프트·현장 보정).
#   AI 실사화·합성은 건물을 올려다보는 3점 투시로 수직을 모으거나 비틀어 '렌더/합성 티'가 났다.
# 사용: python check_verticals.py --img 결과.png [--max-deg 0.3] [--exclude-mask 사람.png]
# 성공 토큰: VERT_OK median=<deg> lines=<n>   실패: VERT_FAIL (exit 1)
import argparse, sys
import numpy as np, cv2
from PIL import Image


def vertical_tilts(gray, excl=None, minlen=None):
    h = gray.shape[0]
    e = cv2.Canny(gray, 50, 150)
    if excl is not None:
        e[excl] = 0
    L = cv2.HoughLinesP(e, 1, np.pi / 720, 80, minLineLength=minlen or max(40, h // 12), maxLineGap=6)
    if L is None:
        return np.array([])
    d = []
    for x1, y1, x2, y2 in L[:, 0]:
        a = np.degrees(np.arctan2(x2 - x1, y2 - y1))   # 수직 기준 기울기
        a = (a + 90) % 180 - 90
        if abs(a) < 8:                                  # 거의 세로인 선만
            d.append(a)
    return np.array(d)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True); ap.add_argument("--max-deg", type=float, default=0.3)
    ap.add_argument("--exclude-mask")
    a = ap.parse_args()
    g = cv2.cvtColor(np.asarray(Image.open(a.img).convert("RGB")), cv2.COLOR_RGB2GRAY)
    ex = None
    if a.exclude_mask:
        ex = cv2.resize(np.asarray(Image.open(a.exclude_mask).convert("L")), g.shape[::-1]) > 127
    d = vertical_tilts(g, ex)
    if len(d) < 5:
        print(f"VERT_FAIL 세로선 부족(lines={len(d)}) — 사람이 확인"); sys.exit(1)
    med = float(np.median(np.abs(d)))
    # 수직 수렴(3점 투시): 화면 왼쪽 선과 오른쪽 선의 기울기 부호가 반대로 체계적
    tag = "VERT_OK" if med <= a.max_deg else "VERT_FAIL"
    print(f"{tag} median={med:.2f} lines={len(d)} mean_signed={float(np.mean(d)):.2f}")
    sys.exit(0 if tag == "VERT_OK" else 1)


if __name__ == "__main__":
    main()
