# 회귀: 필름룩이 소리를 지우거나 길이를 바꾸지 않는지, 그레인이 실제로 들어가는지 (임시 폴더에서만).
# 배경: 2026-11-12 뮤비 전체 적용 — 소리 유지·길이 동일이 납품 조건.
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from film_look import run, vf

assert "c0s=8" in vf() and "c0s=11" in vf(grain=11), vf()
assert "gblur" not in vf(2, clean=True) and "curves" not in vf(2, clean=True), vf(2, clean=True)  # 선명 모드는 블러·톤 없음


def probe(p, k):
    return subprocess.run(["ffprobe", "-v", "error", "-show_entries", k, "-of", "csv=p=0", p],
                          capture_output=True, text=True, check=True).stdout.split()


with tempfile.TemporaryDirectory() as d:
    src, out = os.path.join(d, "s.mp4"), os.path.join(d, "o.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:size=320x180:rate=24:duration=2",
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=2", "-c:a", "aac", "-shortest", src], check=True)
    run(src, out)
    assert "audio" in probe(out, "stream=codec_type"), "소리 사라짐"
    assert abs(float(probe(out, "format=duration")[0]) - float(probe(src, "format=duration")[0])) < 0.1
    # 단색 회색 입력 → 그레인이 들어가면 화소 편차가 생긴다
    st = subprocess.run(["ffmpeg", "-v", "info", "-i", out, "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YDIF",
                         "-f", "null", "-"], capture_output=True, text=True).stderr
    ydif = [float(l.split("=")[1]) for l in st.splitlines() if "YDIF=" in l]
    assert ydif and max(ydif) > 0.5, ydif  # 프레임 간 그레인 변화
    # 사진: 크기 유지·그레인 들어감(단색 회색 → 표준편차 > 0)
    from PIL import Image, ImageStat
    pi, po = os.path.join(d, "g.png"), os.path.join(d, "g_out.png")
    Image.new("RGB", (64, 48), (128, 128, 128)).save(pi)
    run(pi, po)
    im = Image.open(po)
    assert im.size == (64, 48) and ImageStat.Stat(im.convert("L")).stddev[0] > 0.5, ImageStat.Stat(im.convert("L")).stddev
    assert d.startswith(tempfile.gettempdir())  # 파수꾼: 임시 폴더 밖에 쓰지 않음
print("TEST_OK")
