"""족자봉 스킬 회귀 검사 (일러 없이 돈다).
사고 배경 (2026-10-22 부산 사이버보안 콘퍼런스):
 - 오류 처리기가 열린 문서를 전부 닫게 짜여 있어, 같은 일러에 떠 있던 ASURA님의 저장 안 된 문서를 닫을 뻔했다
   → build.jsx 는 C:/jjb 아래 문서만 닫아야 한다 (closeMine).
 - verify.py 의 레이아웃 상수가 build.jsx 와 다르면 엉뚱한 영역을 비교해 거짓 통과/실패가 난다.
 - 발주표(2900x1200)와 실제 파일(2900x2350)이 달랐다 → 판 비율과 원본 영역 비율이 어긋나면 잡는다.
사용: python -X utf8 test_skill.py [jobs.js 경로]"""
import json, re, subprocess, sys, pathlib
here = pathlib.Path(__file__).parent
jobs_path = sys.argv[1] if len(sys.argv) > 1 else str(here.parent / "examples/busan_2026/jobs.js")
build = (here / "build.jsx").read_text(encoding="utf-8-sig")
verify = (here / "verify.py").read_text(encoding="utf-8")

assert "app.documents[0].close" not in build, "모든 문서를 닫는 코드가 있다 — closeMine() 만 써야 한다"
assert r'indexOf("c:\\jjb\\")' in build, "closeMine 의 C:/jjb 경로 제한이 없다"
# ES3 에 Array.indexOf 없음 — 배열 리터럴 뒤 indexOf 만 잡는다 (lines[0].indexOf 처럼 문자열 indexOf 는 된다)
assert "Array.prototype.indexOf" not in build and not re.search(r"\]\s*\)?\.indexOf\(", re.sub(r"\w+\[\d+\]\.indexOf", "", build)), "ES3 에 Array.indexOf 없음"

b = dict(re.findall(r"\b(M|GAP|LABEL|TITLE) = (\d+) \* MM", build))
v = re.search(r"M, TITLE, LABEL, GAP = (\d+), (\d+), (\d+), (\d+)", verify).groups()
assert (b["M"], b["TITLE"], b["LABEL"], b["GAP"]) == v, f"레이아웃 상수 불일치 build={b} verify={v}"

src = "const fs=require('fs');eval(fs.readFileSync(process.argv[1],'utf8').replace(/^\uFEFF/,''));console.log(JSON.stringify(JOBS))"
jobs = json.loads(subprocess.run(["node", "-e", src, jobs_path], capture_output=True, text=True, encoding="utf-8", check=True).stdout)
bad = []
for j in jobs:
    for p in j["pieces"]:
        for part in p["parts"]:
            d = part["dst"]
            if len(d) == 3 and part.get("rect"):   # 비율 유지 배치: 원본 영역이 판 밖으로 넘치면 안 된다
                h = d[2] * part["rect"][3] / part["rect"][2]
                if d[1] + h > p["H"] + 0.5 or d[0] + d[2] > p["W"] + 0.5: bad.append(f"{j['key']} {p['pos']} 넘침 h={h:.0f}")
            if len(p["parts"]) == 1 and part.get("rect") and len(d) == 3 and d[2] == p["W"]:
                r = part["rect"]
                if abs(r[2] / r[3] - p["W"] / p["H"]) > 0.01: bad.append(f"{j['key']} {p['pos']} 비율 {r[2]}x{r[3]} vs {p['W']}x{p['H']}")
        for op in part.get("pre", []):   # 글줄 다시 배치 op 형식
            if len(op.get("region", [])) != 4 or not (op.get("move") or op.get("scale") or op.get("hide")):
                bad.append(f"{j['key']} {p['pos']} pre op 형식 {op}")
# 겹친 삼항식은 ExtendScript 가 틀리게 계산한다 (2026-10-22 pre 로그에서 TypeError)
code = "\n".join(l.split("//")[0] for l in build.splitlines())
assert not re.search(r"\?[^;:()\n]*:[^;:()\n]*\?", code), "겹친 삼항식이 있다 — if 로 바꿀 것"
assert not bad, "\n".join(bad)

# 색 맞춤 (2026-10-22: 일러 SWOP 변환으로 우리아이티 파랑 ΔE 16.5, 검정이 4도 362% 로 나갈 뻔했다)
sys.path.insert(0, str(here / "color"))
from match import best
assert best((0, 0, 0))[0] == (0, 0, 0, 100), "검정은 K100 이어야 한다"
for rgb in [(242, 97, 34), (40, 56, 116), (29, 77, 159), (11, 125, 224)]:
    c, de = best(rgb)
    assert sum(c) <= 300, f"{rgb} 총 잉크 {sum(c)}%"
    assert de < 3.0, f"{rgb} → {c} ΔE {de:.1f}"
assert "imageColorSpace == ImageColorSpace.RGB) ras.push" in (here / "color/colormatch.jsx").read_text(encoding="utf-8"), "그림은 원본에서 뽑아야 한다"
# 2026-10-27 굿모닝: 새 문서 기본 72ppi 로 빛 고리 글로우가 빠졌다 / 프로필 태그 차이로 verify 가 멀쩡한 판을 떨어뜨렸다
assert re.search(r"rasterEffectSettings\.resolution = (\d+)", build) and int(re.search(r"rasterEffectSettings\.resolution = (\d+)", build).group(1)) >= 300, "래스터효과 해상도 300 고정이 없다"
assert "textFonts.getByName" not in build, "getByName 은 설치 안 된 글꼴도 돌려줘 라벨이 대체 글꼴(가는 글씨)로 찍힌다 — 설치 목록에서 이름으로 찾을 것 (2026-10-28 이글루)"
for name in ("verify.py", "localdiff.py"):
    t = (here / name).read_text(encoding="utf-8")
    assert "set_icc(" in t and "RGB_SRC" in t, f"{name}: CMYK 원본은 프로필 끄고, RGB 원본은 켜고 비교해야 한다"
print(f"OK — {len(jobs)}개사 {sum(len(j['pieces']) for j in jobs)}판")
