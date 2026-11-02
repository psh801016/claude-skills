"""excel_to_csv.py — 행사마다 모양이 다른 참가기업 엑셀을 fill_template.jsx 가 먹는 CSV 로 바꾼다.

받는 엑셀 예 (탄소중립 컨퍼런스 참가기업 LIST, 2026-10-15):
  1줄 제목 / 2~3줄 병합 머리글 [NO | 기관명 → 국문·영문 | 백월 디자인 | 컨펌] / 그 아래 데이터.
머리글 줄은 '국문'·'영문'이 같이 있는 줄을 찾아 정하고, 병합 칸은 위 줄 글자까지 합쳐 칸 이름을 본다.
그래서 제목 줄 수·추가 칸·칸 순서가 달라도 된다. 필요한 칸만 뽑고 나머지(백월 디자인·컨펌 등)는 버린다.

  py -3 excel_to_csv.py 참가기업.xlsx                         → 참가기업_간판.csv
  py -3 excel_to_csv.py 참가기업.xlsx --qty A1=2,A12=3        → 부스 2칸·3칸 쓰는 회사는 간판도 2장·3장
  py -3 excel_to_csv.py 참가기업.xlsx --logos "로고폴더"        → 회사명·부스번호로 로고 파일을 찾아 '로고' 칸에
  py -3 excel_to_csv.py 참가기업.xlsx --extra 층               → 틀에 '층' 글자를 추가했을 때 그 칸도 뽑기
엑셀에 수량(부스수) 칸이 있으면 그 값을 쓰고, --qty 가 그 위에 덮어쓴다.
엑셀에 사이즈(규격·크기) 칸이 있으면 '틀' 칸으로 옮긴다 → fill_template.jsx 가 '틀_<사이즈>' 틀을 고른다.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

ALIASES = {
    "부스번호": ["NO", "NO.", "번호", "부스", "부스번호", "부스NO", "BOOTH"],
    "국문": ["국문", "국문명", "기관명(국문)", "국문기관명"],
    "영문": ["영문", "영문명", "기관명(영문)", "영문기관명"],
    "수량": ["수량", "장수", "부스수", "부스개수", "개수", "칸수"],
    "틀": ["틀", "사이즈", "규격", "크기", "간판크기", "간판사이즈"],
    "연번": ["연번", "순번", "순서"],
}
LOGO_EXT = {".ai", ".eps", ".pdf", ".png", ".jpg", ".jpeg", ".psd", ".tif", ".tiff"}


def norm(s):
    return re.sub(r"\s+", "", str(s or "")).upper()


def clean(s):
    return re.sub(r"\s+", " ", str(s if s is not None else "")).strip()   # 칸 안 줄바꿈·겹공백 → 한 칸


def key(s):
    """로고 파일명 대조용: ㈜·(주)·주식회사·기호·공백 제거, 소문자."""
    s = re.sub(r"㈜|\(주\)|주식회사|co\.?,?\s*ltd\.?|inc\.?", "", str(s or ""), flags=re.I)
    return re.sub(r"[^0-9a-z가-힣]", "", s.lower())


def load_grid(path):
    if path.suffix.lower() == ".csv":
        raw = path.read_bytes()
        for enc in ("utf-8-sig", "cp949"):
            try:
                return list(csv.reader(raw.decode(enc).splitlines()))
            except UnicodeDecodeError:
                pass
        sys.exit(f"CSV 인코딩을 읽을 수 없습니다: {path}")
    from openpyxl import load_workbook
    ws = load_workbook(path, data_only=True).active
    grid = [[c.value for c in row] for row in ws.iter_rows()]
    for rng in ws.merged_cells.ranges:                      # 병합 칸은 왼쪽 위 값으로 채운다
        v = grid[rng.min_row - 1][rng.min_col - 1]
        for r in range(rng.min_row - 1, rng.max_row):
            for c in range(rng.min_col - 1, rng.max_col):
                grid[r][c] = v
    return grid


def find_logo(files, no, ko, en):
    keys = {k for k in (key(no), key(ko), key(en)) if k}
    exact = [f for f in files if key(f.stem) in keys]
    if exact:
        return exact
    return [f for f in files if any(len(k) >= 2 and (k in key(f.stem) or key(f.stem) in k) for k in (key(ko), key(en)) if k)]


def convert(path, qty=None, extra=(), logos=None, ju=False):
    qty = qty or {}
    grid = load_grid(Path(path))
    hr = next((i for i, row in enumerate(grid[:20])
               if any(norm(v) in ALIASES["국문"] for v in row) and any(norm(v) in ALIASES["영문"] for v in row)), None)
    if hr is None:
        sys.exit("머리글 줄('국문'·'영문'이 같이 있는 줄)을 앞 20줄에서 못 찾았습니다.")
    width = max(len(r) for r in grid)
    heads = [{norm(grid[r][c]) for r in range(max(0, hr - 2), hr + 1) if c < len(grid[r])} for c in range(width)]
    aliases = dict(ALIASES, **{e: [norm(e)] for e in extra})
    cols = {}
    for field, names in aliases.items():
        hit = [c for c in range(width) if heads[c] & set(names)]
        if hit:
            cols[field] = hit[0]
    need = ["부스번호", "국문", "영문", *extra]
    lost = [f for f in need if f not in cols]
    if lost:
        sys.exit(f"엑셀에서 이 칸을 못 찾았습니다: {', '.join(lost)}  (머리글 줄 {hr + 1})")

    files = [f.resolve() for f in Path(logos).iterdir() if f.suffix.lower() in LOGO_EXT] if logos else []
    head = ["부스번호", "국문", "영문"] + (["틀"] if "틀" in cols else []) + list(extra) + (["로고"] if logos else []) + ["수량"]
    out, seen, notes = [], set(), []
    for row in grid[hr + 1:]:
        row = list(row) + [None] * (width - len(row))
        v = {f: clean(row[c]) for f, c in cols.items()}
        if not (v["국문"] or v["영문"]):
            continue
        if ju:                                             # 요청서 지침 "㈜ 말고 (주)로 통일" (2026-10-15 부산)
            v["국문"] = v["국문"].replace("㈜", "(주)")
        no = v["부스번호"]
        if not no and v.get("연번", "").isdigit():          # 부스번호 칸이 비면 연번을 01 형식으로 (부산 요청서가 그랬다)
            no = f"{int(v['연번']):02d}"
            if not any("연번" in n for n in notes):
                notes.append("부스번호 칸이 비어 연번을 부스번호로 사용 (확정 번호 오면 다시 돌릴 것)")
        if no in seen:
            notes.append(f"부스번호 중복: {no}")
        seen.add(no)
        q = str(qty.get(no, re.sub(r"[^0-9]", "", v.get("수량", "")) or "1"))
        line = [no, v["국문"], v["영문"]] + ([v["틀"]] if "틀" in cols else []) + [v[e] for e in extra]
        if logos:
            hit = find_logo(files, no, v["국문"], v["영문"])
            if len(hit) > 1:
                notes.append(f"{no} 로고 후보 여러 개(첫 번째 사용): {', '.join(h.name for h in hit)}")
            elif not hit:
                notes.append(f"{no} {v['국문']}: 로고 없음 → 로고 없이 만든다")
            line.append(str(hit[0]) if hit else "")
        out.append(line + [q])
    unknown = set(qty) - seen
    if unknown:
        notes.append(f"--qty 에 있는데 엑셀에 없는 번호: {', '.join(sorted(unknown))}")
    return head, out, notes


def parse_qty(s):
    out = {}
    for part in filter(None, (p.strip() for p in s.split(","))):
        no, _, n = part.partition("=")
        if not n.strip().isdigit():
            sys.exit(f"--qty 형식은 A1=2,A12=3 입니다: {part}")
        out[no.strip()] = int(n)
    return out


def trim_logo(src, dst):
    """PNG·JPG 로고의 흰색·투명 여백을 잘라 사본 저장. 일러 스크립트는 그림 테두리 기준으로 맞추기 때문에
    여백이 있으면 로고가 작아진다 (2026-10-15 부산 사이버보안: 안랩 11339px 판은 로고가 가운데 점만 했다)."""
    from PIL import Image
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    px, step, xs, ys = im.load(), max(1, max(w, h) // 1500), [], []
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b, a = px[x, y]
            if a > 20 and min(r, g, b) < 235:
                xs.append(x); ys.append(y)
    if not xs:
        return src
    pad = step * 2
    im.crop((max(0, min(xs) - pad), max(0, min(ys) - pad), min(w, max(xs) + pad + 1), min(h, max(ys) + pad + 1))).save(dst)
    return dst


CMYK_ICC = r"C:\Windows\System32\spool\drivers\color\JapanColor2001Coated.icc"   # 한국판 어도비 기본(Korea General Purpose)


def to_cmyk_tiff(src, dst, icc=CMYK_ICC):
    """로고를 CMYK TIFF 로 (흰 바탕에 합친 뒤 sRGB → Japan Color 2001 Coated, 상대 색도계).
    일러 안에서 바꾸면 안 된다: 메뉴 명령(CMYK로 변환)은 스크립트에서 안 먹었고, 래스터화로 바꾸다 일러가 멈췄다
    (2026-10-15 부산, 메모리 13GB·응답 없음 → ASURA님이 강제 종료). 그래서 일러 밖에서 그림 파일 자체를 바꾼다."""
    from PIL import Image, ImageCms
    im = Image.open(src).convert("RGBA")
    flat = Image.new("RGB", im.size, (255, 255, 255))
    flat.paste(im, mask=im.split()[3])
    srgb = ImageCms.createProfile("sRGB")
    out = ImageCms.profileToProfile(flat, srgb, icc, renderingIntent=1, outputMode="CMYK")
    out.save(dst, compression="tiff_lzw", icc_profile=open(icc, "rb").read(), dpi=(300, 300))
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--qty", default="", help="부스번호=장수, 쉼표로 (예: A1=2,A12=3)")
    ap.add_argument("--logos", help="로고 파일 폴더 (파일명 = 회사명·영문명·부스번호)")
    ap.add_argument("--extra", default="", help="추가로 뽑을 칸 이름, 쉼표로")
    ap.add_argument("--ju", action="store_true", help="국문 ㈜ → (주) 통일")
    ap.add_argument("--cmyk", action="store_true", help="로고를 CMYK TIFF 로 바꿔 넣기 (출력용)")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    extra = [s.strip() for s in a.extra.split(",") if s.strip()]
    head, rows, notes = convert(a.src, parse_qty(a.qty), extra, a.logos, a.ju)
    out = Path(a.out or Path(a.src).with_name(Path(a.src).stem + "_간판.csv"))
    if a.logos:                                            # 래스터 로고는 여백 자른 사본으로 바꿔 넣는다 (원본 불변)
        li, tdir = head.index("로고"), out.parent / "로고_정리"
        for r in rows:
            src = Path(r[li]) if r[li] else None
            if src and src.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                tdir.mkdir(exist_ok=True)
                try:
                    r[li] = str(trim_logo(src, tdir / f"{r[0]}_{src.stem}.png"))
                    if a.cmyk:
                        r[li] = str(to_cmyk_tiff(r[li], tdir / f"{r[0]}_{src.stem}_cmyk.tif"))
                except Exception as e:                     # 못 여는 그림이면 원본 그대로 쓰고 알린다
                    notes.append(f"{r[0]} 로고 여백 자르기 실패({e}) → 원본 사용")
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows([head] + rows)
    print(f"저장: {out}  ({len(rows)}개 부스, 간판 {sum(int(r[-1]) for r in rows)}장)")
    for n in notes:
        print("주의: " + n, file=sys.stderr)


if __name__ == "__main__":
    main()
