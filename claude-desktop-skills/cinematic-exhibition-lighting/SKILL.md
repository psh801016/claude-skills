---
name: cinematic-exhibition-lighting
description: "Create source-faithful, naturally photographed event-lighting prompts from an interior or stage render, with or without a lighting reference. Returns a final-composite prompt and a matching light-only plate prompt; generate images only when explicitly asked."
---

# Cinematic Exhibition Lighting

Treat Image 1 as the immutable camera and construction source. When supplied, Image 2 contributes only lighting character: beam count, color, aiming behavior, haze, edge softness, and landing behavior. Never use Image 2's room, fixtures, people, screens, text, or architecture. Without Image 2, derive a restrained lighting design from the visible fixtures, venue type, and requested mood; do not invent a concert look.

## Default deliverable

When writing prompts for Image 1, return exactly two independently copyable fenced `text` blocks, in this order:

1. `COMPOSITED FINAL PROMPT`
2. `PURE ADDITIVE LIGHT PLATE PROMPT`

Put the heading inside each block. Output no prose before, between, or after the blocks. The first prompt requests the finished lighting-applied image; the second requests the matching black-background light plate. Do **not** create images, invoke an image generator, or save files unless the user explicitly asks to generate, make, render, produce, or deliver the images.

## Reference and delivery routing

- **Lighting reference supplied:** Analyze Image 2 before prompting. Extract only its visible beam count, color temperature, source direction, haze density, beam softness, landing behavior, indirect-light reach, and venue mood. Apply those properties to Image 1's existing fixtures and surfaces; Image 2 never supplies architecture, screens, furniture, people, or graphics.
- **No lighting reference:** Derive a coherent venue-specific design from Image 1: visible fixture inventory and aiming, event type, LED brightness, room ambient level, stage hierarchy, audience/table layout, and available bounce surfaces. Build the room from broad stage wash, local LED spill, restrained wall/stair/table bounce, and only then the small number of shafts justified by haze and visible fixtures. Choose the count from the space; never use a fixed default beam count.
- **Prompt request:** Return the two prompt blocks only. Do not create images.
- **Explicit image request:** Generate and deliver both images separately: (1) the finished source-faithful composite and (2) its matching pure additive light plate. Generate only one if the user explicitly limits the request to a composite or to a plate.
- **Review before a skill edit:** When the user asks to see an image before changing this skill, generate the requested visual first and leave this skill unchanged until the user explicitly authorizes an update.
- If full photorealization is also needed, `interior-prompt-maker` owns the material-preserving base; this skill owns the lighting plan and both final outputs. Magnific and person workflows preserve the user-selected composite and do not redesign its lighting.

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

- **Venue baseline:** In a clean conference hall, default to low atmospheric haze. Let most fixtures read through their lit target, gentle fixture glow, and short near-source falloff; use only the few shafts that materially improve the requested mood. Full-room haze is allowed only when the user explicitly requests it.
- **Shaft character:** A natural shaft has a soft, irregular density gradient, a dimmer outer envelope, and fades into room ambience before the target. Keep its center translucent enough that the existing room remains visually legible. It may be partly interrupted by truss, screen edge, furniture, or people where those objects actually occlude the optical path.
- **Aiming and count:** Do not turn every visible fixture on. Select a small asymmetric set whose angles follow the apparent fixture aim and whose landings contribute to the scene. Avoid repeated, evenly spaced, identical-width cones, symmetric fan arrays, and parallel beams that have no visible lighting purpose.
- **Surface response:** The landing is a low-contrast, perspective-correct material response. Matte carpet and fabric receive broad diffuse lift; black tablecloths receive a restrained, low-sheen elongated lift; metal or polished trim gets only a narrow localized highlight. Keep the response connected to its source and diminish it outside the target.
- **Furniture and occlusion:** Read tables, chairs, and stage furniture as actual light blockers and receivers, not as an untouched backdrop. Highlight only their real exposed top planes or rims where the mapped beam plausibly reaches them; preserve their shadowed faces and interrupt the light at their existing edges. Do not paint a generic pool beneath or through furniture.
- **Indirect light:** Treat stage lips, stair treads, wall reveals, and LED spill as local bounce with short falloff. It must inherit the selected palette and never become an even room-wide wash. Preserve the venue's existing ambient exposure and practical ceiling-light balance.
- **Color discipline:** Unless a show palette is requested, use one dominant temperature with a close supporting tint. White-blue means neutral-cool white with a lightly desaturated blue edge, not saturated cyan beams. Never mix warm amber accents into a white-blue design.

## Shared invariants

- Image 1 supplies the exact camera, crop, room, ceiling, walls, stage, screens, artwork, typography, logos, furniture, materials, and visible equipment.
- Keep beams clear of LED faces unless the user explicitly targets an LED face. In the composite, restore the original screen artwork above light layers.
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
- Make the plate directly alignable with the composite under Screen or Linear Dodge (Add).
- Keep shafts visibly readable on black; do not reduce them to faint residual differences. Preserve their source glows, tapered haze, and connected reflected-light deposits.

## Explicit image-production requests

Only when the user explicitly asks to make, generate, render, produce, or deliver images, create both the composite and the matching plate as separate outputs unless they explicitly limit the request to one. Build the plate from the selected composite, inspect it visually, and ensure no beam, haze, glow, landing, or directly illuminated material response is missing. Deliver each output at Image 1's exact pixel dimensions.

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
- The composite or plate shows beams while ignoring mapped table, chair, aisle, stage, wall, or frame responses, or lets light continue through their visible occluding edges.
- The plate's shafts are too faint to read clearly against its black canvas.
- An explicit image request returns only prompt text, or delivers the composite and light plate as one merged/ambiguous output when the user did not limit the request to one.

If registration fails, refine individual masks; do not weaken the geometry lock.
