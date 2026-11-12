# 회귀: 선명형 마무리가 ①헤일로를 줄이고 ②윤곽 폭(선명도)을 유지하고 ③밝기 깜빡임을 줄이며
#       ④소리·길이를 지키는지 (AI 결함을 흉내 낸 합성 클립, 임시 폴더에서만).
# 배경: 2026-11-12 채팅 실측(헤일로 10.1%→1.8%, 윤곽 0.96→0.95px)을 우리 구현으로 재현해 고정.
import os, subprocess, sys, tempfile
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
import sharp_finish as sf

W, H, N = 320, 180, 24


def scene(k):
    f = np.full((H, W), 0.25, np.float32)
    f[:, W // 2:] = 0.75                                      # 수직 명암 경계
    f[:12, :] = 0.75; f[5:7, 20:300] = 0.25                  # 밝은 띠 위 2px 어두운 획(가는 글자)
    f = cv2.GaussianBlur(f, (0, 0), 1.0)
    sharp = f + 1.5 * (f - cv2.GaussianBlur(f, (0, 0), 2.0))   # 과한 언샤프 = 헤일로
    rng = np.random.default_rng(k)
    sharp = sharp + rng.normal(0, 0.01, sharp.shape)          # 프레임마다 끓는 질감
    sharp = sharp * (1 + (0.02 if k % 2 else -0.02))          # 밝기 깜빡임 ±2%
    return np.clip(sharp, 0, 1)


def metrics(frames):
    row = np.mean([f[H // 2 - 20:H // 2 + 20].mean(0) for f in frames], 0)
    lo, hi = row[:W // 2 - 15].mean(), row[W // 2 + 15:].mean()
    over = (row.max() - hi) / (hi - lo)
    t = (row - lo) / (hi - lo)
    c = W // 2
    x10 = next(x for x in range(c - 15, c + 15) if t[x] >= 0.1)
    x90 = next(x for x in range(c - 15, c + 15) if t[x] >= 0.9)
    stroke = np.mean([f[3:9, 30:290].min(0).mean() for f in frames])
    bg = np.mean([f[0:3, 30:290].mean() for f in frames])
    flick = np.std([f.mean() for f in frames]) / np.mean([f.mean() for f in frames])
    return over, x90 - x10, flick, bg - stroke


def read(p):
    cap, out = cv2.VideoCapture(p), []
    while True:
        ok, f = cap.read()
        if not ok:
            return out
        out.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255)


with tempfile.TemporaryDirectory() as d:
    raw, src, out = (os.path.join(d, n) for n in ("raw.yuv", "s.mp4", "o.mp4"))
    with open(raw, "wb") as fh:
        for k in range(N):
            g = (scene(k) * 255 + 0.5).astype(np.uint8)
            fh.write(cv2.cvtColor(g, cv2.COLOR_GRAY2BGR).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "24",
                    "-i", raw, "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-c:v", "libx264", "-crf", "4",
                    "-pix_fmt", "yuv444p", "-c:a", "aac", "-shortest", src], check=True)
    class A: noise = 0.0; dehalo = 0.7; temporal_thr = 0.03; crf = 4
    sf.video(src, out, A)
    o0, w0, f0, s0 = metrics(read(src)); o1, w1, f1, s1 = metrics(read(out))
    print(f"halo {o0:.3f}->{o1:.3f}  edge {w0}->{w1}px  flicker {f0:.4f}->{f1:.4f}  stroke {s0:.3f}->{s1:.3f}")
    assert s1 >= s0 * 0.85, "가는 획 대비가 15% 넘게 줄어듦(글자 얇아짐)"
    assert o1 < o0 * 0.5, "헤일로가 절반 이하로 줄지 않음"
    assert w1 <= w0 + 1, "윤곽이 흐려짐(선명도 손실)"
    assert f1 < f0 * 0.6, "밝기 깜빡임이 줄지 않음"
    pr = lambda p, k: subprocess.run(["ffprobe", "-v", "error", "-show_entries", k, "-of", "csv=p=0", p],
                                     capture_output=True, text=True).stdout.split()
    assert "audio" in pr(out, "stream=codec_type"), "소리 사라짐"
    assert len(read(out)) == N, "프레임 수 바뀜"
    # 사진 경로
    pi, po = os.path.join(d, "a.png"), os.path.join(d, "b.png")
    cv2.imwrite(pi, cv2.cvtColor((scene(0) * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR))
    class B: noise = 0.006; dehalo = 0.7
    sf.still(pi, po, B)
    assert cv2.imread(po).shape == cv2.imread(pi).shape
    assert d.startswith(tempfile.gettempdir())               # 파수꾼: 임시 폴더 밖에 쓰지 않음
print("TEST_OK")
