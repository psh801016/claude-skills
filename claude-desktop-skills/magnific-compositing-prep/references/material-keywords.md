<!-- magnific-compositing-prep/SKILL.md 에서 분리. 원문 그대로이며 내용 변경 없음. -->

## 공간별 재료 키워드 (CGI 렌더 전용)

PROMPT 핵심 구성 뒤에 해당 공간 블록을 이어 붙인다.

### 호텔 연회장 / 이벤트홀 / 컨퍼런스홀
```
patterned carpet pile variation and weave texture,
dark upholstered chair fabric tension and fold,
acoustic wall panel micro-texture and mounting depth,
warm LED track spotlight falloff and shadow definition,
projection screen matte surface, polished stage floor reflection gradient
```

### 오피스 / 회의실
```
acoustic ceiling tile depth and grid shadow,
carpet tile seam and wear variation,
glass partition fingerprint and reflection depth,
desk surface material weight, diffuse task lighting softness
```

### 호텔 로비 / 고급 상업 공간
```
large format stone floor mineral variation and joint depth,
marble polished reflection gradient,
metal trim anisotropic specular, reception desk material weight,
lobby glazing system depth and mullion shadow
```

### 상업 쇼룸 / 전시 공간
```
polished or honed floor surface reflectivity,
display shelf and case material edge detail,
neutral wall matte surface, focused spotlight circle definition,
product surface micro-texture contrast
```

### 주거 거실 / 침실
```
wood flooring grain variation and plank seam,
upholstered sofa fabric compression and weave,
matte painted wall subtle surface variation,
curtain fabric translucency and fold
```

### 카페 / 레스토랑
```
table surface material scratch and variation,
upholstery weave and seam detail,
ceramic or stone tile grout line depth,
warm pendant light glow falloff, bar counter edge and material weight
```

### 전시관 / 갤러리
```
polished concrete or hardwood reflectivity and seam,
white plaster wall micro-texture, track light directional definition,
artwork frame edge and glass reflection, neutral ambient balance
```

### 의료 / 교육 공간
```
vinyl or terrazzo floor pattern and seam,
acoustic panel perforation depth, diffuse ceiling panel even glow,
matte wall paint subtle variation, handrail metal surface detail
```

### 전시부스 / 전시홀 (3종: 목공 · 블럭 · 옥타놈)
```
anodized aluminum post and beam edge specular highlight, panel-to-panel seam depth,
matte white melamine or PVC infill panel surface, fascia header band flatness,
grey needle-punch exhibition carpet pile, aluminum base rail edge,
overhead truss and spotlight specular, straight vertical frame lines preserved
```
유형별 추가(원본이 어느 부스인지에 맞춰 한 줄 선택):
- 목공부스: `smooth continuous painted or vinyl-wrapped wall surface, sharp clean flush corner, solid built wall`
- 블럭부스: `standardized rectangular box modules, fine consistent seams between modules, flat even matte panel faces` (발광은 원본 그래픽면에 있을 때만 국소적으로, 벽 전체 발광 금지)
- 그래픽 재료(원본에 보이는 1~2종만): `flat tight self-adhesive vinyl film (kelji) wrapped on wall, taut smooth SEG tension fabric matte surface, satin PVC flex banner, matte foam PVC board`
> 3종 공통으로 수직/수평 직선 보존이 생명이다. CGI 소스면 Creativity를 더 낮게(0.1~0.2) 잡아 격자·모서리 왜곡을 막는다. 옥타놈은 포스트가 패널보다 볼록 돌출된 seam을, 블럭부스는 균일한 박스 모듈 접합 그리드를, 목공은 이음매 없는 매끈면을 유지시킨다. 발광·광택 토큰을 여럿 겹치면 전면발광·bloom이 나므로 주 재료 1개에만 적용한다.

### 목록에 없는 공간 (fallback)
위 목록에 없는 공간(체육관, 종교시설, 공장 내부, 지하주차장 등)은 키워드 블록을 생략하거나 임의 창작하지 말고, **가장 유사한 블록을 선택**하거나 그 공간의 **바닥·벽·천장·조명 4요소**를 같은 형식(재료명 + micro-texture/seam/falloff 패턴)으로 직접 작성한다.

---
