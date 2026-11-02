"""make_csv.py — 일러스트레이터 변수(Variables) 패널에 바로 넣을 CSV 를 만든다.

영상(디자이너맘 '일러스트레이터 이미지 자동배치')에서 손으로 하던 두 가지를 대신한다.
  1) 사진마다 '속성 > 보안 > 개체 이름' 경로를 복사해 붙이던 일
  2) 엑셀에서 '@사진 앞에 작은따옴표를 붙여야 하던 함정 (CSV 에 직접 쓰면 필요 없다)

사용:
  py -3 make_csv.py <사진폴더>                         # 사진 파일명 = 이름 으로 명단 생성
  py -3 make_csv.py <사진폴더> --list 명단.csv         # 명단의 '이름' 칸으로 사진을 찾아 붙임
  옵션: --key 이름  --image-col 사진  -o 출력.csv

명단에 있는데 사진이 없으면 목록을 찍고 exit 1 (CSV 는 그 칸을 비운 채 저장된다).
"""
import argparse
import csv
import sys
from pathlib import Path

IMG_EXT = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".psd", ".gif", ".bmp"}
# 일러 2026 은 UTF-8 만 받는다. CP949·UTF-16 은 "The dataset file is invalid" (2026-10-15 실호출).
# BOM 을 붙여야 엑셀로 열어도 한글이 안 깨진다.
OUT_ENCODING = "utf-8-sig"


def read_list(path):
    raw = Path(path).read_bytes()
    for enc in ("utf-8-sig", "cp949"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        sys.exit(f"명단 인코딩을 읽을 수 없습니다: {path}")
    rows = list(csv.reader(text.splitlines()))
    return rows[0], rows[1:]


def odd_ratio(paths, tol=0.02):
    """첫 사진과 가로세로비가 다른 사진. 일러는 새 사진을 '대각선 길이'만 맞춰 넣어서
    비율이 다르면 틀 안에서 빈 곳이 생기거나 잘린다 (2026-10-15 실측)."""
    from PIL import Image
    ratios = [(p, Image.open(p).size) for p in paths]
    base = ratios[0][1][0] / ratios[0][1][1]
    return [p.name for p, (w, h) in ratios if abs(w / h / base - 1) > tol]


def build(img_dir, list_path=None, key="이름", image_col="사진"):
    imgs = {p.stem: p.resolve() for p in sorted(Path(img_dir).iterdir())
            if p.suffix.lower() in IMG_EXT}
    if list_path:
        header, rows = read_list(list_path)
        if key not in header:
            sys.exit(f"명단에 '{key}' 칸이 없습니다. 있는 칸: {header}")
        k = header.index(key)
        # 명단에 이미 @사진 칸이 있으면 덮어쓴다
        header = [h for h in header if h.lstrip("@") != image_col]
    else:
        header, rows, k = [key], [[stem] for stem in imgs], 0
    out, missing = [], []
    for r in rows:
        if not any(c.strip() for c in r):
            continue
        name = r[k].strip()
        p = imgs.get(name)
        if p is None:
            missing.append(name)
        out.append(r[:len(header)] + [str(p) if p else ""])
    return header + ["@" + image_col], out, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("img_dir")
    ap.add_argument("--list")
    ap.add_argument("--key", default="이름")
    ap.add_argument("--image-col", default="사진")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()

    header, rows, missing = build(a.img_dir, a.list, a.key, a.image_col)
    out = Path(a.out or Path(a.img_dir) / "list_ai.csv")
    with open(out, "w", encoding=OUT_ENCODING, newline="") as f:
        csv.writer(f).writerows([header] + rows)
    print(f"저장: {out}  ({len(rows)}행, 칸: {', '.join(header)})")
    used = [Path(r[-1]) for r in rows if r[-1]]
    odd = odd_ratio(used) if used else []
    if odd:
        print(f"주의: 첫 사진과 비율이 다른 사진 {len(odd)}장: 같은 비율로 잘라 두지 않으면 "
              f"카드마다 사진 크기가 달라집니다: {', '.join(odd)}", file=sys.stderr)
    if missing:
        print(f"사진 없음 {len(missing)}건: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
