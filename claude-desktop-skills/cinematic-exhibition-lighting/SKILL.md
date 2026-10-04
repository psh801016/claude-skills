---
name: cinematic-exhibition-lighting
description: "Create source-faithful, naturally photographed event-lighting prompts from an interior or stage render, with or without a lighting reference. Returns a final-composite prompt and a matching light-only plate prompt; generate images only when explicitly asked."
---

# Cinematic Exhibition Lighting

Treat Image 1 as the immutable camera and construction source. When supplied, Image 2 contributes only lighting character: beam count, color, aiming behavior, haze, edge softness, and landing behavior. Never use Image 2's room, fixtures, people, screens, text, or architecture. Without Image 2, derive a restrained lighting design from the visible fixtures, venue type, and requested mood; do not invent a concert look.

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

## ★ As-built reality rules — mandatory for exhibition and event scenes (wired 2026-09-21)

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
