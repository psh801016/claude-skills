# 현장사진 바레이션 — GPT(codex exec) 로 클린 플레이트 / 재실사화 이미지를 만든다.
# 배경: 2026-10-27 연회장 사진 집기 제거 + 정면 투시 작업을 매번 손으로 프롬프트 쓰던 것을 고정.
#       codex 가 출력 경로를 추측해 저장하므로 경로를 프롬프트에 박고, 파일·해상도를 실측해야 성공으로 본다.
# 사용:
#   python variation.py plate   --src 원본.jpg --out 결과.png [--view front|keep] [--keep "꽃장식"] [--extra "..."]
#   python variation.py realize --src 합성본.png [--plate 클린플레이트.png] --out 결과.png [--extra "..."]
# 성공 토큰: VARIATION_OK <경로> <가로>x<세로>   실패: VARIATION_FAIL <사유> (exit 1)
import argparse, re, shutil, subprocess, sys
from pathlib import Path

MODEL = "gpt-6-sol"  # 이미지 = 최고 등급 바로 아래 (rules.md AI 일 분배)

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
    "keep": ("Same camera position, angle, field of view and framing as the photo, with vertical lines "
             "made perfectly vertical."),
}


def plate_prompt(a, out):
    keep = KEEP + (f", and also keep: {a.keep}" if a.keep else "")
    return f"""Edit the attached photo. Output ONE photorealistic image, 16:9 landscape, 2560x1440.
GOAL: an EMPTY venue as a clean background plate for 3D compositing.
CAMERA: {VIEW[a.view]}
REMOVE completely and fill with the floor/wall/stage behind them (same pattern, same lighting): {REMOVE}.
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


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # 콘솔 cp949 에서 한글 토큰 깨짐 방지
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["plate", "realize"])
    p.add_argument("--src", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--plate")
    p.add_argument("--view", choices=list(VIEW), default="front")
    p.add_argument("--keep")
    p.add_argument("--extra")
    a = p.parse_args()

    src, out = Path(a.src).resolve(), Path(a.out).resolve()
    imgs = [src]
    if a.mode == "realize":
        if a.plate:  # 2026-10-28: 클린 플레이트 없이 3D 합성본만 오는 컷도 있다
            imgs.append(Path(a.plate).resolve())
    for i in imgs:
        if not i.exists():
            print(f"VARIATION_FAIL 입력 없음: {i}"); sys.exit(1)
    if out.exists():
        print(f"VARIATION_FAIL 출력이 이미 있음(덮어쓰기 금지): {out}"); sys.exit(1)
    out.parent.mkdir(parents=True, exist_ok=True)

    prompt = (plate_prompt if a.mode == "plate" else realize_prompt)(a, out)
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
    print(f"VARIATION_OK {out} {w}x{h}")


if __name__ == "__main__":
    main()
