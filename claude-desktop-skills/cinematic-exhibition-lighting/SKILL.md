---
name: cinematic-exhibition-lighting
description: "Create source-faithful, naturally photographed event-lighting prompts from an interior or stage render, with or without a lighting reference. Returns a final-composite prompt and a matching light-only plate prompt; generate images only when explicitly asked. Use when the user says '조명 바꿔줘', '이 조명으로', '레퍼런스 조명 적용', '조명 이식', '시네마틱 조명', '전시 느낌으로', '조명 레이어', 'lighting transfer'. Not for plain photorealism without lighting change (interior/arch-prompt-maker) or people compositing (person-layer-maker)."
---

# Cinematic Exhibition Lighting

Treat Image 1 as the immutable camera and construction source. When supplied, Image 2 contributes only lighting character: beam count, color, aiming behavior, haze, edge softness, and landing behavior. Never use Image 2's room, fixtures, people, screens, text, or architecture. Without Image 2, derive a restrained lighting design from the visible fixtures, venue type, and requested mood; do not invent a concert look.

## ★ 납품 관문 — 반려 점검표 (모든 런타임 공통, 생략 금지)

사용자가 같은 지적을 수십 번 반복했다(Claude·GPT 모두, 2026-11-05 KOBC 4차 반려). 이미지를 내기 전에 **아래 표를 항목마다 예/아니오로 채워 보고에 붙이고**, 자동 점검 토큰 없이 납품하지 않는다.

| # | 반려된 지적 (사용자 원문) | 통과 조건 |
|---|---|---|
| 1 | "무대만 빔이 가냐" | 빔이 무대 면에만 있지 않다. 객석 공기·객석 수광이 있다 |
| 2 | "무대 조명 이상해" | 빔 착지가 한 점에 모이지 않는다. 무대 가운데 X자 교차가 없다. 회색 기둥이나 뜬 빛자국이 없다 |
| 3 | "실 조명에 맞게" / "찾은 게 엉뚱해" | 모든 광원이 **사진에 실제로 보이는 기구**의 렌즈 좌표에서 나온다. 레퍼런스 사진은 실제로 열어 보고 사용자에게 보여 준다 |
| 4 | "객석에 조명이 묻어야 실감" | 객석 테이블·의자에 빛 번짐 풀이 있다 |
| 5 | "굴곡에 맞게 빛이 꺾이고 실루엣이 나와야" | 테이블 윗면·의자 윗선만 빛을 받는다. 카메라 쪽 면은 그늘로, 의자 뒤 카펫엔 그림자가 진다 |
| 6 | "빛줄기가 너무 얄상해" | 빔 능선 두께 12px 이상(2560 기준) + 넓은 헤이즈 외피 |
| 7 | "고보가 딱 떨어져 인위적" ↔ "너무 뭉갰어, 선명하게" | 블러 4~5px(경계 기울기 0.075~0.16 띠), 핫스팟→가장자리 감쇠, 얼룩. 글자는 읽힌다. 조명판에 나무결 없음 |
| 8 | "의자 테이블 빛 실루엣 이상해, 안 맞아" (평평한 보라 띠·대각선 끊김) | 테이블·의자 수광은 색 마스크 띠가 아니라 **원본 명암(위를 향한 면)** 을 따른다. 빔은 착지 전에 공기 속으로 사라진다. 자동 검사 "sticker edge" |
| 10 | "고보 텍스트가 원 밖으로 왜 나가" | 고보 글자는 원형 구멍 마스크 안에서만, 폭은 구멍 지름의 80% 이하 |
| 11 | "2027이 아니고 2026, 실수있다" | 고보·배너에 넣는 행사명·연도는 사진 속 LED·그래픽 표기와 대조해 다르면 빌드 전에 한 번 되묻는다(지시만 믿지 않는다) |
| 9 | "무대 조명 이상해" (회색 기둥) | 화면 밖 가상 광원(앞트러스 키) 금지 — 사진에 근거가 없으면 장부에 넣지 않는다 |
| 12 | "뭉게지는데" (2026-11-06 오디토리움) | GPT 재생성본(저해상도) 위에 조명을 얹지 않는다 — 고해상도 원본에서 레이어로. 반사광은 표면 반사율을 곱하고, 디자인물(사인·LED)에는 바닥 수광·과한 헤이즈를 얹지 않는다(LED 앞 헤이즈 30%). 예제 `scripts/examples/build_light_auditorium_blue.py` |
| 13 | "야 이미지 만들라고 프롬프트 말고" / "또 시작이네" (2026-11-09 레이더 워크숍 연회장) | 사용자가 이미지를 보내며 "조명스킬사용"이라고만 해도 **이미지(합성본+조명판)를 만든다**. 프롬프트 두 블록은 "프롬프트 만들어줘"라고 할 때만. 빔 LED 감쇄는 경계 블러(σ45)로 — 화면 경계에서 빔이 뚝 끊기면 반려. 예제 `scripts/examples/build_light_banquet_radar.py` |
| 14 | "조명위치와 빛이 나가는게 안맞아" / "너무 빛줄기가 얇아" / "분위기가 안난다" (2026-11-09 연회장) | 빔 방향 = 기구 몸통→렌즈 축 실측(2배 확대 크롭으로 두 점 찍기) — 비스듬한 프로파일을 수직으로 그리지 않는다. 빔 끝폭 w1 ≥ 60px(2560), 벽 그레이징은 260. 연회장 "분위기"는 주변 0.40 디밍 + 파란 렌즈 글로우 + 무대·객석 앞 파란 번짐(레퍼런스 확정 전 기본값) |
| 15 | "벽이 타는거 같다" / "무대로 내려 꽂는 조명 이상해, 절대 주지 말고 무대에서 테이블 쪽으로 퍼져나가는 걸로" (2026-11-09 연회장) | 연회장 기본 = 무대 다운라이트 빔 없음. 트러스 기구 → 테이블 윗면으로 넓게 퍼지는 빔(착지 x 가 광원 순서대로 = 교차 없음, 착지 전 소산) + 테이블·의자 윗면 풀. 벽 수광은 하이라이트가 날아가지 않게(벽 최대 상승 ≤ +25 밝기). 객석 경계 마스크는 σ30 이상(벽 밑단 가로선 방지) |

