# -*- coding: utf-8 -*-
"""릴스 '와이프 반전' 1개를 만든다 (크레딧 0, 로컬 ffmpeg).

흐름: 도면 플래시 컷(0.6초씩) → 흰 모델(문구1) → 세로선 와이프 → 실사(문구2).
- 흰 모델과 실사는 같은 카메라 각도여야 한다(같은 렌더의 i2i 실사화). 50% 겹쳐 어긋나면 쓰지 않는다.
- 글자는 화면 가운데 한 줄만(위 14%·아래 35%는 인스타 버튼 자리). 제목 띠·번호·검은 틀 금지.

사고 배경(2026-11-10): 검은 틀+단계 번호 슬라이드, 세로 꽉 채운 가로그림 훑기, 3,950크레딧 AI 드론 영상이
모두 '구리다'로 반려. 업계 조사 공통점 = 같은 각도 비포→애프터 반전 1번 + 7~15초 + 가운데 짧은 문구.

사용:
  python reel_wipe.py --clay 모델.png --photo 실사.png --out 릴스.mp4 \
      [--flash 도면1.png 도면2.png] [--cx 0.5] [--text1 "도면만 넣었다"] [--text2 "나머지는 전부 AI"] [--sec 9]
성공 토큰: REEL_OK <경로> <초>
"""
import argparse, math, os, subprocess, sys, tempfile, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FONT = r"C:\Windows\Fonts\malgunbd.ttf"


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def vcrop(im, cx):
    """가로 이미지를 9:16 세로로 자른다(cx = 가로 중심 비율)."""
    w, h = im.size
    cw = int(h * 9 / 16)
    x0 = max(0, min(w - cw, int(w * cx) - cw // 2))
    return im.crop((x0, 0, x0 + cw, h))


def fill_white(im):
    """도면: 흰 바탕 세로 화면을 최대한 채우게 앉힌다."""
    s = min((W - 60) / im.width, (H - 160) / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    c = Image.new("RGB", (W, H), "white")
    c.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    return c


def zoomed(src, z):
    sw, sh = src.size
    nw, nh = sw / z, sh / z
    return src.crop(((sw - nw) / 2, (sh - nh) / 2, (sw + nw) / 2, (sh + nh) / 2)).resize((W, H), Image.LANCZOS)


def put_text(im, s, alpha, font):
    if alpha <= 0 or not s:
        return im
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = (W - d.textlength(s, font=font)) / 2, 820
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((x, y + 4), s, font=font, fill=(0, 0, 0, int(170 * alpha)))
    d.text((x, y), s, font=font, fill=(255, 255, 255, int(255 * alpha)))
    base = im.convert("RGBA")
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    base.alpha_composite(lay)
    return base.convert("RGB")


def render(a):
    photo = Image.open(a.photo).convert("RGB")
    clay = Image.open(a.clay).convert("RGB").resize(photo.size, Image.LANCZOS)
    pv, cv = vcrop(photo, a.cx), vcrop(clay, a.cx)
    flashes = [fill_white(Image.open(p).convert("RGB")) for p in (a.flash or [])]
    font = ImageFont.truetype(FONT, 96)
    t0 = 0.6 * len(flashes)          # 모델 등장 시각
    tw = t0 + 1.4                    # 와이프 시작
    tmp = tempfile.mkdtemp(prefix="reel_")
    try:
        n = int(a.sec * FPS)
        for f in range(n):
            t = f / FPS
            if t < t0:
                im = flashes[int(t / 0.6)]
            else:
                z = 1.0 + 0.06 * (t / a.sec)
                c, p = zoomed(cv, z), zoomed(pv, z)
                k = ease((t - tw) / 1.0)
                xw = int(W * k)
                im = c.copy()
                if xw > 0:
                    im.paste(p.crop((0, 0, xw, H)), (0, 0))
                if 0 < k < 1:
                    ImageDraw.Draw(im).rectangle((xw - 3, 0, xw + 3, H), fill=(255, 255, 255))
                if t < tw:
                    im = put_text(im, a.text1, ease((t - t0 - 0.2) / 0.3) * (1 - ease((t - tw + 0.2) / 0.2)), font)
                else:
                    im = put_text(im, a.text2, ease((t - tw - 1.4) / 0.4), font)
            im.save(os.path.join(tmp, f"{f:04d}.png"))
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-framerate", str(FPS),
                        "-i", os.path.join(tmp, "%04d.png"), "-c:v", "libx264", "-crf", "18", "-preset", "slow",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not os.path.exists(a.out) or os.path.getsize(a.out) < 10000:
        sys.exit("REEL_FAIL 출력 없음")
    print(f"REEL_OK {a.out} {a.sec}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--clay", required=True)
    ap.add_argument("--photo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--flash", nargs="*")
    ap.add_argument("--cx", type=float, default=0.5)
    ap.add_argument("--text1", default="도면만 넣었다")
    ap.add_argument("--text2", default="나머지는 전부 AI")
    ap.add_argument("--sec", type=float, default=9.0)
    render(ap.parse_args())
