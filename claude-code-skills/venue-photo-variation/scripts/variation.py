# 현장사진 바레이션 — GPT(codex exec) 로 클린 플레이트 / 재실사화 이미지를 만든다.
# 배경: 2026-10-27 연회장 사진 집기 제거 + 정면 투시 작업을 매번 손으로 프롬프트 쓰던 것을 고정.
#       codex 가 출력 경로를 추측해 저장하므로 경로를 프롬프트에 박고, 파일·해상도를 실측해야 성공으로 본다.
# 사용:
#   python variation.py plate   --src 원본.jpg --out 결과.png [--view front|keep] [--keep "꽃장식"] [--extra "..."]
#   python variation.py realize --src 합성본.png [--plate 클린플레이트.png] --out 결과.png [--extra "..."]
# 성공 토큰: VARIATION_OK <경로> <가로>x<세로>   실패: VARIATION_FAIL <사유> (exit 1)
import argparse, re, shutil, subprocess, sys
from pathlib import Path

def latest_best_model():
    """2026-11-09 사용자 "지피티 항상 최신 최고로": 이름을 박지 않고 codex 모델 캐시의 1순위(최신 세대 최고)를 쓴다."""
    import json
    try:
        d = json.loads((Path.home() / ".codex" / "models_cache.json").read_text(encoding="utf-8"))
        ms = d.get("models", d) if isinstance(d, dict) else d
        return min(ms, key=lambda m: int(m.get("priority", 99)))["slug"]
    except Exception:
        return "gpt-6.1-sol"


MODEL = latest_best_model()

REMOVE = ("every table and tablecloth, every chair and chair cover, pianos, music stands, podiums/lecterns, "
          "flags, flower stands and flower arches, sound desks, sofas, carts, banners, easels, cables and any "
          "loose items on the floor or stage")

KEEP = ("all architecture and fixed equipment: ceiling shape, ceiling panels and fabric swags, chandeliers, "
        "downlights, lighting trusses and moving lights, projector boxes, screens (blank), curtains, stage and "
        "its steps, speakers, wall panels, mouldings, wainscot, sconces, doors and exit signs, floor/carpet pattern")

VIEW = {
    "front": ("Move the camera sideways onto the center axis of the stage (or main wall), looking straight at it, "
              "eye height about 1.6 m, lens level, a wide view showing the whole stage, side walls and ceiling. Strict one-point perspective: all vertical lines "
              "vertical, frontal horizontals horizontal, single vanishing point at the center."),
    # 2026-11-11 "카메라 각도도 틀리지 않냐, 내 껀 너무 정적인데" — 전시부스 히어로 컷(@ralphgalhardo_arquiteto 최근작) 구도
    "corner": ("Move the camera to a dynamic three-quarter position: about 35-45 degrees off the stage (or main wall) axis, "
               "slightly below eye level, close with a wide view, lens level so all vertical lines stay vertical. Two-point perspective: "
               "the main wall and one side wall recede diagonally across the frame, the polished floor fills the lower third as leading lines."),
    "keep": ("Same camera position, angle, field of view and framing as the photo, with vertical lines "
             "made perfectly vertical."),
}


def plate_prompt(a, out):
    keep = KEEP + (f", and also keep: {a.keep}" if a.keep else "")
    rm = REMOVE
    if getattr(a, "remove", None):  # 2026-11-09 "스크린 제거해": KEEP 의 'screens (blank)' 와 부딪히지 않게 빼고 REMOVE 에 더한다
        if "screen" in a.remove.lower(): keep = keep.replace("screens (blank), ", "")
        rm = REMOVE + f", and also: {a.remove} (show the wall surface behind them, continuing the same wall panels)"
    return f"""Edit the attached photo. Output ONE photorealistic image, 16:9 landscape, 2560x1440.
GOAL: an EMPTY venue as a clean background plate for 3D compositing.
CAMERA: {VIEW[a.view]}
REMOVE completely and fill with the floor/wall/stage behind them (same pattern, same lighting): {rm}.
KEEP EXACTLY (same design, materials, colors, positions - do not redesign): {keep}.
Same light color and exposure as the photo. Real photograph look.
The room contains only the kept elements above, empty and clean.
{a.extra or ''}
Save the final image as PNG to exactly this path: {out}"""


def realize_prompt(a, out):
    # interior-prompt-maker 규칙: 초점거리 숫자 금지, 부정문 금지(GPT 는 부정어를 그린다), 2영역(ZONE A 잠금 / ZONE B 실사화)
    ref = (" Image 2 = the same venue as a clean real photograph (reference for light, color and material response only)."
           if a.plate else "")
    return f"""Image 1 = composite: 3D-rendered event objects placed onto a real photograph of a venue.{ref}
Turn Image 1 into ONE believable on-location event photograph of that venue, 16:9, 2560x1440.
Apply a strict two-zone transformation.
ZONE A stays registered one-to-one with Image 1: identical camera, field of view, framing, horizon and vanishing point, the four corners and edges of every screen, panel and banner, every object's position, size and outline, and all typography, logos, flags and artwork exactly as in Image 1. The venue architecture, ceiling, chandeliers, lighting rigs, walls, doors and carpet keep their exact photographed look from Image 1.
ZONE B is only the 3D-rendered objects' surface response: actively convert their synthetic CGI shading into real photographed behavior. Any tablecloths become real heavy polyester banquet cloth with soft vertical drape folds reaching the carpet and a gentle satin sheen; any chair covers become stretched spandex banquet covers with fabric tension and soft seat creases, same color as Image 1. Each table and chair has grounded soft contact shadows and ambient occlusion on the patterned carpet, matching the venue's warm overhead light direction. Printed banners read as matte tensioned PVC flex with a faint broad light falloff. Every LED screen is emissive: brighter than its surroundings, a fine pixel grid visible up close, its colors casting soft localized blue light onto the stage floor and the immediately adjacent surfaces. Overall color temperature, exposure, sensor noise and slight lens softness of the 3D objects match the photographed venue so everything reads as one camera exposure.
The object set is exactly the set in Image 1.
{a.extra or ''}
Save the final image as PNG to exactly this path: {out}"""