시작 전 질문은 하나만(2026-11-05 6판 반려의 원인 = 기준이 매 판 하나씩 드러남): "레퍼런스 사진 파일 + 분위기(은은/화려) + 하지 말 것, 이 세 가지 주시겠어요?" — 답이 없으면 은은한 컨퍼런스 기본값으로 가고 그 사실을 보고에 적는다.

자동 점검(필수, 성공 토큰 `AUDIT_PASS`):
```
python scripts/audit_light_rules.py --plate <조명판> --obj-mask <물건마스크> --src <원본> --ledger <ledger.json> --gobo <고보레이어> --beams <빔레이어> --floor-y <바닥선>
python scripts/verify_light_pair.py <pair.json>
```
보존 레이어 방식(Python 직접 작성)으로 만들 때는 즉석 코드 대신 `scripts/examples/build_light_kobc.py` 를 복사해서 시작한다. 위 1~9 가 기본값으로 들어 있고 `ledger.json` 을 같이 낸다(수광면 지도, 굵은 빔+외피, 부드러운 고보, 실제 기구 좌표 장부). 새로 반려되면 이 표에 한 줄을 추가하고 audit 스크립트에도 검사를 넣는다. `references/lessons.md` 에만 적으면 아무 모델도 읽지 않는다.

## 밝기 수치 검수 (AZTechnology 2026-11-12) (근거: vault wiki/reference/aztechnology-claude-code-blender-carrier-analysis-2026-11-12.md)
- 결과·원본을 흑백 변환해 벽·바닥·LED면·주 피사체 평균 밝기를 비교한다. 주 피사체와 배경 차이 약 10 이상, 원본 대비 구조물 밝기 순서가 뒤집히지 않아야 한다. 눈 판단 단독으로 통과시키지 않는다.

## Image execution — use retained layers, not improvised subtraction

For image requests, read [workflow and output contract](references/workflow-and-output-contract.md) before choosing the production method. Read [lighting layer set](references/lighting-layer-set.md) when separating effects or compositing across graphics/people. The [approved quality reference](references/forward-beam-quality-reference.md) is optional visual guidance, never a fixed lighting preset.

