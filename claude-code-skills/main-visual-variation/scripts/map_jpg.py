"""새로 뽑은 맵 jpg 를 기존 jpg 와 같은 픽셀 크기로 맞춰 덮어쓸 파일을 만든다 (main-visual-variation).

사고 배경(2026-10-28 교통문화): 일러 150ppi 내보내기가 기존 텍스처보다 1px 커서 그대로 덮으면
3ds Max UV 가 미세하게 어긋난다. 기존 크기로 LANCZOS 리샘플(1~2px 차이만) 하고 품질 92·150dpi 로 저장.
크기 차이가 2% 를 넘으면 다른 대지를 뽑은 것이니 멈춘다.

  python map_jpg.py <새 jpg 폴더> <기존 jpg 폴더> [<결과 폴더>]   → 결과 폴더(기본: 새 폴더/fit) 에 같은 이름으로
  출력 마지막 줄 MAP_JPG_OK n개  /  MAP_JPG_FAIL 이유
"""
import sys
from pathlib import Path

from PIL import Image


def fit(new_dir: Path, old_dir: Path, out_dir: Path) -> list[str]:
    # 기존 폴더를 못 찾으면 조용히 원래 크기로 저장하던 버그(2026-10-29: bash 경로 /x/... 를 윈도우 파이썬이 못 읽음) → 멈춘다
    if not old_dir.is_dir():
        raise SystemExit(f"MAP_JPG_FAIL 기존 jpg 폴더 없음: {old_dir} (윈도우 경로 X:/… 로 넘길 것)")
    out_dir.mkdir(parents=True, exist_ok=True)
    done, bad = [], []
    for p in sorted(new_dir.glob("*.jpg")):
        old = old_dir / p.name
        im = Image.open(p).convert("RGB")
        if old.is_file():
            ow, oh = Image.open(old).size
            if abs(ow - im.width) / ow > 0.02 or abs(oh - im.height) / oh > 0.02:
                bad.append(f"{p.name}: 새 {im.size} vs 기존 {(ow, oh)} — 2% 넘게 다름(다른 대지?)")
                continue
            if (ow, oh) != im.size:
                im = im.resize((ow, oh), Image.LANCZOS)
        im.save(out_dir / p.name, quality=92, dpi=(150, 150), subsampling=0)
        done.append(p.name)
    if bad:
        raise SystemExit("MAP_JPG_FAIL " + " / ".join(bad))
    return done


def test() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        t = Path(td); (t / "new").mkdir(); (t / "old").mkdir()
        Image.new("RGB", (301, 200), "red").save(t / "new" / "a.jpg")
        Image.new("RGB", (300, 200), "blue").save(t / "old" / "a.jpg")
        Image.new("RGB", (640, 480), "red").save(t / "new" / "b.jpg")      # 기존 없음 → 그대로
        assert fit(t / "new", t / "old", t / "fit") == ["a.jpg", "b.jpg"]
        assert Image.open(t / "fit" / "a.jpg").size == (300, 200)
        assert Image.open(t / "fit" / "b.jpg").size == (640, 480)
        Image.new("RGB", (400, 200), "red").save(t / "new" / "c.jpg")
        Image.new("RGB", (300, 200), "red").save(t / "old" / "c.jpg")
        try:
            fit(t / "new", t / "old", t / "fit"); raise AssertionError("2% 초과를 안 잡음")
        except SystemExit as e:
            assert "MAP_JPG_FAIL" in str(e)
        try:
            fit(t / "new", t / "없는폴더", t / "fit3"); raise AssertionError("없는 기존 폴더를 안 잡음")
        except SystemExit as e:
            assert "기존 jpg 폴더 없음" in str(e)
    print("MAP_JPG_TEST_OK")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--test":
        test(); sys.exit(0)
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    new, old = Path(sys.argv[1]), Path(sys.argv[2])
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else new / "fit"
    names = fit(new, old, out)
    print(f"MAP_JPG_OK {len(names)}개 → {out}")
