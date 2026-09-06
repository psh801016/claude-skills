# -*- coding: utf-8 -*-
r"""order_check 회귀 테스트.

사고 배경 (2026-08-31):
  발주 치수 +10mm 규칙이 사내 문서마다 다르게 적혀 있었다.
  - 옥타정리.pptx  : "미싱선이 있는 사이즈는 +10mm 추가해서 발주"
  - 발주파일만들기.hwp : "높이 2.5 이상이면 2m→1950, 3m→2940 …"
  둘 다 조건을 정확히 안 적어서, 실제 발주파일 3건(19케이스)을 전수 대조해
  '폭 2m이상 + 세로 2480이상 + 상하단 바미싱' 3조건임을 역산했다.
  출력 후에는 되돌릴 수 없는 값이라, 규칙이 조용히 틀어지면 바로 실패하도록 정답지를 박아둔다.

정답지 출처(전부 실제 발주 파일):
  A. C:\psh\발주\발주파일_소이1.pptx                       (무대·게이트)
  B. C:\psh\발주\순환경재페스티벌(공감발주)_0619.pptx        (로비·상생라운지)
  C. X:\…위성활용콘퍼런스…\★발주파일\위성활용컨퍼런스(공감발주).pptx (2D팀 작성)

실행: python test_order_check.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from order_check import order_size, check_row, _finish_kind, parse_width  # noqa: E402

BAR = "현수막 상하단 바미싱"
RND = "현수막 둥글게 양면"

# (출처, 폭m, 세로mm, 마감, 기대가로, 기대세로)
CASES = [
    # ── A. 발주파일_소이1.pptx ────────────────────────────────
    ("A 무대 바닥백월", 3.0, 2480, BAR, 2940, 2480),   # ★ +10
    ("A 무대 날개",     0.5, 2480, BAR,  450, 2480),
    ("A 무대 뒷판",     4.0, 2980, BAR, 3930, 2980),   # ★ +10
    ("A 무대 뒷판날개", 1.0, 2980, BAR,  950, 2980),
    ("A 게이트 간판",   3.0,  750, BAR, 2930,  750),
    ("A 게이트 날개1",  1.0, 3230, BAR,  950, 3230),
    ("A 게이트 날개2",  0.5, 3230, BAR,  450, 3230),
    ("A 게이트 뒷백월", 3.0, 2480, RND, 2930, 2480),   # ★ 둥글게 → +10 없음
    ("A 게이트 타이틀", 1.0, 2480, BAR,  950, 2480),
    ("A 경품 간판",     4.0,  500, BAR, 3920,  500),
    ("A 경품 하단",     4.0, 1000, BAR, 3920, 1000),
    ("A 경품 날개",     0.5, 2480, RND,  450, 2480),
    # ── B. 순환경재페스티벌(공감발주) ─────────────────────────
    ("B 도슨트투어",    2.0,  500, BAR, 1940,  500),
    ("B 안내/등록데스크", 4.0, 500, BAR, 3920,  500),
    ("B 등록데스크 하단", 2.0, 1000, BAR, 1940, 1000),
    ("B 등록데스크 정면", 4.0, 1000, BAR, 3920, 1000),
    ("B 상생라운지 날개", 0.5, 2480, BAR, 450, 2480),
    ("B 상생라운지 정면", 2.0, 2000, RND, 1940, 2000),
    ("B 상생라운지 번호", 3.0,  750, BAR, 2930,  750),
    # ── C. 위성활용콘퍼런스 (2D팀 작성) ───────────────────────
    ("C 중회의장 로비백월", 4.0, 2480, BAR, 3930, 2480),  # ★ +10
    ("C 중회의장 내부백월", 2.0, 2480, BAR, 1950, 2480),  # ★ +10, 2m 직접 확증
    ("C 중회의장 날개",     0.5, 2480, BAR,  450, 2480),
    ("C 울타리",            3.0, 2000, RND, 2930, 2000),
    ("C 부스 간판",         3.0,  750, BAR, 2930,  750),
]


def test_octa_cases():
    bad = []
    for name, w, h, fin, ew, eh in CASES:
        gw, gh, why = order_size(w, h, fin)
        if (gw, gh) != (ew, eh):
            bad.append("%s: %s x %s 나왔는데 %s x %s 여야 함 (%s)"
                       % (name, gw, gh, ew, eh, why))
    assert not bad, "\n".join(bad)
    return len(CASES)


def test_plus10_boundary():
    """경계값 — 셋 중 하나라도 빠지면 +10이 붙으면 안 된다."""
    assert order_size(2.0, 2480, BAR)[0] == 1950      # 3조건 충족
    assert order_size(1.5, 2480, BAR)[0] == 1445      # 폭 미달
    assert order_size(2.0, 2479, BAR)[0] == 1940      # 세로 1mm 미달
    assert order_size(2.0, 2480, RND)[0] == 1940      # 마감 다름


def test_finish_kind():
    assert _finish_kind("현수막 상하단 바미싱") == "bar"
    assert _finish_kind("현수막둥글게양면") == "round"
    assert _finish_kind("현수막 불칼질") == "fire"
    assert _finish_kind("후렉스") == "flex"
    assert _finish_kind("모름") is None


def test_fire_flex_passthrough():
    """불칼질·후렉스는 옥타표를 타지 않고 그대로 통과해야 한다.

    입력값에 여유가 이미 들었는지 알 수 없어 자동으로 더하면 안 된다(이중 여유 사고).
    실제 발주값: 무대백월 2200x4200 불칼질 / 게이트 후렉스 2290x2290.
    """
    w, h, why = order_size(2200, 4200, "현수막 불칼질")
    assert (w, h) == (2200, 4200), (w, h)
    assert "확인" in why
    w, h, _ = order_size(2290, 2290, "후렉스")
    assert (w, h) == (2290, 2290)


def test_double_sided():
    """양면 세로 2배는 '적용할 때만' 켠다.

    실제 파일에 두 관행이 다 있다:
      450 x 4960 둥글게양면  (2480 x 2 = 세로를 2배로 적음)
      2930 x 2480 둥글게양면 2장 (세로 그대로, 수량으로 표현)
    그래서 기본값은 끔.
    """
    assert order_size(0.5, 2480, RND)[1] == 2480
    assert order_size(0.5, 2480, RND, double_sided=True)[1] == 4960


def test_check_row_catches_typo():
    row = {"구역": "무대", "폭": 3.0, "세로": 2480,
           "마감": BAR, "적힌가로": "2930"}      # 2940 이어야 하는데 2930 으로 적음
    res = check_row(row)
    assert not res["ok"]
    assert "2940" in res["문제"][0]


def test_parse_width_from_jsx_labels():
    """order_label.jsx 가 내보내는 폭 라벨을 그대로 먹어야 한다."""
    assert parse_width("3m") == 3.0
    assert parse_width("2m(+10)") == 2.0
    assert parse_width("0.5m") == 0.5
    assert parse_width(1.5) == 1.5
    # jsx CSV 한 줄이 그대로 통과하는지
    row = {"구역": "Artboard 1", "폭": "3m(+10)", "세로": 2480,
           "마감": BAR, "적힌가로": "2940", "적힌세로": "2480"}
    assert check_row(row)["ok"]


def test_unknown_width_is_loud():
    try:
        order_size(3.5, 2480, BAR)
    except ValueError as e:
        assert "3.5" in str(e)
    else:
        raise AssertionError("표에 없는 폭인데 조용히 통과했다")


if __name__ == "__main__":
    n = test_octa_cases()
    test_plus10_boundary()
    test_finish_kind()
    test_fire_flex_passthrough()
    test_double_sided()
    test_check_row_catches_typo()
    test_parse_width_from_jsx_labels()
    test_unknown_width_is_loud()
    print("OK — 실제 발주 %d케이스 + 경계·예외 6종 전부 통과" % n)
