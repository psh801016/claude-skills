"""부산 사이버보안 콘퍼런스 부스간판 목록 만들기 (2026-10-15).

요청서 엑셀 → 간판 CSV. 로고는 요청서에 적힌 폴더에서 회사별로 눈으로 대조해 고른 파일(아래 LOGO)을 쓰고,
PNG 는 흰 여백·투명 여백을 잘라 '로고' 폴더에 사본으로 둔다(원본은 건드리지 않는다).
요청서 지침: ㈜ → (주) 통일, 간판 3000x750.
부스번호 = 연번 01~22 (ASURA님 2026-10-15). 간판 크기는 옥타 발주 규격 2930x750 유지(엑셀 3000 대신, ASURA님 지시).
"""
import csv
import re
from pathlib import Path

from openpyxl import load_workbook
from PIL import Image

HERE = Path(__file__).parent
import sys
sys.path.insert(0, r"C:\Users\PSH\.agents\skills\illustrator-data-merge\scripts")
from excel_to_csv import to_cmyk_tiff   # 로고는 CMYK TIFF 로 (ASURA님 "rgb 를 cmyk 로")
BOOTH = ""   # 빈 값이면 연번을 01 형식으로 (ASURA님 2026-10-15 "연번을 01~22로")
TYPO = {"프리이빗에이아이": "프라이빗에이아이", "Jcporp Systme": "Jcorp System"}   # 로고 표기 기준
XLSX = Path(r"Z:\01. 진행중인작업\▶ 06. 2Group_1Part\[11.04-05] 2026 부산 사이버보안 콘퍼런스\01. 실행\05. 디자인\00. 디자인 요청서\[3D] 전시 간판 요청서 1014.xlsx")
EXPO = Path(r"Z:\01. 진행중인작업\▶ 06. 2Group_1Part\[11.04-05] 2026 부산 사이버보안 콘퍼런스\01. 실행\04. 전시")
L, W = EXPO / "99. 홈페이지 업로드용" / "1012", EXPO / "99. 홈페이지 업로드용" / "1012" / "웹용"
SH, JC = EXPO / "02. 전시기업 자료" / "09. 신화씨엔에스", EXPO / "02. 전시기업 자료" / "20. 제이콥시스템, 정원엔시스"

# 연번 → (틀, 로고, 로고2). 같은 로고가 여러 판이면 여백 적고 큰 쪽(웹용)을 골랐다.
LOGO = {
    1: ("", L / "1. 78리서치랩.png", None),
    2: ("", L / "2. 넷코아테크.png", None),
    3: ("", L / "3. 드림시큐리티.png", None),
    4: ("", L / "4. 비테크놀로지.png", None),
    5: ("", W / "05_03.png", None),                              # 소만사 (1012 판은 여백 큼)
    6: ("로고2", SH / "Illumio_Logo_Orange.png", SH / "로고-신화CNS-01.png"),  # CMYK 로 바꾸려고 ai 대신 같은 이름 png   # 비고: 로고 좌우 배치
    7: ("", L / "7. 아이시큐.png", None),
    8: ("", W / "09_02.png", None),                              # 안랩 (1012 판은 11339px 여백)
    9: ("", L / "10. NNSP.png", None),
    10: ("", L / "11. 우리아이티.png", None),                     # 192x43 저해상도
    11: ("", L / "12. 위드네트웍스.png", None),
    12: ("", L / "13. (주)윈스테크넷.png", None),
    13: ("", W / "14_02.png", None),                             # 이글루 (1012 폴더엔 없음)
    14: ("2사", HERE / "로고" / "14_1.png", HERE / "로고" / "14_2.png"),  # 비고: 1부스 2개 기업 반반. 합본 PDF 를 9000px 로 그려 반으로 자름
    15: ("", L / "15. FutureSystems_ci_투명배경.png", None),
    16: ("", L / "16. 굿모닝아이텍.png", None),                   # 190x30 저해상도
    17: ("", L / "17. 넥스원소프트.png", None),                   # 472x75 저해상도
    18: ("", L / "18. 스패로우.png", None),
    19: ("", L / "19. 시큐어레터.png", None),
    20: ("", W / "20_02.png", None),                             # 워터월 (여백 적은 판)
    21: ("", L / "21. PaloAltoNetworks_logo_transparent.png", None),
    22: ("", L / "22. PRIBIT_로고_투명배경.png", None),
    # 2026-10-16 추가 (엑셀 5행, 연번 없음 · 부스번호 04 · 비고: 번호 도형 하늘색 말고 연두색)
    "국제식물검역인증원": ("연두", EXPO / "02. 전시기업 자료" / "22. 국제식물검역인증원" / "국제식물검역인증원_로고_투명_4000px.png", None),
}


