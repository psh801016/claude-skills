<!-- magnific-compositing-prep/SKILL.md 에서 분리. 원문 그대로이며 내용 변경 없음. -->

## 출력 예시

### 예시 1 — 호텔 연회장 실사진

```
[SOURCE: 실사진]

PROMPT
real interior photograph upscale, perfect rectilinear perspective, plumb vertical walls, level horizontal ceiling and floor planes, accurate vanishing points preserved, straight parallel lines throughout, compositing-ready background plate, enhance sharpness and material clarity only, no structural or spatial alteration, preserve all existing surfaces as-is, preserve the Fairmont logo on the rear LED screen exactly, preserve the floral patterned carpet color and repeat design exactly

NEGATIVE (SD/ComfyUI 대체 경로 전용 — Magnific/nanobanana에는 입력하지 않음)
barrel distortion, pincushion distortion, fisheye, curved walls, warped geometry, bent vertical lines, tilted horizon, perspective warp, lens aberration, added film grain, artificial noise, vignette, hallucinated texture, artificial aging, new stains or marks, changed room geometry, new furniture added, objects moved or removed, hallucinated objects, new architectural elements, reframed composition, style change, dreamlike, painterly, illustration

SETTINGS
Creativity : 0.1
Resemblance: 0.95
Detail     : 0.35
HDR        : 0.1
```

### 예시 2 — 오피스 회의실 CGI 렌더

```
[SOURCE: CGI 렌더]

PROMPT
convert CGI render to photorealistic interior photograph, strict rectilinear geometry lock — plumb verticals, level horizontals, accurate vanishing points unchanged, no perspective shift, photorealistic material quality, realistic surface micro-texture, subtle material imperfection and aging, photographic light response on surfaces, compositing-ready photorealistic background, professional architectural photography, acoustic ceiling tile depth and grid shadow, carpet tile seam and wear variation, glass partition fingerprint and reflection depth, desk surface material weight, diffuse task lighting softness, preserve the glass partition transparency and surface reflection exactly, preserve the acoustic ceiling tile grid layout and panel depth exactly, preserve the long conference table position and surface geometry exactly

NEGATIVE (SD/ComfyUI 대체 경로 전용 — Magnific/nanobanana에는 입력하지 않음)
CGI look, plastic material, uniform synthetic texture, oversaturated colors, perfectly clean non-aging surfaces, barrel distortion, pincushion distortion, fisheye, curved walls, warped geometry, bent vertical lines, perspective shift, lens aberration, render artifact, ambient occlusion banding, new furniture added, objects moved, hallucinated objects, new architectural elements, toon shading, illustration, cartoon, added film grain

SETTINGS
Creativity : 0.3
Resemblance: 0.80
Detail     : 0.5
HDR        : 0.2
```
