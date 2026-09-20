"""회귀 테스트 - 검산기가 '조용히 통과'하지 않는지 확인.

배경: 2026-09-15. "GPT한테 평면도 이미지 주고 캐드 그려달라니까 도면이 엉망"이
출발점이었다. 엉망의 정체는 두 가지였다.
  (1) px->mm 축척을 잘못 잡아 전체가 엉뚱한 크기로 나오는데 아무도 안 잡아줌
  (2) 문/창이 벽 밖으로 튀어나가는데 그냥 그려짐
둘 다 '그림은 그려지는데 틀린' 유형이라 눈으로 못 잡는다. 그래서 검산기가
이 둘을 반드시 errors 로 뱉는지만 확인한다.

실행: python test_plan2dxf.py
"""
import json, copy, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan2dxf import validate, shoelace

# 예제는 스킬의 examples/ 에 있다. 어느 폴더에서 돌려도 찾게 한다.
_HERE = os.path.dirname(os.path.abspath(__file__))
for _c in (os.path.join(_HERE, "..", "examples", "apartment-84A-plan.json"),
           os.path.join(_HERE, "sample-84A.json"), "sample-84A.json"):
    if os.path.exists(_c):
        BASE = json.load(open(_c, encoding="utf-8")); break
else:
    raise SystemExit("예제 plan.json 을 찾지 못했습니다")


def prep(plan):
    plan = copy.deepcopy(plan)
    for w in plan["walls"]:
        w.pop("_ops", None)
    for op in plan.get("openings", []):
        plan["walls"][op["wall"]].setdefault("_ops", []).append(op)
    return plan


def test_sample_passes():
    e, w, total = validate(prep(BASE))
    assert not e, e
    assert 75 < total < 90, total


def test_scale_error_is_caught():
    """축척을 2배로 잘못 잡으면(px->mm 계수 오류) 면적이 4배가 되어 걸려야 한다."""
    bad = copy.deepcopy(BASE)
    for wall in bad["walls"]:
        wall["a"] = [c * 2 for c in wall["a"]]
        wall["b"] = [c * 2 for c in wall["b"]]
    for r in bad["rooms"]:
        r["poly"] = [[c * 2 for c in p] for p in r["poly"]]
    for op in bad["openings"]:
        op["at"] *= 2
    e, _, total = validate(prep(bad))
    assert e, "축척 2배 오류를 검산기가 놓쳤다"
    assert any("스케일" in x for x in e), e


def test_opening_outside_wall_is_caught():
    """문이 벽 길이를 벗어나면 걸려야 한다."""
    bad = copy.deepcopy(BASE)
    bad["openings"][6]["at"] = 9000      # 4200mm 짜리 벽인데 9000mm 지점
    e, _, _ = validate(prep(bad))
    assert any("벗어남" in x for x in e), e


def test_selfcheck_area():
    assert abs(shoelace([[0, 0], [1000, 0], [1000, 2000], [0, 2000]]) - 2_000_000) < 1


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
    print("모든 검사 통과")