def trim(src, dst):
    """흰색·투명 여백을 잘라 PNG 사본으로 저장."""
    im = Image.open(src).convert("RGBA")
    px = im.load()
    w, h = im.size
    xs, ys = [], []
    step = max(1, max(w, h) // 1500)
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b, a = px[x, y]
            if a > 20 and min(r, g, b) < 235:
                xs.append(x); ys.append(y)
    pad = step * 2
    box = (max(0, min(xs) - pad), max(0, min(ys) - pad), min(w, max(xs) + pad + 1), min(h, max(ys) + pad + 1))
    im.crop(box).save(dst)
    return im.size, box


def main():
    ws = load_workbook(XLSX, data_only=True).active
    out_logo = HERE / "로고"; out_logo.mkdir(exist_ok=True)
    rows = [["부스번호", "국문", "영문", "국문2", "영문2", "틀", "로고", "로고2", "수량"]]
    added = []                                                   # 연번 없는 추가 줄 → 기존 22장 뒤에 붙인다
    for r in range(5, ws.max_row + 1):
        no, booth, ko, en, qty = (ws.cell(r, c).value for c in (1, 2, 3, 4, 5))
        if not ko:
            continue
        key = no if isinstance(no, int) else str(ko).strip()
        ko = re.sub(r"\s+", " ", str(ko)).strip().replace("㈜", "(주)")
        en = re.sub(r"\s+", " ", str(en)).strip()
        for wrong, right in TYPO.items():                        # 엑셀 오타 — ASURA님 확인 후 수정 (2026-10-15)
            ko, en = ko.replace(wrong, right), en.replace(wrong, right)
        tpl, l1, l2 = LOGO[key]
        tag = f"{no:02d}" if isinstance(no, int) else "add" + str(len(added) + 1)
        ko2 = en2 = ""
        if tpl == "2사":                                         # "(주)제이콥시스템&(주)정원엔시스" → 반반
            ko, ko2 = [x.strip() for x in ko.split("&", 1)]
            en, en2 = [x.strip() for x in en.split("&", 1)]
        paths = []
        for i, src in enumerate((l1, l2)):
            if src is None:
                paths.append(""); continue
            assert src.exists(), src
            if src.parent == out_logo:                            # 이미 정리해 둔 로고
                paths.append(str(src)); continue
            if src.suffix.lower() == ".png":
                dst = out_logo / f"{tag}_{i + 1}.png"
                size, box = trim(src, dst)
                print(f"{tag} {src.name} {size} → 자름 {box}")
                paths.append(str(dst))
            else:
                paths.append(str(src))                            # 벡터는 그대로 (여백은 일러 스크립트가 걷어냄)
        for i, pth in enumerate(paths):                            # 모든 로고 → CMYK TIFF
            if pth:
                tif = out_logo / f"{tag}_{i + 1}_cmyk.tif"
                to_cmyk_tiff(pth, tif); paths[i] = str(tif)
        line = [str(booth).strip() if booth else (BOOTH or f"{no:02d}"), ko, en, ko2, en2, tpl, paths[0], paths[1], str(qty or 1)]
        (rows if isinstance(no, int) else added).append(line)
    rows += added
    with open(HERE / "부스간판_목록.csv", "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(rows)
    print(len(rows) - 1, "줄 저장")


if __name__ == "__main__":
    main()