- Preserve the user-selected asset and its lighting. An accepted plate is not permission to regenerate it. A correction changes only the requested effects and updates the matching composite.
- Keep the restored source artwork **below foreground air effects**, above unrelated surface-light edits. Protect screen content, not the entire rectangular image region in front of it. Screen faces, LED emission and haze in front of a screen are different components.
- Author or retain the actual light layer(s) used to make the final composite. Export the plate from those same layers. A whole-image AI edit may be a candidate, but `max(candidate - original, 0)`, smoothing, or screen-shaped black masks do not establish an exact light extraction. Do not redraw beams while claiming to extract an approved composite.
- If the room must become darker, prepare and retain that exposure-adjusted base separately. Adding light cannot darken the original. Deliver that base when it is needed to reproduce the supplied composite.
- Before delivery, run `python scripts/verify_light_pair.py <pair.json>` as specified in the workflow contract. It checks saved images, layer provenance, required effect supports (including LED-foreground haze when present), unlit areas, dimensions and the declared blend. Its `NUMERIC_PASS` is **not** a visual approval: also inspect for graphic/geometry residue and discontinuities along the complete light paths. Never write or repeat a success flag without its actual check output.

## Default deliverable

When writing prompts for Image 1, return exactly two independently copyable fenced `text` blocks, in this order:

1. `COMPOSITED FINAL PROMPT`
2. `PURE ADDITIVE LIGHT PLATE PROMPT`

Put the heading inside each block. Output no prose before, between, or after the blocks. The first prompt requests the finished lighting-applied image; the second requests the matching black-background light plate. Do **not** create images, invoke an image generator, or save files unless the user explicitly asks to generate, make, render, produce, or deliver the images.

## Production gates — no partial delivery

For every generated composite or light plate, create this execution record **before** making an image:

1. `canvas`: the user's requested width × height. Start the final working canvas at that size. If a generator returns a smaller candidate, disclose its native size; register its lighting to the source canvas and build both final members from the same layers. Never independently enlarge the two deliverables or claim native-resolution generation from their final dimensions.
2. `base`: the immutable source asset path and its dimensions.
3. `selected composite`: the exact selected composite path and hash; update this record when the selected version changes. Use `none` only before selection.
4. `beam ledger`: every `S → T → L` path and its colour/intensity/haze.
5. `receiver ledger`: every visible direct or connected response on stage, stair, carpet, table, chair, wall, curtain, or screen surround, explicitly marked `lit` or `unlit`. Record foreground air support separately from the screen surface; a screen surface marked `unlit` does not mean its foreground air is black.

For a light-only request, the plate must contain every `lit` receiver response and only those responses; all `unlit` receivers and all base geometry remain RGB 0,0,0 black. Do not omit a spatial light response because it is subtle, and do not add a plausible response that is absent from the approved composite.

When a composite is selected, never call an image generator to make its plate. Use only its matching AOV/additive layer or a verified deterministic extraction. If neither exists, stop and report the missing source; an invented plate is forbidden.

Before delivery, verify: exact requested dimensions for both members, locked source/crop, beam-ledger placement, receiver-ledger completeness, and saved-image reconstruction with the retained base under the **one recorded** blend mode (Screen or Linear Dodge/Add). These modes are not interchangeable. Reject rather than deliver if any gate is missing, if either file was independently resized, or if the plate is a new lighting design.

## Reference and delivery routing

- **Lighting reference supplied:** Analyze Image 2 before prompting. Extract only its visible beam count, color temperature, source direction, haze density, beam softness, landing behavior, indirect-light reach, and venue mood. Apply those properties to Image 1's existing fixtures and surfaces; Image 2 never supplies architecture, screens, furniture, people, or graphics.
- **No lighting reference:** Derive a coherent venue-specific design from Image 1: visible fixture inventory and aiming, event type, LED brightness, room ambient level, stage hierarchy, audience/table layout, and available bounce surfaces. Build the room from broad stage wash, local LED spill, restrained wall/stair/table bounce, and only then the small number of shafts justified by haze and visible fixtures. Choose the count from the space; never use a fixed default beam count.
- **Prompt request:** Return the two prompt blocks only. Do not create images.
- **Explicit image request:** Generate and deliver both images separately: (1) the finished source-faithful composite and (2) its matching pure additive light plate. Generate only one if the user explicitly limits the request to a composite or to a plate.
- **Review before a skill edit:** When the user asks to see an image before changing this skill, generate the requested visual first and leave this skill unchanged until the user explicitly authorizes an update.
- If full photorealization is also needed, `interior-prompt-maker` owns the material-preserving base; this skill owns the lighting plan and both final outputs. Magnific and person workflows preserve the user-selected composite and do not redesign its lighting.

## ★ As-built reality rules — mandatory for exhibition and event scenes

When Image 1 shows an **exhibition booth, event hall, registration desk, entrance gate, photo zone, or backwall**, read this before planning any lighting:

```
C:\Users\PSH\.agents\skills\interior-prompt-maker\references\as-built-reality.md
```

