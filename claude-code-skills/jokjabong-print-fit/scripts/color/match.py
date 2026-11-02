"""RGB → CMYK '색 맞춤' 변환 (기준: Japan Color 2001 Coated, 종이 흰색 기준 상대 색도).
- 표준 변환: lcms 상대색도 + 검은점 보정(BPC) → 그림 픽셀에 쓴다
- 단색(벡터) 최적화: 표준 변환값에서 출발해 C·M·Y·K 를 1% 단위로 움직여 원본 RGB 와의 ΔE2000 이 가장 작은 값을 찾는다
  (총 잉크 320% 이하, 원래 K 가 0 인 밝은 색에는 K 를 넣지 않는다 — 탁해지지 않게)"""
import math
from functools import lru_cache
from PIL import Image, ImageCms
ICC = r"C:\Windows\System32\spool\drivers\color\JapanColor2001Coated.icc"
JC = ImageCms.getOpenProfile(ICC); SRGB = ImageCms.createProfile("sRGB"); LAB = ImageCms.createProfile("LAB")
REL = ImageCms.Intent.RELATIVE_COLORIMETRIC; BPC = ImageCms.Flags.BLACKPOINTCOMPENSATION
T_RGB_CMYK = ImageCms.buildTransform(SRGB, JC, "RGB", "CMYK", renderingIntent=REL, flags=BPC)
T_RGB_LAB = ImageCms.buildTransform(SRGB, LAB, "RGB", "LAB", renderingIntent=REL)
T_CMYK_LAB = ImageCms.buildTransform(JC, LAB, "CMYK", "LAB", renderingIntent=REL)

def _lab(img, t):
    L, a, b = ImageCms.applyTransform(img, t).getpixel((0, 0)); return (L / 2.55, a - 128, b - 128)
def lab_rgb(rgb): return _lab(Image.new("RGB", (1, 1), tuple(rgb)), T_RGB_LAB)
@lru_cache(maxsize=None)
def lab_cmyk(c): return _lab(Image.new("CMYK", (1, 1), tuple(round(v * 2.55) for v in c)), T_CMYK_LAB)
def std(rgb): return tuple(round(v / 2.55) for v in ImageCms.applyTransform(Image.new("RGB", (1, 1), tuple(rgb)), T_RGB_CMYK).getpixel((0, 0)))

def de2000(l1, l2):
    L1, a1, b1 = l1; L2, a2, b2 = l2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2); Cb = (C1 + C2) / 2; G = 0.5 * (1 - math.sqrt(Cb**7 / (Cb**7 + 25**7)))
    a1p, a2p = a1 * (1 + G), a2 * (1 + G); C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1 = math.degrees(math.atan2(b1, a1p)) % 360; h2 = math.degrees(math.atan2(b2, a2p)) % 360
    dL, dC, dh = L2 - L1, C2p - C1p, h2 - h1
    if C1p * C2p == 0: dh = 0
    elif dh > 180: dh -= 360
    elif dh < -180: dh += 360
    dH = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2))
    Lb, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    hb = (h1 + h2) / 2 if abs(h1 - h2) <= 180 else (h1 + h2 + 360) / 2
    T = 1 - .17 * math.cos(math.radians(hb - 30)) + .24 * math.cos(math.radians(2 * hb)) + .32 * math.cos(math.radians(3 * hb + 6)) - .2 * math.cos(math.radians(4 * hb - 63))
    SL = 1 + .015 * (Lb - 50)**2 / math.sqrt(20 + (Lb - 50)**2); SC = 1 + .045 * Cbp; SH = 1 + .015 * Cbp * T
    RT = -2 * math.sqrt(Cbp**7 / (Cbp**7 + 25**7)) * math.sin(math.radians(60 * math.exp(-((hb - 275) / 25)**2)))
    return math.sqrt((dL / SL)**2 + (dC / SC)**2 + (dH / SH)**2 + RT * (dC / SC) * (dH / SH))

def best(rgb):
    """원본 RGB 에 가장 가까운 CMYK (정수 %) 와 ΔE"""
    ref = lab_rgb(rgb); st = list(std(rgb)); allowK = st[3] > 0 or max(rgb) - min(rgb) < 12
    score = lambda c: de2000(ref, lab_cmyk(tuple(c)))
    if max(rgb) - min(rgb) <= 6:   # 검정·회색은 K 단독 (인쇄 관례: 글자 번짐·4도 맞춤 어긋남 방지)
        k = min(range(101), key=lambda k: score((0, 0, 0, k)))
        return (0, 0, 0, k), score((0, 0, 0, k))
    while sum(st) > 300 and st[3] > 0: st[3] -= 1   # 출발점도 총 잉크 한도 안으로
    starts = [st] + ([st[:3] + [min(100, st[3] + d)] for d in (8, 16)] if allowK else [])   # 한 출발점에선 중간에 멈출 수 있다
    bestc, bests = None, 1e9
    for cur in starts:
        s = score(cur)
        for step in (8, 4, 2, 1):
            moved = True
            while moved:
                moved = False
                for ch in range(4 if allowK else 3):
                    for d in (step, -step):
                        c = cur[:]; c[ch] = min(100, max(0, c[ch] + d))
                        if sum(c) > 300 or c == cur: continue
                        sc = score(c)
                        if sc < s - 1e-6: cur, s, moved = c, sc, True
        if s < bests: bestc, bests = cur, s
    return tuple(bestc), bests

if __name__ == "__main__":
    for name, rgb, now in [("신화 주황", (242, 97, 34), (0, 76, 99, 0)), ("소만사 남색", (40, 56, 116), (99, 90, 25, 12)), ("소만사 연하늘", (198, 216, 239), (20, 9, 0, 0)),
                           ("소만사 파랑", (29, 77, 159), (97, 80, 3, 0)), ("우리 파랑", (11, 125, 224), (79, 48, 0, 0)), ("우리 남색", (11, 58, 107), (100, 84, 32, 18))]:
        ref = lab_rgb(rgb); st = std(rgb); b, s = best(rgb)
        print(f"{name:8s} {str(rgb):15s} 현재 {str(now):17s} ΔE {de2000(ref, lab_cmyk(now)):4.1f} | 표준 {str(st):17s} ΔE {de2000(ref, lab_cmyk(st)):4.1f} | 최적 {str(b):17s} ΔE {s:4.1f}")
