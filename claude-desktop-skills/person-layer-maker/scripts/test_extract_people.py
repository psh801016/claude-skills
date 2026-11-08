# extract_people.py 회귀 테스트 — 실제 납품 파일로 돈다(대표 조건). 파일이 없으면 SKIP.
# 배경: 2026-11-05 KOBC 포토존 2일차 — "사람 빵구났다(손에 든 물건 빠짐)", "공중부양", "좌측 문 기움(호모그래피)",
#       사람 박스를 매번 손으로 잡느라 시간이 샘. 이 테스트가 지키는 것:
#   ① --auto-boxes 가 새로 넣은 2명을 찾고 뒤쪽 여자를 behind 로 판정 ② 사람 밖 배경은 그대로(outside_diff<0.05)
#   ③ 부분 아핀 정합 rms<2 ④ check_feet.jpg 확인 시트가 나온다 ⑤ 회색 바지·검은 구두 남성(22_magB 가운데)의 마스크가
#   구두 바닥(y≥1245)까지 내려온다 — '원본과 달라진 곳' 픽셀 게이트가 구두를 카펫으로 봐서 발목에서 잘렸던 사고(2026-11-05 "다리 잘렸다").
#   결과는 임시 폴더에만 쓴다.
import re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).parent
W = Path(r"G:\내 드라이브\AI-작업기록\Claude\2026-11-05_KOBC-로비포토존")
base, cand, occ = W / "23_사람레이어" / "people_final.png", W / "25_magB.png", W / "15_가림.png"
if not all(p.exists() for p in (base, cand, occ)):
    print("SKIP 실제 파일 없음"); sys.exit(0)
with tempfile.TemporaryDirectory() as t:
    r = subprocess.run([sys.executable, str(HERE / "extract_people.py"), "--base", str(base), "--cand", str(cand),
                        "--out-dir", t, "--occluder", str(occ), "--auto-boxes"],
                       capture_output=True, text=True, encoding="utf-8", env={"PYTHONIOENCODING": "utf-8", **__import__("os").environ})
    out = r.stdout
    boxes = [l for l in out.splitlines() if l.startswith("AUTO_BOX")]
    assert len(boxes) == 2, out
    assert sum(":behind" in b for b in boxes) == 1, out
    m = re.search(r"PEOPLE_OK inliers=\d+ rms=([\d.]+) outside_diff=([\d.]+)", out)
    assert m, out
    assert float(m.group(1)) < 2.0 and float(m.group(2)) < 0.05, out
    assert (Path(t) / "check_feet.jpg").exists(), "확인 시트 없음"
# ⑤ 발 잘림 — 1차 합성(배경 15 + 후보 22) 가운데 남성
import numpy as np
from PIL import Image
base2, cand2 = W / "15_배경최종.png", W / "22_magB.png"
if base2.exists() and cand2.exists():
    with tempfile.TemporaryDirectory() as t:
        r = subprocess.run([sys.executable, str(HERE / "extract_people.py"), "--base", str(base2), "--cand", str(cand2),
                            "--out-dir", t, "--occluder", str(occ), "--auto-boxes"],
                           capture_output=True, text=True, encoding="utf-8", env={"PYTHONIOENCODING": "utf-8", **__import__("os").environ})
        assert "PEOPLE_OK" in r.stdout, r.stdout
        m = np.asarray(Image.open(Path(t) / "people_mask.png").convert("L"))[:, 1000:1180] > 127
        feet_y = int(np.where(m.any(1))[0].max())
        assert feet_y >= 1245, f"가운데 남성 마스크가 구두 전에 끝남 feet_y={feet_y}"
# ⑥ 2026-11-06 Kofpi 부스 "왜 매번 사람이 붕 떠 있어, 잘라 붙인 거 같아": 유광 바닥 반사를 버리던 사고 + 한 박스 두 사람 중
#    작은 사람(스태프)을 지우던 사고. 지키는 것: 사람 5명 박스, 스태프 다리(x 900~960, y 1000~1100) 있음, 회색 정장 남성 발밑
#    반사 구역(y 1270~1380, x 540~700)이 원본보다 후보 쪽에 가깝다.
K = W.parent / "2026-11-06_Kofpi-부스배경"
kb, kc, kl = K / "08_최종C_현수막제거.png", K / "11_magA.png", K / "01_부스_알파.png"
if all(p.exists() for p in (kb, kc, kl)):
    with tempfile.TemporaryDirectory() as t:
        r = subprocess.run([sys.executable, str(HERE / "extract_people.py"), "--base", str(kb), "--cand", str(kc),
                            "--out-dir", t, "--auto-boxes", "--lock", str(kl)],
                           capture_output=True, text=True, encoding="utf-8", env={"PYTHONIOENCODING": "utf-8", **__import__("os").environ})
        assert "PEOPLE_OK" in r.stdout and r.stdout.count("AUTO_BOX") >= 5, r.stdout
        pm = np.asarray(Image.open(Path(t) / "people_mask.png").convert("L")) > 127
        assert pm[1000:1100, 900:960].mean() > 0.3, "스태프 다리 없음(한 박스 두 사람 중 작은 사람 지움)"
        out = np.asarray(Image.open(Path(t) / "people_final.png").convert("RGB")).astype(float)
        b0 = np.asarray(Image.open(kb).convert("RGB")).astype(float)
        import cv2
        c0 = cv2.resize(np.asarray(Image.open(kc).convert("RGB")), (b0.shape[1], b0.shape[0])).astype(float)
        z = (slice(1270, 1380), slice(540, 700))
        assert np.abs(out[z] - c0[z]).mean() < np.abs(out[z] - b0[z]).mean(), "발밑 반사가 안 옮겨짐(붕 떠 보임)"
