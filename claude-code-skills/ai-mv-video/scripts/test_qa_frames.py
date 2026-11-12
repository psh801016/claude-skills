# 회귀: 컷 경계 4시점 계획과 촘촘 계획이 맞는지, 실제 짧은 영상에서 시트가 나오는지 (임시 폴더에서만).
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from qa_frames import plan, sheets
ts, lb = plan(10, 0.5, "0,4,10")
assert len(ts) == 8 and abs(ts[0] - 0.4) < 1e-6 and lb[4].startswith("cut02"), (ts, lb)
ts2, _ = plan(2.0, 0.5, "")
assert ts2 == [0.0, 0.5, 1.0, 1.5], ts2
with tempfile.TemporaryDirectory() as d:
    v = os.path.join(d, "t.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=320x180:rate=24:duration=2", v], check=True)
    assert sheets(v, ts2, ["a", "b", "c", "d"], os.path.join(d, "o"), 320) == 1
    assert os.path.exists(os.path.join(d, "o", "qa_001.jpg"))
    assert d.startswith(tempfile.gettempdir())  # 파수꾼: 임시 폴더 밖에 쓰지 않음
print("TEST_OK")
