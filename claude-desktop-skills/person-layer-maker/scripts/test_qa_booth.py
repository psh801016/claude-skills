# qa_booth.py 회귀 테스트 — 2026-11-06 Kofpi 부스 하루치 반려판을 검사가 실제로 잡는지.
#   통과해야: 부스1 80_최종(최종 납품), 부스2 60_최종(최종 납품)
#   걸려야:   부스1 73(인쇄물 조각 — 글자 두 겹·상판 물결), 76(카운터 모서리 두 겹), 78(안쪽 남성 머리 덮임 → 키 0.89),
#            63_A(원 생성본 — 글자 틀림·사람 1.05~1.11배), 부스2 56(조각 복원), 58(넓은 사람 마스크)
import subprocess, sys
from pathlib import Path
HERE = Path(__file__).parent
B = Path(r"G:\내 드라이브\AI-작업기록\Claude")
K1, K2 = B / "2026-11-06_Kofpi-부스배경", B / "2026-11-06_Kofpi-부스배경2"
# 2026-11-06 개정: 사람 보존 검사(--cand --plate) 추가 — 80_최종(스태프 다리·남성 다리가 렌더에 덮임)은 이제 걸려야 한다
# 2026-11-06 개정 2: 앞뒤 순서 검사(⑤ --occluder). 87(자동 판정 — 사실상 86 과 동일)도 걸려야 한다.
# 2026-11-06 개정 3: ⑥ 흰 면 얼룩. 97(조명 14px, 얼룩)은 걸리고 99_s120 은 통과.
cases = [(K1, "99_s120.png", "92_사람마스크.png", 0.89885, 715.2, True),
         (K1, "97_최종.png", "92_사람마스크.png", 0.89885, 715.2, False),
         (K1, "91_최종.png", "85_사람마스크.png", 0.89885, 715.2, False),
         (K1, "90_최종.png", "85_사람마스크.png", 0.89885, 715.2, False),   # 지어낸 '옆면' 집기 마스크로 다리 절단 → ④ 사람 덮임
         (K1, "87_최종.png", "85_사람마스크.png", 0.89885, 715.2, False),
         (K1, "86_최종.png", "85_사람마스크.png", 0.89885, 715.2, False),
         (K1, "80_최종.png", "85_사람마스크.png", 0.89885, 715.2, False),
         (K1, "73_최종.png", "85_사람마스크.png", 0.89885, 715.2, False),
         (K1, "76_최종.png", "85_사람마스크.png", 0.89885, 715.2, False),
         (K1, "78_최종.png", "85_사람마스크.png", 0.89885, 715.2, False),
         (K1, "63_A_2560.png", "85_사람마스크.png", 0.89885, 715.2, False),
         (K2, "63_최종.png", "59_사람마스크_딱.png", 0.90338, 720.9, True),
         (K2, "62_최종.png", "59_사람마스크_딱.png", 0.90338, 720.9, False),   # 조명 14px 얼룩
         (K2, "56_최종.png", "59_사람마스크_딱.png", 0.90338, 720.9, False),
         (K2, "58_최종.png", "59_사람마스크_딱.png", 0.90338, 720.9, False)]
ran = 0
for K, img, ppl, k, yh, want in cases:
    if not (K / img).exists() or not (K / ppl).exists(): continue
    r = subprocess.run([sys.executable, str(HERE / "qa_booth.py"), "--img", str(K / img), "--render", str(K / "01_부스_흰배경_2560.png"),
                        "--alpha", str(K / "01_부스_알파.png"), "--people", str(K / ppl), "--k", str(k), "--yh", str(yh)]
                       + (["--cand", str(K / "66_크기.png"), "--plate", str(K / "64_판_정합.png"), "--occluder", str(K / "89_앞집기마스크.png")] if K == K1 else
                          ["--cand", str(K / "50_magR_A_2560.png"), "--plate", str(K / "61_판_정합.png")])
                       + (["--removed", str(K / "98_지운자리.png")] if ppl == "92_사람마스크.png" else []),
                       capture_output=True, text=True, encoding="utf-8", env={"PYTHONIOENCODING": "utf-8", **__import__("os").environ})
    ok = "QA_OK" in r.stdout
    assert ok == want, f"{K.name}/{img}: 기대 {'통과' if want else '걸림'} → {r.stdout.strip()[-200:]}"
    ran += 1
if ran == 0:
    print("SKIP 실제 파일 없음"); sys.exit(0)
print(f"TEST_OK {ran}건")