It is the single source of truth for *how these builds actually look when installed*, derived from the user's own site photographs. **Never copy it — read that one path.** Every photorealization skill points at the same file.

Lighting-specific consequences you must respect:

1. **Self-luminous members are structure, not lighting.** A Maxima frame glows because the extrusion itself is the emitting surface — do not re-plan it as a fixture, do not add beams from it, and do not extinguish it. Its infill (matte banner or tension fabric) stays **non-emissive**, set back inside the frame.
2. **Judge glow by the member, not by print colour.** Whole member face glowing = Maxima. Only a thin edge line glowing = Octanorm with an LED strip. No glow = Octanorm. A bright blue printed graphic is **not** a light source.
3. **Maxima spill is wide.** Cyan-blue spill reaches the ceiling tiles and 1–2 m of floor, and it shifts the floor's own colour (a red carpet turns violet near the frame). Keep the gradient; do not clip the spill to the frame.
4. **Registration backwalls fall off downward** (ceiling diffuse dominates) — the opposite of stage backwalls, which are lit from below by uplights. Do not mix the two.
5. **Booth lighting is weak in real halls.** Clip-arm spots make bright ellipses with darker gaps between them; an evenly bright backwall reads as a render.

## Beam mapping

Before writing either prompt, inspect Image 1 and register each intended beam in original-canvas pixel coordinates:

- `S=(x,y)`: centre of an existing visible fixture lens or aperture.
- `T`: named visible target surface with a closed, perspective-correct contact polygon.
- `L`: closed direct-deposit polygon fully inside `T`.

Each beam must begin exactly at `S`, follow the visible aiming axis, and terminate at `L`. If an off-frame source is genuinely supported by Image 1, record its boundary entry point `E=(x,y)` and inward direction instead. Do not invent an in-frame source.

For tabletop targets, define `T` as the usable tabletop only; exclude its edges, underside, legs, chairs, objects, and adjacent surfaces. Inset `L` visibly from every tabletop edge. Use a perspective-correct diffuse response, never a circular floor pool or a floating halo.

Before prompting, make a **scene-response map** for every chosen beam: name every existing object that it directly lights, grazes, or is occluded by (for example tabletop, chair-back, exposed aisle carpet, stage lip, wall reveal, or screen surround). Specify its bounded material response and leave every unlit object unchanged. A beam-only design is incomplete when the selected composition visibly needs these connected responses.

## Natural event-lighting realism

The finished image should read as a professionally photographed live venue, not as a lighting previsualization. Apply this hierarchy: visible source and plausible landing first, subtle local material response second, volumetric shaft last. A shaft is evidence of air scatter, not a solid painted cone.

- **Venue baseline:** In a clean conference hall, default to low atmospheric haze. This is a default, not a cap on an explicit request for stronger effects or a darker room. Preserve readable requested shafts and adjust the room exposure separately; do not use faintness as a substitute for realism. Full-room haze is allowed only when the user explicitly requests it.
- **Shaft character:** A natural shaft has a soft, irregular density gradient, a dimmer outer envelope, and fades into room ambience before the target. Keep its center translucent enough that the existing room remains visually legible. It may be partly interrupted by truss, screen edge, furniture, or people where those objects actually occlude the optical path.
- **Aiming and count:** Do not turn every visible fixture on. Select a small asymmetric set whose angles follow the apparent fixture aim and whose landings contribute to the scene. Avoid repeated, evenly spaced, identical-width cones, symmetric fan arrays, and parallel beams that have no visible lighting purpose.
- **Surface response:** The landing is a low-contrast, perspective-correct material response. Matte carpet and fabric receive broad diffuse lift; black tablecloths receive a restrained, low-sheen elongated lift; metal or polished trim gets only a narrow localized highlight. Keep the response connected to its source and diminish it outside the target.
- **Furniture and occlusion:** Read tables, chairs, and stage furniture as actual light blockers and receivers, not as an untouched backdrop. Highlight only their real exposed top planes or rims where the mapped beam plausibly reaches them; preserve their shadowed faces and interrupt the light at their existing edges. Do not paint a generic pool beneath or through furniture.
- **Indirect light:** Treat stage lips, stair treads, wall reveals, and LED spill as local bounce with short falloff. It must inherit the selected palette and never become an even room-wide wash. Preserve the venue's existing ambient exposure and practical ceiling-light balance.
- **Color discipline:** Unless a show palette is requested, use one dominant temperature with a close supporting tint. White-blue means neutral-cool white with a lightly desaturated blue edge, not saturated cyan beams. Never mix warm amber accents into a white-blue design.

