# 공간 만들기 한 명령: 3D 렌더(물건만, 알파) + 현장 사진 → 렌더 카메라에 맞는 실제 공간 배경 합성본.
# 2026-11-06 사용자 "공간 만드는거 업그레이드 시켜" — 로비 등록데스크·포토존에서 손으로 이은 절차를 묶었다:
#   ① 렌더 알파 → 물건 마스크·흰 배경 2560  ② space_underlay(소실점 RANSAC 자동, 앞 모서리 자동, 벽 방향 자동)
#   ③ variation.py rebg 를 N 장 병렬(GEOMETRY LOCK)  ④ restore_objects(물건 원본 픽셀)  ⑤ check_vp
#   ⑥ VP_OK 중 소실점 오차·정합 오차가 가장 작은 1장을 --final 로. 하나도 통과 못 하면 SPACE_FAIL(납품 금지).
# 사용:
#   python space_rebg.py --render 렌더.png(알파) --refs 현장1.jpg [현장2.jpg] --height-m 2.0 --wall-gap 2.2
#       --materials "<벽·바닥·천장 마감(긍정문, 사진에 있는 것만)>" --work 작업폴더 --final 결과.png [--n 2]
#       [--soffit 2.9,1.8 --ceil 4.0 --tile ashlar|bond --portal s0,s1,h]
#   --wall-gap: 물건 앞 모서리에서 벽까지(m). 사람이 뒤에 앉는 데스크 ≥2.0(점검표 11), 포토월 ≈ 깊이+0.5~1
# 성공 토큰: SPACE_OK <final> vp=<deg> rms=<px>
import argparse, re, shutil, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).parent
PY = sys.executable

LOCK = ("GEOMETRY LOCK: Image 1 already contains the exact room geometry drawn as a simple placeholder model. Keep every wall edge, "
        "wall base line, tile course, ceiling line, soffit edge, floor tile joint and opening at exactly the same pixel position and angle, "
        "all converging to the same vanishing points as the objects. Only turn the placeholder surfaces into the real finishes of Image 2. ")
REAL = ("Keep the room, the camera and every object's shape exactly. Make the event structures read as real built objects photographed on site: "
        "stretched printed fabric lightbox panels with a faint broad light falloff, brushed aluminium frame edges with small highlights, real soft "
        "contact shadows and ambient occlusion where every base meets the floor, soft blurred reflections of the panels and carpet on the polished "
        "floor, screens glowing slightly. One camera exposure with fine sensor grain.")
