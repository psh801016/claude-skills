# 영상 검수용 프레임 시트 — 생성 직후(촘촘) / 편집 뒤(컷별 4시점) 둘 다 이걸로 본다.
# 사고 배경(2026-11-11 Velvet Shift MV): 썸네일 4장만 보고 넘겨 손 좌우·성별·저지 번호·드론·기중기를
#   사용자가 먼저 발견. 0.5초 간격 + 960px 이상으로 봐야 잡힌다.
# 사용: python qa_frames.py <video> <out_dir> [--step 0.5] [--width 960] [--cuts "0,3.5,6.95,..."]
#   --cuts 를 주면 컷마다 10/37/63/90% 4시점, 없으면 step 간격 전체.
# 성공 토큰: QA_FRAMES_OK <시트 수>
import argparse, os, subprocess, json
from PIL import Image, ImageDraw

def dur(v):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", v],
                       capture_output=True, text=True, check=True).stdout
    return float(json.loads(o)["format"]["duration"])

def grab(v, t, w, tmp):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % t, "-i", v, "-frames:v", "1",
                    "-vf", "scale=%d:-2" % w, tmp], check=True)
    return Image.open(tmp).convert("RGB")

def sheets(v, times, labels, out, w, per=4):
    os.makedirs(out, exist_ok=True)
    tmp = os.path.join(out, "_f.png"); n = 0
    for k in range(0, len(times), per):
        ims = []
        for t, lb in zip(times[k:k + per], labels[k:k + per]):
            im = grab(v, t, w, tmp); ImageDraw.Draw(im).text((8, 8), lb, fill=(255, 255, 0)); ims.append(im)
        cw, ch = ims[0].size; cols = 2
        sh = Image.new("RGB", (cw * cols, ch * ((len(ims) + 1) // cols)))
        for i, im in enumerate(ims): sh.paste(im, ((i % cols) * cw, (i // cols) * ch))
        n += 1; sh.save(os.path.join(out, "qa_%03d.jpg" % n), quality=85)
    os.remove(tmp)
    return n

def plan(d, step, cuts):
    if cuts:
        b = [float(x) for x in cuts.split(",")]
        ts, lb = [], []
        for i in range(len(b) - 1):
            for f in (0.1, 0.37, 0.63, 0.9):
                t = b[i] + (b[i + 1] - b[i]) * f; ts.append(t); lb.append("cut%02d %.2fs" % (i + 1, t))
        return ts, lb
    ts = [round(i * step, 3) for i in range(int(d / step)) if i * step < d - 0.05]
    return ts, ["%.2fs" % t for t in ts]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("out")
    ap.add_argument("--step", type=float, default=0.5); ap.add_argument("--width", type=int, default=960)
    ap.add_argument("--cuts", default="")
    a = ap.parse_args()
    ts, lb = plan(dur(a.video), a.step, a.cuts)
    print("QA_FRAMES_OK", sheets(a.video, ts, lb, a.out, a.width))
