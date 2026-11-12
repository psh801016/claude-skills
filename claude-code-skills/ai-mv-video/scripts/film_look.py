# AI 영상 'AI 티' 줄이는 후반 필름룩(ffmpeg 만, 크레딧 0).
# 배경: 2026-11-12 p12 컷 테스트 → 그레인 11 은 하늘에서 거칠어 8 로 낮춰 Velvet Shift 전체 적용.
# 순서 고정: 약한 블러 → 톤 커브(검정 들어올림·하이라이트 눌림) → 채도 -14% → 섀도 청록/하이라이트 웜 → 시간축 그레인.
# 사용: python film_look.py 입력.mp4 출력.mp4 [--grain 8] [--blur 0.6] [--sat 0.86]
# 사진(png/jpg)도 된다: 그레인 기본 4, 색 손실 없이 rgb 로 저장. 실사화·합성 마무리용(아직 사용자 판정 전 — 값 이력은 각 스킬에).
# --clean: 선명해야 하는 결과(전시·제품·글자·요즘 톤 뮤비)용. 블러·톤커브·색틀기 없이 아주 고운 그레인만 깔아
#   합성 부분끼리 노이즈 결만 맞춘다(2026-11-12 사용자 "선명하게 나와야하는것들은?").
import argparse, subprocess


STILL = (".png", ".jpg", ".jpeg", ".webp")


def vf(grain=8, blur=0.6, sat=0.86, pix="yuv420p", clean=False):
    c = max(1, round(grain / 4))
    if clean:
        return f"scale=trunc(iw/2)*2:trunc(ih/2)*2:flags=lanczos,noise=c0s={grain}:c0f=t,format={pix}"
    return (f"scale=trunc(iw/2)*2:trunc(ih/2)*2:flags=lanczos,gblur=sigma={blur},"
            "curves=master='0/0.04 0.25/0.24 0.75/0.74 1/0.95',"
            f"eq=saturation={sat}:contrast=0.97,"
            "colorbalance=rs=-0.03:bs=0.04:rh=0.04:bh=-0.03,"
            f"noise=c0s={grain}:c0f=t:c1s={c}:c1f=t:c2s={c}:c2f=t,format={pix}")


def run(src, out, grain=None, blur=0.6, sat=0.86, crf=16, clean=False):
    if src.lower().endswith(STILL):
        g = (2 if clean else 4) if grain is None else grain
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf(g, blur, sat, "rgb24", clean),
                        "-frames:v", "1", out], check=True)
        return
    grain = (3 if clean else 8) if grain is None else grain
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf(grain, blur, sat, clean=clean),
                    "-c:v", "libx264", "-crf", str(crf), "-preset", "slow", "-bf", "0",
                    "-c:a", "copy", "-movflags", "+faststart", out], check=True)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("src"); a.add_argument("out")
    a.add_argument("--grain", type=float, default=None, help="영상 8, 사진 4")
    a.add_argument("--blur", type=float, default=0.6)
    a.add_argument("--sat", type=float, default=0.86)
    a.add_argument("--crf", type=int, default=16)
    a.add_argument("--clean", action="store_true", help="선명 유지: 블러·색보정 없이 고운 그레인만(영상 3, 사진 2)")
    p = a.parse_args()
    run(p.src, p.out, p.grain, p.blur, p.sat, p.crf, p.clean)
    print("FILM_LOOK_OK", p.out)
