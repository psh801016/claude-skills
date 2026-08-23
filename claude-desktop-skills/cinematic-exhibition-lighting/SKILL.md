---
name: cinematic-exhibition-lighting
description: "Create source-faithful event-lighting prompts from an interior or stage render plus a lighting reference. Returns a final-composite prompt and a matching light-only plate prompt; generate images only when explicitly asked."
---

# Cinematic Exhibition Lighting

Treat Image 1 as the immutable camera and construction source. Transfer only the lighting character from Image 2: beam count, color, aiming behavior, haze, edge softness, and landing behavior. Never use Image 2's room, fixtures, people, screens, text, or architecture.

## Default deliverable

When Image 1 and lighting-reference Image 2 are supplied, return exactly two independently copyable fenced `text` blocks, in this order:

1. `COMPOSITED FINAL PROMPT`
2. `PURE ADDITIVE LIGHT PLATE PROMPT`

Put the heading inside each block. Output no prose before, between, or after the blocks. The first prompt requests the finished lighting-applied image; the second requests the matching black-background light plate. Do **not** create images, invoke an image generator, or save files unless the user explicitly asks to generate, make, render, produce, or deliver the images.

## Beam mapping

Before writing either prompt, inspect Image 1 and register each intended beam in original-canvas pixel coordinates:

- `S=(x,y)`: centre of an existing visible fixture lens or aperture.
- `T`: named visible target surface with a closed, perspective-correct contact polygon.
- `L`: closed direct-deposit polygon fully inside `T`.

Each beam must begin exactly at `S`, follow the visible aiming axis, and terminate at `L`. If an off-frame source is genuinely supported by Image 1, record its boundary entry point `E=(x,y)` and inward direction instead. Do not invent an in-frame source.

For tabletop targets, define `T` as the usable tabletop only; exclude its edges, underside, legs, chairs, objects, and adjacent surfaces. Inset `L` visibly from every tabletop edge. Use a perspective-correct diffuse response, never a circular floor pool or a floating halo.

## Shared invariants

- Image 1 supplies the exact camera, crop, room, ceiling, walls, stage, screens, artwork, typography, logos, furniture, materials, and visible equipment.
- Keep beams clear of LED faces unless the user explicitly targets an LED face. In the composite, restore the original screen artwork above light layers.
- Do not invent, remove, duplicate, relocate, or redesign fixtures, truss, podiums, lecterns, microphones, monitors, speakers, cables, furniture, people, walls, ceiling, or stage geometry.
- Gobo, laser, lens flare, starburst, global color wash, and generic concert decoration are off unless explicitly requested.

## COMPOSITED FINAL PROMPT

The first block must be a complete prompt for a finished lighting-applied render, not a workflow specification. It must:

- Start exactly: `Create a final source-faithful lighting composite at the exact pixel dimensions of Image 1.`
- State Image 1 is the immutable edit target and Image 2 is lighting reference only.
- List all mapped `S → T → L` or approved `E → T → L` records with coordinates, beam color, intensity, haze, and target-material response.
- Describe the requested spatial mood faithfully. If the user asks for natural room atmosphere, retain visible soft volumetric beams while distributing restrained response across the specified room surfaces; do not silently remove the beams or focus all light on the stage.
- Require illumination-only changes inside direct-beam, local-haze, landing, and physically connected short-spill masks. Preserve every source-material edge and all screen artwork.
- Explicitly prohibit all unrequested new objects and retain the original crop.

## PURE ADDITIVE LIGHT PLATE PROMPT

The second block must always be a separate, matching light-only extraction prompt. It must:

- Start exactly: `Create a pure additive lighting pass on a uniform RGB 0,0,0 black canvas at the exact pixel dimensions of Image 1.`
- Repeat the same mapped beam paths, source coordinates, colors, intensities, haze, and landing geometry used by the composite prompt.
- Include the shafts and the same visible light deposits/reflections that appear in the finished composite.
- Include every visually present light effect from the selected composite design: every beam shaft, haze envelope, source glow, landing, and connected reflected-light deposit. A wall, table, seat top, aisle, or stage-front response is included only when it is actually lit in that design; never omit it, and never invent it.
- Render no room, fixture, screen, graphic, furniture, silhouette, base material, shadow, text, logo, or unlit pixel. Every pixel outside the registered beam, haze, landing, and reflection masks must be RGB 0,0,0 black.
- Make the plate directly alignable with the composite under Screen or Linear Dodge (Add).
- Keep shafts visibly readable on black; do not reduce them to faint residual differences. Preserve their source glows, tapered haze, and connected reflected-light deposits.

## Explicit image-production requests

Only when the user explicitly asks to make, generate, render, produce, or deliver images, create the requested composite and/or plate. For a requested light-only plate, produce the complete visible lighting design from the selected composite on a black canvas, inspect it visually, and ensure no beam, haze, glow, landing, or directly illuminated material response is missing. Deliver it at Image 1's exact pixel dimensions.

## Verification

Reject a generated result if any check fails:

- A 50% overlay moves, repaints, or rebuilds architecture, screen text, logos, furniture contours, carpet boundaries, or crop.
- A beam does not begin at its registered source or terminate on its registered `L` polygon.
- The composite loses requested visible beams, adds a global wash, or concentrates light on an unrequested surface.
- The light plate differs in beam placement, color, or landing response from the composite, or contains non-black pixels outside the registered lighting masks.
- Any beam, haze, source glow, landing, or directly illuminated material response visible in the selected composite design is absent from the plate.
- The plate's shafts are too faint to read clearly against its black canvas.

If registration fails, refine individual masks; do not weaken the geometry lock.
