"""일러 없이 도는 회귀 검사 (main-visual-variation).

사고 배경(다른 일러 스킬에서 실제로 터진 것 — 같은 함정을 여기서 미리 잡는다):
- ExtendScript 는 ES3 라 `Array.indexOf` 가 없고, 한 줄 중간 `//` 주석이 뒤 `}` 까지 먹어 'catch without try' 로 안 돌았다 → node 로 문법 검사.
- 겹친 삼항식 `a ? x : b ? y : z` 를 일러가 틀리게 계산했다 → 금지.
- 2026-10-23 충남: 04 백월.ai 가 3D 치수 +100씩(996x264·752x264)이라 목공 불칼질 규칙이 맞는지 sizes.py 가 박아 둔다.
실행: python test_skill.py [jobs.js]
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))   # python -I 로 돌려도 sizes 를 찾게
JSX = sorted(list(HERE.glob("*.jsx")) + list((HERE.parent / "examples").rglob("*.js")) + list((HERE.parent / "examples").rglob("*.jsx")))


def test_syntax():
    node = shutil.which("node")
    if not node:
        print("SKIP 문법 검사: node 없음")
        return
    bad = []
    for f in JSX:
        r = subprocess.run([node, "-e", "new Function(require('fs').readFileSync(process.argv[1],'utf8').replace(/^\\uFEFF/,'').replace(/^#target.*$/m,''))", str(f)],
                           capture_output=True, text=True, encoding="utf-8")
        if r.returncode:
            bad.append(f"{f.name}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else r.returncode}")
    assert not bad, "문법 오류:\n" + "\n".join(bad)
    print(f"OK 문법 {len(JSX)}개")


def test_es3_traps():
    hits = []
    for f in JSX:
        for i, line in enumerate(f.read_text(encoding="utf-8-sig").splitlines(), 1):
            code = line.split("//")[0]
            if re.search(r"\b(sel|parts|names|items|keep|list|arr)\.indexOf\(", code):
                hits.append(f"{f.name}:{i} 배열 indexOf")
            # 괄호 없이 else 자리에 또 삼항식 (`a ? 0 : b ? 1 : 2`) 만 잡는다 — 괄호로 감싼 것·연달아 더한 것은 괜찮다
            if re.search(r"\?[^:;]*:\s*[^;,()\"']*\?", code):
                hits.append(f"{f.name}:{i} 겹친 삼항식")
    assert not hits, "ES3 함정: " + ", ".join(hits)
    print("OK ES3 함정 없음")


def test_raster_effects():
    """새 문서를 만드는 jsx 는 래스터효과 해상도를 300 이상으로 둔다.
    2026-10-27: 기본 72 로 둔 1/10 시트에서 LED 원 둘레 글로우가 실물 7ppi 로 굳어 맵 PNG·_출 렌더에 그대로 갔다(족자봉 굿모닝에서 먼저 발견)."""
    bad = []
    for f in JSX:
        s = f.read_text(encoding="utf-8-sig")
        if "addDocument(" in s:
            m = re.search(r"rasterEffectSettings\.resolution = (\d+)", s)
            if not m or int(m.group(1)) < 300: bad.append(f.name)
    assert not bad, "래스터효과 300 설정 없음: " + ", ".join(bad)
    print("OK 래스터효과 300")


def test_jobs(jobs: Path):
    """jobs.js 의 모든 layout 조각이 PIECES 에 있고, 발주 치수가 sizes.py 규칙과 맞는지.
    + node 로 실제 실행해 문법 오류를 잡는다(2026-11-03 주석이 쉼표를 먹어 일러에서 'Expected: ]' 로 6판 빌드 실패)."""
    src = jobs.read_text(encoding="utf-8-sig")
    node = shutil.which("node")
    if node:
        r = subprocess.run([node, "-e", "global.$={evalFile(){}};global.PHOTOS={};eval(require('fs').readFileSync(process.argv[1],'utf8').replace(/^﻿/,''));if(!JOBS.length)process.exit(2)", str(jobs)],
                           capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0, "jobs.js 실행 오류: " + (r.stderr.strip().splitlines() or ["?"])[0]
    pieces = set(re.findall(r'^\s*"?([가-힣A-Za-z0-9_]+)"?\s*:\s*\{\s*(?:src|region)', src, re.M))
    pieces |= set(re.findall(r'P\("([^"]+)"', src))
    used = set(re.findall(r'piece:\s*"([^"]+)"', src))
    for lst in re.findall(r'pieces:\s*\[([^\]]*)\]', src):
        used |= set(re.findall(r'"([^"]+)"', lst))
    missing = used - pieces
    assert not missing, f"PIECES 에 없는 조각: {sorted(missing)}"
    import sizes
    for m in re.finditer(r'//\s*검산:\s*(\S+)\s+(\d+)\s+(\d+)\s*(\S*)\s*=\s*(\d+)x(\d+)', src):
        method, w, h, fin, W, H = m.groups()
        got = sizes.order_size(method, float(w), float(h), fin or None)
        assert (got[0], got[1]) == (int(W), int(H)), f"검산 불일치 {m.group(0)} → {got}"
    print(f"OK jobs 조각 {len(used)}개 / 검산 {len(re.findall('검산:', src))}건")


if __name__ == "__main__":
    test_syntax()
    test_es3_traps()
    test_raster_effects()
    import sizes
    sizes.test()
    for j in sys.argv[1:] or sorted((HERE.parent / "examples").rglob("jobs.js")):
        test_jobs(Path(j))
    print("전부 통과")