def rebg_prompt(a, out):
    # 2026-11-05 KOBC 로비 등록데스크: 3D 렌더(가짜 석재 배경)의 구도·물건은 그대로, 배경만 실제 현장(참고 사진)으로 바꾼다.
    n = len(a.refs or [])
    refs = f" Images 2 to {n + 1} = real photographs of the actual venue where these objects will stand (reference for architecture, materials, colors and light)." if n else ""
    return f"""Image 1 = a 3D render of event objects (the foreground objects) standing in a placeholder environment.{refs}
Create ONE believable on-location event photograph, 16:9, 2560x1440, at exactly the camera, framing, horizon, vanishing points and lens of Image 1.
The foreground objects of Image 1 stay registered one-to-one: identical position, size, outline, edges, all typography, logos and artwork, as in Image 1.
Everything around them becomes the real venue from the reference photographs, rebuilt in Image 1's perspective: its wall finishes, ceiling, light fixtures, floor finish and color, at true real-world scale relative to the objects.
{a.extra or ''}
The objects sit on the real floor with soft grounded contact shadows and ambient occlusion, lit by the venue's own light; their printed panels read as matte printed graphics with a faint broad light falloff. Color temperature, exposure, sensor noise and slight lens softness are one camera exposure across the whole frame.
Save the final image as PNG to exactly this path: {out}"""


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # 콘솔 cp949 에서 한글 토큰 깨짐 방지
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["plate", "realize", "rebg"])
    p.add_argument("--src", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--plate")
    p.add_argument("--view", choices=list(VIEW), default="front")
    p.add_argument("--keep"); p.add_argument("--remove", help="추가로 지울 것(영문). screen 이 들어가면 KEEP 의 스크린 항목을 뺀다")
    p.add_argument("--extra")
    p.add_argument("--refs", nargs="*", help="rebg: 실제 현장 참고 사진들")
    a = p.parse_args()

    src, out = Path(a.src).resolve(), Path(a.out).resolve()
    imgs = [src]
    if a.mode == "realize":
        if a.plate:  # 2026-10-28: 클린 플레이트 없이 3D 합성본만 오는 컷도 있다
            imgs.append(Path(a.plate).resolve())
    if a.mode == "rebg":
        imgs += [Path(r).resolve() for r in (a.refs or [])]
    for i in imgs:
        if not i.exists():
            print(f"VARIATION_FAIL 입력 없음: {i}"); sys.exit(1)
    if out.exists():
        print(f"VARIATION_FAIL 출력이 이미 있음(덮어쓰기 금지): {out}"); sys.exit(1)
    out.parent.mkdir(parents=True, exist_ok=True)

    prompt = {"plate": plate_prompt, "realize": realize_prompt, "rebg": rebg_prompt}[a.mode](a, out)
    out.with_suffix(".prompt.txt").write_text(prompt, encoding="utf-8")
    cmd = ["codex", "exec", "-m", MODEL, "--skip-git-repo-check"]
    for i in imgs:
        cmd += ["-i", str(i)]
    cmd.append("-")
    r = subprocess.run(cmd, input=prompt, text=True, encoding="utf-8", capture_output=True, shell=sys.platform == "win32")
    log = (r.stdout or "") + (r.stderr or "")
    out.with_suffix(".log.txt").write_text(log, encoding="utf-8")
    if not out.exists():
        # 2026-10-27: codex 셸이 안 떠(helper_unknown_error) 생성은 됐는데 저장 실패 → 세션 폴더에서 직접 회수
        m = re.search(r"session id:\s*([0-9a-f-]+)", log)
        d = Path.home() / ".codex" / "generated_images" / (m.group(1) if m else "_none_")
        pngs = sorted(d.glob("*.png"), key=lambda f: f.stat().st_mtime) if d.exists() else []
        if pngs:
            shutil.copy2(pngs[-1], out)
            print(f"회수: codex 저장 실패 → {pngs[-1]} (후보 {len(pngs)}장 중 마지막)")
    if not out.exists():
        print(f"VARIATION_FAIL codex exit={r.returncode}, 출력 없음 — 로그: {out.with_suffix('.log.txt')}"); sys.exit(1)
    from PIL import Image
    w, h = Image.open(out).size
    if (w, h) != (2560, 1440):  # 2026-11-09: 저장 실패 회수본이 엔진 원본 1672x941 그대로 OK 로 나갔다 → 납품 규격으로 맞춘다
        from PIL import ImageFilter
        Image.open(out).convert("RGB").resize((2560, 1440), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 40, 2)).save(out)
        print(f"크기 보정: {w}x{h} → 2560x1440"); w, h = 2560, 1440
    print(f"VARIATION_OK {out} {w}x{h}")


if __name__ == "__main__":
    main()
