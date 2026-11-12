"""test_plan2elev.py — plan2elev.py 회귀 테스트.

사고 배경(2026-11-09): 휴플로우 리습(HF2 입면 왁구·HFA 면적표)을 plan.json 위에 옮기며,
(1) 벽 폭·층고가 사각형으로 정확히 서는지 (2) 문은 바닥부터·창은 창대 900부터 뚫리는지
(3) 면적 글자가 ㎡·PY 로 맞게 계산되는지(20㎡ = 6.05PY) 를 잡는다.
실행: python test_plan2elev.py → 마지막 줄 TEST_PLAN2ELEV_OK
"""
import json, os, subprocess, sys, tempfile
import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))

PLAN = {
    "meta": {"unit": "mm"},
    "walls": [
        {"a": [0, 0], "b": [4000, 0], "t": 200, "type": "ext", "h": 2.6},
        {"a": [4000, 0], "b": [4000, 5000], "t": 200, "type": "ext", "h": 2.6},
    ],
    "openings": [
        {"wall": 0, "at": 1000, "w": 900, "kind": "door"},
        {"wall": 1, "at": 1500, "w": 1800, "kind": "window"},
    ],
    "rooms": [{"name": "홀", "poly": [[0, 0], [4000, 0], [4000, 5000], [0, 5000]]}],
}


def main():
    with tempfile.TemporaryDirectory() as td:
        pj = os.path.join(td, "plan.json"); out = os.path.join(td, "elev.dxf")
        json.dump(PLAN, open(pj, "w", encoding="utf-8"), ensure_ascii=False)
        r = subprocess.run([sys.executable, os.path.join(HERE, "plan2elev.py"), pj, "-o", out], capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0, r.stderr
        info = json.loads(r.stdout.strip().splitlines()[-1])
        assert [w["w"] for w in info["walls"]] == [4000, 5000] and info["walls"][0]["h"] == 2600, info
        assert info["rooms"][0]["m2"] == 20.0 and info["rooms"][0]["py"] == 6.05, info

        doc = ezdxf.readfile(out); msp = doc.modelspace()
        elev = [e for e in msp.query("LINE") if e.dxf.layer == "A-ELEV"]
        assert len(elev) == 8, len(elev)  # 벽 2개 × 4변
        opens = [e for e in msp.query("LINE") if e.dxf.layer == "A-ELEV-OPEN"]
        assert len(opens) == 8, len(opens)
        ys = sorted({round(e.dxf.start.y) for e in opens})
        base = min(round(e.dxf.start.y) for e in elev)
        # 문: 바닥(base)~base+2100 · 창: base+900~base+2100
        assert base in ys and base + 900 in ys and base + 2100 in ys, (base, ys)
        xs = sorted({round(e.dxf.start.x) for e in opens})
        assert 1000 in xs and 1900 in xs, xs            # 문 at 1000, w 900
        assert len(msp.query("DIMENSION")) >= 5          # 벽 폭 2 + 개구부 2 + 층고 1 + 총폭 1
        assert len([e for e in msp.query("SOLID") if e.dxf.layer == "A-ELEV-MRK"]) == 3  # 꺾임 ▽ 시작 1 + 벽 끝 2
        texts = [m.text for m in msp.query("MTEXT")]
        assert any("20.00㎡ / 6.05PY" in t for t in texts), texts
        assert any(t == "TOTAL" for t in texts)
    print("TEST_PLAN2ELEV_OK")


if __name__ == "__main__":
    main()