## Shared invariants

- Image 1 supplies the exact camera, crop, room, ceiling, walls, stage, screens, artwork, typography, logos, furniture, materials, and visible equipment.
- Do not aim direct surface illumination at LED faces unless requested. Restore original screen artwork above surface-light corrections, **below** existing or requested foreground beams/haze. Foreground air can overlap a screen in camera projection without illuminating or rewriting the screen surface. Never erase foreground light with a screen-rectangle mask.
- Do not invent, remove, duplicate, relocate, or redesign fixtures, truss, podiums, lecterns, microphones, monitors, speakers, cables, furniture, people, walls, ceiling, or stage geometry.
- Gobo, laser, lens flare, starburst, global color wash, and generic concert decoration are off unless explicitly requested.

## COMPOSITED FINAL PROMPT

The first block must be a complete prompt for a finished lighting-applied render, not a workflow specification. It must:

- Start exactly: `Create a final source-faithful lighting composite at the exact pixel dimensions of Image 1.`
- State Image 1 is the immutable edit target and, when supplied, Image 2 is lighting reference only.
- List all mapped `S → T → L` or approved `E → T → L` records with coordinates, beam color, intensity, haze, and target-material response.
- Describe the requested spatial mood faithfully and apply the natural event-lighting hierarchy. For a natural room atmosphere, specify sparse low-haze shafts, their visible source and landing, interrupted optical paths where applicable, and restrained connected response across the specified surfaces.
- Require illumination-only changes inside direct-beam, local-haze, landing, and physically connected short-spill masks. Preserve every source-material edge and all screen artwork.
- Explicitly prohibit all unrequested new objects and retain the original crop.

## PURE ADDITIVE LIGHT PLATE PROMPT

The second block must always be a separate, matching light-only extraction prompt. It must:

- Start exactly: `Create a pure additive lighting pass on a uniform RGB 0,0,0 black canvas at the exact pixel dimensions of Image 1.`
- Repeat the same mapped beam paths, source coordinates, colors, intensities, haze, and landing geometry used by the composite prompt.
- Include the shafts and the same visible light deposits/reflections that appear in the finished composite.
- Preserve the composite's sparse shaft count, soft density falloff, interruptions, and local indirect-light reach; do not turn faint ambient haze into bright isolated cones merely because the background is black.
- Include every visually present light effect from the selected composite design: every beam shaft, haze envelope, source glow, landing, and connected reflected-light deposit. A wall, table, seat top, aisle, or stage-front response is included only when it is actually lit in that design; never omit it, and never invent it.
- When the composite lights furniture or architecture, preserve that response as its own bounded additive mask: table-top deposits follow the real perspective-correct top edge; chair responses are separated rim/edge strokes; carpet deposits are clipped to exposed gaps; stage and wall responses remain local. Never reduce these to shafts alone.
- Render no room, fixture, screen, graphic, furniture, silhouette, base material, shadow, text, logo, or unlit pixel. Every pixel outside the registered beam, haze, landing, and reflection masks must be RGB 0,0,0 black.
- Make the plate directly alignable with the retained base under the recorded Screen or Linear Dodge (Add) mode, matching the delivered composite.
- Keep shafts visibly readable on black; do not reduce them to faint residual differences. Preserve their source glows, tapered haze, and connected reflected-light deposits.

## Explicit image-production requests

Only when the user explicitly asks to make, generate, render, produce, or deliver images, create both the composite and the matching plate as separate outputs unless they explicitly limit the request to one. Build the plate from the selected composite, inspect it visually, and ensure no beam, haze, glow, landing, or directly illuminated material response is missing. Deliver each output at Image 1's exact pixel dimensions.

## Selected-composite plate lock — mandatory

Once a composite is selected, its light plate is an **extraction of that exact selected composite**, not a second lighting design and not a plausible replacement inferred from Image 1. Do not create, move, strengthen, remove, or reinterpret a beam, wash, landing, or reflected response while making the plate.

Before generating a plate, make a response ledger from the selected composite at original-canvas coordinates. For every visible light effect, record its source or indirect source, mask, and receiver. For every table, chair, aisle, wall, screen, or stage region that is **not visibly lit in the selected composite**, record `unlit` and render it RGB 0,0,0 in the plate. Never add a plausible-looking furniture rim, table arc, carpet pool, or environmental bounce merely because the object is near a light.

