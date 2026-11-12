# 선명형 AI 티 제거(블러·그레인으로 가리지 않고 가짜 선명함만 걷어냄). 크레딧 0.
# 인코딩 -bf 0: x264 기본 B프레임(P-B-B-B)은 어두운 AI 클립에서 4프레임마다 밝기가 0.1% 출렁여 깜빡임 지표를 두 배로 올린다(2026-11-12 실측 0.148→0.064).
# 배경: 2026-11-12 사용자 "선명하게 나와야하는것들은?" + vault reference/ai-sharp-clean-deai-method-and-test-2026-11-12
#   (채팅 실측: 헤일로 10.1%→1.8%, 윤곽 폭 유지). 채팅 원본은 전 프레임 메모리 적재·mp4v 손실 출력 → 여기선
#   5프레임 창으로 흘려 처리하고 ffmpeg libx264 로 바로 쓰며 소리를 살린다. 사진(png/jpg)도 3~6단계만 적용.
# 순서: ①밝기 깜빡임 보정(앞뒤 3프레임 평균) ②움직임 적응 시간축 평균(차이 작은 픽셀만 ±2프레임)
#       ③헤일로 클램프(강한 윤곽 주변만, 블러본 국소 최소·최대로 제한) ④하이라이트 롤오프(knee .82, peak .97)
#       ⑤채도 -5% ⑥휘도 센서 노이즈(암부 1.6배)
# 사용: python sharp_finish.py in.mp4 out.mp4 [--noise 0.006] [--dehalo 0.7] [--temporal-thr 0.03]
import argparse, subprocess, json, collections
import numpy as np, cv2

STILL = (".png", ".jpg", ".jpeg", ".webp")


def dehalo(f, s, sig=2.5, win=7, thr=0.35):
    # 큰 명암 경계(블러 σ3 뒤에도 남는 경계)에만 건다 → 2px 가는 획(글자)은 마스크에 안 걸려 얇아지지 않음.
    if s <= 0:
        return f
    g = cv2.GaussianBlur(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (0, 0), 3)
    e = cv2.magnitude(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1))
    m = cv2.dilate((e > thr).astype(np.uint8), np.ones((win, win), np.uint8)).astype(np.float32)
    b = cv2.GaussianBlur(f, (0, 0), sig)
    k = np.ones((win, win), np.uint8)
    c = np.clip(f, cv2.erode(b, k), cv2.dilate(b, k))       # 블러본 범위 밖으로 튄 오버·언더슈트만 자름
    w = (m * s)[..., None]
    return (f * (1 - w) + c * w).astype(np.float32)


def tone(f, sat=0.95, knee=0.82, peak=0.97):
    r = peak - knee
    f = np.where(f > knee, knee + r * (1 - np.exp(-(f - knee) / r)), f)
    hsv = cv2.cvtColor(f.astype(np.float32), cv2.COLOR_BGR2HSV)
    hsv[..., 1] *= sat
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR).astype(np.float32)


def noise(f, amt, rng):
    if amt <= 0:
        return f
    y = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    n = rng.standard_normal(y.shape).astype(np.float32) * amt * (1 + 0.6 * (1 - y))  # 암부 최대 1.6배
    return (f + n[..., None]).astype(np.float32)


def still(src, out, a):
    f = cv2.imread(src).astype(np.float32) / np.float32(255)
    f = noise(tone(dehalo(f, a.dehalo)), a.noise, np.random.default_rng(0))
    cv2.imwrite(out, np.clip(f * 255 + 0.5, 0, 255).astype(np.uint8))


def video(src, out, a):
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                      "stream=width,height,r_frame_rate", "-of", "json", src],
                                     capture_output=True, text=True, check=True).stdout)["streams"][0]
    W, H, fps = info["width"], info["height"], info["r_frame_rate"]
    def frames():
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                             stdout=subprocess.PIPE)
        while True:
            b = p.stdout.read(W * H * 3)
            if len(b) < W * H * 3:
                break
            yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
        p.wait()
    means = np.array([f.mean() for f in frames()]) / 255     # 1패스: 프레임 밝기만
    n = len(means)
    tgt = np.array([means[max(0, i - 3):i + 4].mean() for i in range(n)])
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                            "-r", fps, "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264",
                            "-crf", str(a.crf), "-preset", "slow", "-bf", "0", "-pix_fmt", "yuv420p", "-c:a", "copy",
                            "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    rng = np.random.default_rng(0)
    buf = collections.deque()                                # (번호, 프레임) 최대 5장
    def emit(j):
        f = next(g for i, g in buf if i == j)
        acc, wsum = f.copy(), np.ones(f.shape[:2] + (1,), np.float32)
        for i, g in buf:                                     # ② 움직임 적응 시간축 평균(±2)
            if i != j and abs(i - j) <= 2:
                m = (np.abs(g - f).max(2, keepdims=True) < a.temporal_thr).astype(np.float32)
                acc += g * m; wsum += m
        f = noise(tone(dehalo(acc / wsum, a.dehalo)), a.noise, rng)
        enc.stdin.write(np.clip(f * 255 + 0.5, 0, 255).astype(np.uint8).tobytes())
        while buf and buf[0][0] < j - 1:
            buf.popleft()
    nxt = 0
    for i, f in enumerate(frames()):
        buf.append((i, (f.astype(np.float32) * np.float32(tgt[i] / max(means[i], 1e-4) / 255))))  # ① 밝기 맞춤
        while nxt <= i - 2:
            emit(nxt); nxt += 1
    while nxt < n:
        emit(nxt); nxt += 1
    enc.stdin.close(); enc.wait()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--noise", type=float, default=0.006)
    ap.add_argument("--dehalo", type=float, default=0.7)
    ap.add_argument("--temporal-thr", dest="temporal_thr", type=float, default=0.03)
    ap.add_argument("--crf", type=int, default=16)
    a = ap.parse_args()
    (still if a.src.lower().endswith(STILL) else video)(a.src, a.out, a)
    print("SHARP_FINISH_OK", a.out)
