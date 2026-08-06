---
name: cinematic-exhibition-lighting
description: "Create source-faithful stage-lighting composites, pure additive light plates, and source-aligned material lighting-response passes from an interior or event render plus a lighting reference. Use for cinematic event lighting, beam transfer, concert-light references, table or wall illumination, lighting compositing, and light-only passes. Lock Image 1 camera, architecture, screens, typography, logos, graphics, furniture, and all non-lighting pixels."
---

# Cinematic Exhibition Lighting

Treat Image 1 as the immutable camera and construction source. Transfer only the beam character from Image 2. Never solve a fixed-geometry exhibition or conference render through a full-scene relight.

## Choose the pass mode first

Use exactly one mode and name it in the second output block.

1. **PURE ADDITIVE LIGHT PLATE** is the default. Use it when only beam shafts, haze, pools, spill, and reflections are needed. The output is RGB 0,0,0 black outside those effects.
2. **MATERIAL LIGHTING-RESPONSE PASS** is required when the user asks for light to visibly fall on a table, chair, carpet, wall, or other source material, or when the target generator must preserve the visibly lit material within the light masks. Retain Image 1 material pixels *only inside* the directly illuminated masks; keep everything else black. This is not a mistake or a full-scene render.

Do not use a pure black plate when the user explicitly requires visible source-material response inside the illuminated area.

## Beam mapping: no semantic guessing

Before writing a prompt, inspect Image 1 and register every beam with original-canvas coordinates:

- `S=(x,y)`: the exact centre of one existing visible Image 1 fixture lens or aperture.
- `T`: a named, visible target surface plus its closed perspective-correct contact polygon.
- `L`: a closed direct-deposit polygon fully contained within `T`; list its vertices in original-canvas pixel coordinates.

For each beam, state that its centreline starts exactly at `S`, follows the existing fixture aiming axis, and stops at the first intersection with `L`. Include the original canvas dimensions, coordinate records, and polygon vertices. Do not use only vague direction words such as “left”, “right”, “toward the stage”, or “downward”.

For table illumination, define `T` as the visible usable tabletop plane only: exclude its edge thickness, underside, chairs, objects, base, legs, neighbouring tables, and adjacent structures. Inset `L` from every tabletop edge by a visible guard band and keep every direct-beam deposit fully inside it. The centre aisle, empty floor, carpet, stage, wall, chair, and table legs are excluded unless separately named as a target. Allow short spill only on the same continuous table material, immediately adjacent to `L`, and never across a table edge. Do not substitute circular floor pools for tabletop illumination. Use soft, perspective-correct diffuse tabletop gradients; hard discs, gobos, and floating halos are prohibited unless requested.

## Fixed-source rules

- Image 1 supplies the camera, crop, room, ceiling, walls, stage, screens, artwork, typography, logos, furniture, materials, visible equipment, and all source geometry.
- Image 2 supplies only beam count, color, source-side direction, landing behavior, haze density, and edge softness. Ignore its performers, audience, truss, fixtures, screens, text, and architecture.
- Begin a visible beam at the exact recorded `S` lens/aperture and along its visible aiming axis and mounting structure. An off-frame source is allowed only if Image 1 visibly supports its direction: record its canvas-boundary entry point `E=(x,y)` and inward direction, start the beam at `E`, and never invent an in-frame fixture or open-air origin. Never invent, duplicate, relocate, or redesign a fixture, truss, podium, lectern, monitor, speaker, cable, stage extension, table, chair, wall, or ceiling member.
- Keep beams clear of LED faces unless the user explicitly targets an LED face. Restore source screen artwork above every light layer.
- Gobo and laser are OFF unless the user explicitly requests them.

## Mandatory output contract

When Image 1 and lighting-reference Image 2 are supplied, return exactly two independent, separately copyable fenced `text` blocks, in this order:

1. `COMPOSITED FINAL SPEC`
2. `PURE ADDITIVE LIGHT PLATE PROMPT` **or** `MATERIAL LIGHTING-RESPONSE PASS PROMPT`, matching the selected mode.

Put each heading inside its own fenced block. Output only those two blocks, with no prose before, between, or after them. Do not generate an image unless asked.

### COMPOSITED FINAL SPEC

Specify all of the following:

1. Image 1 remains the untouched bottom layer at its original dimensions.
2. Generate the selected pass at identical dimensions and blend it with Screen or Linear Dodge (Add).
3. Mask the pass to each registered `S → T` or `E → T` beam-path mask, its local haze envelope ending at `L`, and its exact closed `L` landing mask.
4. Use a masked Curves or Multiply adjustment only if the requested look needs contrast; never darken LED faces or direct landing zones.
5. Restore Image 1 as the top source-pixel layer for all LED faces, typography, logos, graphic panels, screen frames, straight architecture, furniture contours, carpet boundaries, and every unlit region.
6. Explicitly name all forbidden generated objects, including podiums and lecterns when the scene contains a stage.
7. Final crop and every source pixel outside the lighting masks remain identical to Image 1.

### Pass prompt requirements

Start a pure plate prompt exactly with:

`Create a pure additive lighting pass on a uniform RGB 0,0,0 black canvas.`

Start a response-pass prompt exactly with:

`Create a source-aligned material lighting-response pass at the exact pixel dimensions of Image 1.`

Then include these requirements, adjusted to the selected mode:

- List every mapped `S → T` or approved `E → T` path with its source/entry coordinate, `T` and `L` polygon vertices, beam color, intensity, haze, and target-surface response.
- Require a beam to stop at `L`; prohibit accidental landings, material response, or post-target continuation on the aisle, bare floor, stage, LED faces, or any other excluded surface.
- For a response pass, permit only the original material pixels within a direct-beam, local-haze, `L`, or physically connected short-spill mask. Inside every response mask, alter illumination values only: do not move, warp, extend, erase, repaint, occlude, or synthesize any source-material edge, object silhouette, table boundary, furniture contour, or camera-space geometry. An adjacent-spill mask must share a visible physical edge with `T`, remain on the same continuous source-material surface, and never cross a tabletop edge, aisle, bare floor, stage, furniture boundary, or excluded surface.
- For a pure plate, render no room, fixture, screen, graphic, furniture, silhouette, base material, shadow, or unlit pixel.
- Prohibit global blue or magenta wash, lens flare, starburst, generic concert pattern, and any unrequested decorative effect.
- Explicitly require no new visible hardware, podium, lectern, rostrum, microphone stand, display stand, console, monitor, speaker, cable, person, object, furniture, or architecture.

## Verification and rejection

Reject the result if any check fails:

- A 50% overlay against Image 1 moves, repaints, or rebuilds an architectural edge, screen, logo, text, furniture contour, carpet boundary, or crop.
- A beam does not visibly begin at its registered existing source lens/approved boundary entry or does not terminate at its registered `L` polygon on `T`.
- A table-targeted beam, response, or spill pixel crosses its registered tabletop masks onto the aisle, floor, stage, wall, chair, or as a hard isolated disc instead of a perspective-correct tabletop response.
- A pure plate has a non-black pixel outside its beam, haze, or direct-deposit masks.
- A material response pass retains source material outside its direct illumination masks or creates any new scene object.

If a generator cannot keep the source and target coordinates registered, reject its output. Do not solve the mismatch by weakening the geometry lock; create or refine the individual source and target masks instead.