Use the selected composite as the plate's required spatial reference. Image 1 may be consulted only to name the locked receiver geometry; it must not supply a new lighting plan. If the selected composite is unavailable, no source-aligned mask can be made, or the tool cannot keep a receiver response on its original perspective-correct surface, stop and request/recreate the composite instead of delivering a guessed plate.

After generation, compare the plate against the selected composite effect by effect: every non-black region must correspond to a visible effect in the composite, and every visible composite effect must have a corresponding plate mask. Reject the plate if it contains object silhouettes, geometry-derived highlights, or any table/chair response that cannot be pointed to in the selected composite. A resize is permitted only when the same spatial transform is applied to both members of the composite/plate pair; resizing one output alone never proves alignment.

### Exact extraction is not generation

When the user says “extract,” “pull only the light,” or selects an existing composite, interpret it as a request for an **unchanged extraction**, never a request to generate a new light design. Do not invoke an image generator to recreate the plate from a flattened image: it can invent or relocate fixtures, beams, furniture responses, and material edges.

An exact plate may be delivered only from one of these matching sources: (1) the renderer's Light Select / lighting AOV from the same camera frame, (2) the selected composite's retained editable light layer(s), or (3) a registered before/after workflow with known blend/exposure and independently verified effect supports, which proves the difference contains no graphic/geometry residue. A clipped highlight cannot be inverted by subtraction. Retain the source as the plate's provenance; for source (3), preserve the verified difference as a source layer and label its provenance honestly.

If only flattened source and composite images are available and a verified difference mask cannot be made, stop. State that exact extraction requires the matching AOV or additive-light layer, and do not output an AI-invented substitute. A plausible new plate is a failed result, even if it looks realistic.

When a user explicitly requests a missing-effect correction, author that correction as a retained layer, update the composite from it, then export the matching plate. Call it a correction/reconstruction, not an unchanged extraction. Do not alter unrelated accepted effects.

### Approved-asset incremental edit lock

When the user says “existing one,” “that one,” “add only this,” or marks a target on an image, the named/marked approved asset is the only edit target. Copy it to a versioned backup, then edit **only** the requested mask. Do not regenerate, restyle, rebuild from Image 1, substitute an earlier generated artifact, or alter any unmarked lighting.

A user-drawn box, arrow, or mark is an edit mask, not a vague placement hint. Use its exact pixel bounds. Do not infer a source count, beam shape, colour, endpoint, or any change outside that mask. If those details cannot be read from the approved asset and mark, ask instead of guessing.

Before delivery, run `scripts/verify_incremental_edit.py` against the backup and candidate with the marked rectangle. It must report the same dimensions and zero changed pixels outside the allowed rectangle. Reject the edit on any failure. Never claim an incremental update was made without this proof.

## Verification

Reject a generated result if any check fails:

- A 50% overlay moves, repaints, or rebuilds architecture, screen text, logos, furniture contours, carpet boundaries, or crop.
- A beam does not begin at its registered source or terminate on its registered `L` polygon.
- The composite loses requested visible beams, adds a global wash, or concentrates light on an unrequested surface.
- The beams read as opaque, uniform, hard-edged cones; remain equally visible across a clear room; form a symmetric fixture-by-fixture fan; or continue through visible occluders without a plausible optical path.
- The light landings are circular pools, extend beyond the perspective-correct target surface, or have stronger contrast than the source fixture and venue exposure support.
- The color palette mixes unrelated accents, or white-blue lighting is rendered as saturated blue/cyan rather than neutral-cool white with restrained blue tint.
- The light plate differs in beam placement, color, or landing response from the composite, or contains non-black pixels outside the registered lighting masks.
- Any beam, haze, source glow, landing, or directly illuminated material response visible in the selected composite design is absent from the plate.
- Foreground beam/haze paths are cut at LED/graphic rectangle boundaries, even if typography is preserved. Check path continuity in both outputs, not only the regions outside screens.
- The plate contains a table, chair, aisle, wall, stage, or screen response that is not visibly present at the corresponding location in the selected composite, even if that response looks physically plausible.
- The plate was generated from a new inferred lighting plan, from Image 1 alone after a composite was selected, or was independently resized without applying the same transform to the selected composite.
- The composite or plate shows beams while ignoring mapped table, chair, aisle, stage, wall, or frame responses, or lets light continue through their visible occluding edges.
- The plate's shafts are too faint to read clearly against its black canvas.
- An explicit image request returns only prompt text, or delivers the composite and light plate as one merged/ambiguous output when the user did not limit the request to one.

If registration fails, refine individual masks; do not weaken the geometry lock.
