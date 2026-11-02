"""사진 칸 맞춤 — 원본 사진을 칸 비율로 가운데 자르고 CMYK TIFF(Japan Color 2001 Coated)로 만든다. 일러 없이.

발주는 CMYK, RGB 사진은 일러 기본 변환(미국 SWOP)에 맡기지 않는다 (ASURA님 2026-10-23 "알지비 색상을 cmyk로 맞춰서").
변환은 족자봉 스킬 색 맞춤 도구(colorize.to_cmyk: 상대색도+BPC, 넓은 단색은 원본과 ΔE 최소값)를 그대로 쓴다.
해상도는 실물 기준 최대 PPI(기본 150)까지 줄이기만 하고 키우지 않는다 — 실물 PPI 가 100 미만이면 '저화질' 로 알린다.

실행: python photos.py <spec.json>
spec = {"out": "C:/mvv/src/photos", "ppi": 150,
        "items": [{"key": "c1_1", "src": "<사진 경로>", "w": 540, "h": 700, "fx": 0.5, "fy": 0.5}, ...]}   (w,h = 실물 mm, fx/fy = 자르기 중심 0~1)
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

sys.path.insert(0, r"C:\Users\PSH\.agents\skills\jokjabong-print-fit\scripts\color")
from colorize import to_cmyk, ICC_BYTES   # noqa: E402

Image.MAX_IMAGE_PIXELS = None


def crop_to(im, aspect, fx=0.5, fy=0.5):
    w, h = im.size
    if w / h > aspect:   # 너무 넓다 → 좌우를 자른다
        nw = round(h * aspect); x = round((w - nw) * fx); return im.crop((x, 0, x + nw, h))
    nh = round(w / aspect); y = round((h - nh) * fy); return im.crop((0, y, w, y + nh))


def make(item, out_dir, ppi):
    im = ImageOps.exif_transpose(Image.open(item["src"]))
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", im.size, (255, 255, 255)); im = im.convert("RGBA"); bg.paste(im, mask=im.split()[-1]); im = bg
    im = crop_to(im.convert("RGB"), item["w"] / item["h"], item.get("fx", 0.5), item.get("fy", 0.5))
    real_ppi = im.size[0] / (item["w"] / 25.4)
    if real_ppi > ppi:
        im = im.resize((round(item["w"] / 25.4 * ppi), round(item["h"] / 25.4 * ppi)), Image.LANCZOS)
    eff = im.size[0] / (item["w"] / 25.4)
    c, _ = to_cmyk(im)
    dst = Path(out_dir) / f"{item['key']}.tif"
    c.save(dst, compression="tiff_lzw", icc_profile=ICC_BYTES, dpi=(eff, eff))
    return dst, im.size, eff


def test():
    # 가로 사진을 세로 칸에 넣으면 좌우만 잘리고 비율이 칸과 같아야 한다
    im = Image.new("RGB", (400, 300), (0, 0, 255))
    c = crop_to(im, 0.5)
    assert c.size == (150, 300), c.size
    c = crop_to(im, 2.0)
    assert c.size == (400, 200), c.size
    print("OK photos crop")


if __name__ == "__main__":
    if sys.argv[1:] == ["test"]:
        test(); sys.exit()
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(spec["out"]); out.mkdir(parents=True, exist_ok=True)
    low = []
    for it in spec["items"]:
        dst, size, eff = make(it, out, spec.get("ppi", 150))
        flag = "  ← 저화질" if eff < 100 else ""
        if flag: low.append(it["key"])
        print(f"{it['key']}: {Path(it['src']).name} → {it['w']}x{it['h']}mm {size[0]}x{size[1]}px 실물 {eff:.0f}ppi{flag}")
    # 일러 빌더가 읽을 배치표 — jobs.js 에서 $.evalFile 로 읽어 layout 에 붙인다 (자리 정보를 한 곳에만 둔다)
    steps = [{"img": (out / f"{it['key']}.tif").as_posix(), "at": it["at"], "w": it["w"], "h": it["h"], "name": it["key"]} for it in spec["items"] if "at" in it]
    (out / "photos.js").write_text("var PHOTOS = " + json.dumps(steps, ensure_ascii=False) + ";\n", encoding="utf-8-sig")
    print(f"완료 {len(spec['items'])}장, 저화질 {len(low)}장 {low} → {out / 'photos.js'}")
