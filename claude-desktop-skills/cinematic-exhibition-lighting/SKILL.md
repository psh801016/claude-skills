---
name: cinematic-exhibition-lighting
description: "Create source-faithful stage-lighting composites and pure light-only plates from an interior or event render plus a lighting reference. Use for cinematic event lighting, beam transfer, concert-light references, lighting compositing, and light-only passes. Lock Image 1 camera, architecture, screens, typography, logos, graphics, furniture, and all non-lighting pixels."
---

# Cinematic Exhibition Lighting

Use an additive lighting plate over the original image. Do not use full-scene i2i relighting for interiors that contain fixed architecture, screens, typography, logos, or furniture.

## Mandatory output contract

When Image 1 and lighting-reference Image 2 are supplied, return exactly two independent blocks, in this order:

1. `COMPOSITED FINAL SPEC`
2. `LIGHT-ONLY PLATE PROMPT`

The composited final is **not** an i2i prompt. It is a deterministic layer-composite specification: Image 1 stays the bottom and top source-pixel layer, and only the generated light plate is blended between them. Never offer a Magnific full-scene prompt as the final path.

Output only the two blocks. Do not include an explanation, settings, negative prompt, or generated image unless asked.

## Image roles

- **Image 1:** immutable source of camera, crop, geometry, ceiling, walls, stage, screens, source artwork, typography, logos, furniture, materials, and visible equipment.
- **Image 2:** lighting reference only. Extract beams, color, source-side direction, landing zones, haze density, and edge softness. Ignore its performers, audience, truss, fixtures, screens, text, watermark, and architecture.
- **Gobo:** OFF unless the user explicitly requests it in the current message.

## Fail-closed mapping

Map Image 2 beams only to physically plausible, concealed positions already available in Image 1. Never invent fixtures, truss, speaker towers, screens, proscenium, walls, ceiling members, stage extensions, or seats.

Omit any reference component that cannot be mapped without adding visible equipment. Concert lasers are omitted unless the user specifically asks for lasers and supplies their placement.

Keep beams clear of every screen face. The source screen artwork is always restored from Image 1 above the light layer.

## COMPOSITED FINAL SPEC

Specify this exact procedure in the first block:

1. Use Image 1 as the untouched bottom layer at original pixel dimensions.
2. Generate the second block on a uniform black canvas at exactly the same dimensions.
3. Put the light-only plate above Image 1 with Screen or Linear Dodge (Add).
4. Add a mask that confines the plate to the described beam paths, haze envelopes, and physical landing zones.
5. Add a Curves or Multiply darkening adjustment beneath the plate and above Image 1. Mask it to the non-beam ceiling, side walls, far seating, deep corners, and rear auditorium only. Preserve visible material detail; do not darken the LED faces or stage landing pools.
6. Put a duplicate of Image 1 at the top. Mask it to all LED faces, typography, logos, screen frames, straight architectural edges, furniture contours, carpet boundaries, and all areas that must remain source-identical.
7. Final canvas, crop, and every non-lighting source pixel must be identical to Image 1.

## LIGHT-ONLY PLATE PROMPT

Start the prompt exactly with:

`Create a pure additive lighting pass on a uniform RGB 0,0,0 black canvas.`

Then describe only the mapped beams, their haze, and their physically connected light deposits.

- Render beam shafts, haze confined tightly to those shafts, compact spot pools, short spill, restrained rim light, and material-appropriate reflections.
- Keep the entire canvas black outside those effects.
- Render no room, ceiling, wall, fixture, screen, graphic, typography, logo, furniture, base material, silhouette, shadow, or unlit pixel.
- Render no visible source hardware. Concealed or off-frame sources contribute only the physically aligned beam and landing light.
- Render no global blue or magenta wash, lens flare, starburst, generic concert pattern, or decorative effect not explicitly mapped from Image 2.

## Verification

Reject the result if either check fails:

- A 50% overlay of the final composite against Image 1 shows movement or repainting of an architectural edge, screen, logo, text, furniture contour, or crop.
- The light-only plate has any non-black pixel outside its beam, haze, or direct light-deposit masks.

## Exact block templates

```text
COMPOSITED FINAL SPEC
Use Image 1 unchanged as the bottom layer at its original pixel dimensions. Place the light-only plate above it in Screen or Linear Dodge (Add), then mask the plate to only [mapped beam paths, haze envelopes, and landing zones]. Add a Curves or Multiply adjustment beneath the plate, masked only to [non-beam ceiling, side walls, far seating, deep corners, and rear auditorium], preserving visible material detail while keeping the LED faces and stage landing pools unchanged. Restore Image 1 source pixels as the top layer for every LED face, screen artwork, typography, logo, screen frame, straight architectural edge, furniture contour, carpet boundary, and unlit region. Final canvas dimensions, crop, and all non-lighting source pixels remain exactly identical to Image 1.
```

```text
LIGHT-ONLY PLATE PROMPT
Create a pure additive lighting pass on a uniform RGB 0,0,0 black canvas. Use Image 2 solely as the lighting reference and map only its physically plausible beam signature onto the camera geometry of Image 1: [beam positions, directions, colors, haze, and landing zones]. Render only the complete volumetric shafts, tightly contained haze, and their physically connected spot pools, short spill, rim light, and reflections. Every LED screen, screen artwork, event title, typography, logo, panel glow, screen reflection, architecture, ceiling, wall, furniture, fixture, object silhouette, material base color, shadow, and unlit pixel contributes zero visible pixels.
```