TAIL = (" Bright neutral venue light, soft contact shadows under the objects, one photographic exposure. "
        "The objects' own graphics are the only readable text.")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", required=True); ap.add_argument("--refs", nargs="+", required=True)
    ap.add_argument("--height-m", type=float, required=True); ap.add_argument("--wall-gap", type=float, required=True)
    ap.add_argument("--materials", required=True); ap.add_argument("--work", required=True); ap.add_argument("--final", required=True)
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--soffit", default=""); ap.add_argument("--ceil", type=float, default=3.4)
    ap.add_argument("--tile", default="bond"); ap.add_argument("--portal", default="")
    ap.add_argument("--realize", action="store_true", help="배경을 맞춘 뒤 재실사화(조명 감쇠·접지 그림자·바닥 반사만, 글자·형태·배경은 원본)")
    a = ap.parse_args()
    wk = Path(a.work); wk.mkdir(parents=True, exist_ok=True)

    # ① 마스크·흰 배경
    r = Image.open(a.render).convert("RGBA").resize((2560, 1440), Image.LANCZOS)
    if np.asarray(r)[..., 3].min() > 200:
        print("SPACE_FAIL 렌더에 투명 배경(알파)이 없다 — 물건만 알파로 렌더해 달라고 요청"); sys.exit(1)
    mask, white, ul = wk / "sp_mask.png", wk / "sp_render.png", wk / "sp_underlay.png"
    Image.fromarray(((np.asarray(r)[..., 3] > 127) * 255).astype(np.uint8)).save(mask)
    bg = Image.new("RGB", r.size, (255, 255, 255)); bg.paste(r, mask=r.split()[3]); bg.save(white)

    # ② 밑그림
    cmd = [PY, str(HERE / "space_underlay.py"), "--render", str(white), "--mask", str(mask), "--anchor-m", str(a.height_m),
           "--wall-gap", str(a.wall_gap), "--ceil", str(a.ceil), "--tile", a.tile, "--out", str(ul)]
    if a.soffit: cmd += ["--soffit", a.soffit]
    if a.portal: cmd += [f"--portal={a.portal}"]
    rc, out = run(cmd); print(out)
    if rc or "UNDERLAY_OK" not in out: print("SPACE_FAIL 밑그림"); sys.exit(1)
    rc, out = run([PY, str(HERE / "check_vp.py"), "--img", str(ul), "--obj-mask", str(mask)]); print("밑그림", out)
    if not out.startswith("VP_OK"): print("SPACE_FAIL 밑그림 소실점부터 틀림 — 렌더 직선 부족, --vp-left/right 수동 필요"); sys.exit(1)

    # ③ rebg N 장 병렬
    extra = LOCK + a.materials + TAIL
    procs = []
    for i in range(a.n):
        (wk / f"c{i}").mkdir(exist_ok=True)   # 2026-11-06: 같은 폴더면 저장 실패한 codex 가 옆 후보의 결과 파일을 자기 것으로 냈다(rms 0.0)
        cand = wk / f"c{i}" / f"sp_cand_{i}.png"
        if cand.exists(): cand.unlink()
        procs.append((cand, subprocess.Popen([PY, str(HERE / "variation.py"), "rebg", "--src", str(ul), "--refs", *a.refs,
                                              "--out", str(cand), "--extra", extra],
                                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")))
    # ④⑤ 복원·검사
    best = None
    for i, (cand, p) in enumerate(procs):
        log = p.communicate()[0]
        if not cand.exists(): print(f"후보{i} 생성 실패: {log.strip().splitlines()[-1:]}"); continue
        fin = wk / f"sp_final_{i}.png"
        if fin.exists(): fin.unlink()
        rc, out = run([PY, str(HERE / "restore_objects.py"), "--src", str(white), "--cand", str(cand), "--obj-mask", str(mask), "--out", str(fin)])
        m = re.search(r"rms=([\d.]+)", out); rms = float(m.group(1)) if m else 99
        rc2, vo = run([PY, str(HERE / "check_vp.py"), "--img", str(fin), "--obj-mask", str(mask)])
        md = re.search(r"median_miss=([\d.]+)", vo); deg = float(md.group(1)) if md else 99
        print(f"후보{i}: rms={rms} vp={deg}° {vo.split()[0]}")
        if rms < 0.05:
            print(f"후보{i} 반려: 정합 오차 0 — 다른 결과 파일의 복사본"); continue
        if rc == 0 and vo.startswith("VP_OK") and rms <= 1.5:
            score = deg + 0.3 * rms
            if best is None or score < best[0]: best = (score, fin, deg, rms)
    if best is None:
        print("SPACE_FAIL 통과 후보 없음 — --n 을 늘려 다시, 또는 재질 문구 단순화"); sys.exit(1)
    out_img = best[1]
    if a.realize:  # 2026-11-06 사용자 "다 실사화까지 해서 주는 거지?" — 렌더 픽셀 그대로면 CG 티가 남는다
        rc_, rv = run([PY, str(HERE / "variation.py"), "realize", "--src", str(out_img), "--out", str(wk / "sp_real_cand.png"), "--extra", REAL])
        if not (wk / "sp_real_cand.png").exists():
            print("SPACE_FAIL 실사화 후보 생성 실패", rv.splitlines()[-1:]); sys.exit(1)
        m = np.asarray(Image.open(mask)) > 127
        bots = [np.where(m[:, x])[0].max() for x in range(m.shape[1]) if m[:, x].any()]
        fy = max(0, min(bots) - 30)                              # 가장 높은 접지점 바로 위부터 바닥 그림자·반사
        real = wk / "sp_real.png"
        if real.exists(): real.unlink()
        rc_, ro = run([PY, str(HERE / "restore_zone_a.py"), "--src", str(out_img), "--cand", str(wk / "sp_real_cand.png"),
                       "--obj-mask", str(mask), "--boxes", "0,0,2560,1440", "--floor-y", str(fy), "--obj-margin", "5",
                       "--color-gain", "--out", str(real)])
        print("실사화", ro.splitlines()[-1] if ro else "")
        rc2, vo = run([PY, str(HERE / "check_vp.py"), "--img", str(real), "--obj-mask", str(mask)])
        print("실사화 후", vo.split(" obj_vp")[0])
        if "RESTORE_OK" not in ro or not vo.startswith("VP_OK"):
            print("SPACE_FAIL 실사화 단계"); sys.exit(1)
        out_img = real
    Path(a.final).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(out_img, a.final)
    print(f"SPACE_OK {a.final} vp={best[2]} rms={best[3]}")


if __name__ == "__main__":
    main()