# ⑦ 2026-11-06 "왜 자꾸 블럭을 틀어버려": 카펫(잠금) 위 스태프의 발밑 구역이 카펫 밖까지 뻗어 옛 배경 후보의 몰딩 띠를 다시 붙였다.
#    배경 밑선을 고친 14_배경최종 위에 돌렸을 때, 스태프 앞 카펫 끝 바로 아래(y 1150~1210, x 820~1010, 사람·카펫 밖) 변경이 거의 없어야 한다.
kb2 = K / "14_배경최종.png"
if kb2.exists() and kc.exists() and kl.exists():
    with tempfile.TemporaryDirectory() as t:
        r = subprocess.run([sys.executable, str(HERE / "extract_people.py"), "--base", str(kb2), "--cand", str(kc),
                            "--out-dir", t, "--auto-boxes", "--lock", str(kl)],
                           capture_output=True, text=True, encoding="utf-8", env={"PYTHONIOENCODING": "utf-8", **__import__("os").environ})
        assert "PEOPLE_OK" in r.stdout and r.stdout.count("AUTO_BOX") >= 5, r.stdout
        import cv2
        fin = np.asarray(Image.open(Path(t) / "people_final.png").convert("RGB")).astype(int)
        b2 = np.asarray(Image.open(kb2).convert("RGB")).astype(int)
        pm2 = cv2.dilate((np.asarray(Image.open(Path(t) / "people_mask.png")) > 20).astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool)
        lk = np.asarray(Image.open(kl).resize((b2.shape[1], b2.shape[0]))) > 127
        dd = (np.abs(fin - b2).max(2) > 12) & ~pm2 & ~lk
        n_strip = int(dd[1150:1210, 820:1010].sum())
        assert n_strip < 400, f"카펫 끝 아래 몰딩 띠가 다시 붙음 {n_strip}px"
# ⑧ 2026-11-06 새 배경으로 다시 뽑은 후보(16_magA): 기둥 옆면 세로띠를 사람으로 잡지 않고(박스 폭 ≥ 높이 15%),
#    스태프 그림자가 옆 카운터 인쇄면(x 1224~1430, y 1000~1200)에 번지지 않는다.
kc3 = K / "16_magA.png"
if kb2.exists() and kc3.exists():
    with tempfile.TemporaryDirectory() as t:
        r = subprocess.run([sys.executable, str(HERE / "extract_people.py"), "--base", str(kb2), "--cand", str(kc3),
                            "--out-dir", t, "--auto-boxes", "--lock", str(kl)],
                           capture_output=True, text=True, encoding="utf-8", env={"PYTHONIOENCODING": "utf-8", **__import__("os").environ})
        assert "PEOPLE_OK" in r.stdout, r.stdout
        for ln in r.stdout.splitlines():
            if ln.startswith("AUTO_BOX"):
                x1_, y1_, x2_, y2_ = [int(v) for v in ln.split()[1].split(":")[0].split(",")]
                assert (x2_ - x1_) >= 0.15 * (y2_ - y1_), f"기둥 띠를 사람으로 잡음 {ln}"
        import cv2
        fin = np.asarray(Image.open(Path(t) / "people_final.png").convert("RGB")).astype(int)
        b2 = np.asarray(Image.open(kb2).convert("RGB")).astype(int)
        pm3 = cv2.dilate((np.asarray(Image.open(Path(t) / "people_mask.png")) > 20).astype(np.uint8), np.ones((21, 21), np.uint8)).astype(bool)
        dd = (np.abs(fin - b2).max(2) > 12) & ~pm3
        assert int(dd[1000:1200, 1224:1430].sum()) < 500, f"카운터 인쇄면에 그림자 번짐 {int(dd[1000:1200, 1224:1430].sum())}px"
print("TEST_OK")
