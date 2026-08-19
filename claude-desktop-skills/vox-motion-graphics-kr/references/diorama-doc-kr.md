# 종이 디오라마 다큐 스타일 (한국어판)

두 번째 하우스 스타일: 시네마틱 빈티지 종이 디오라마 다큐 — 세피아 신문지로
지은 세계, 검열바 컷아웃 인물, 번트오렌지 단일 액센트, 텅스텐 조명, 매크로
틸트시프트. 브리프에 시네마틱/드라마틱/탐사보도 느낌이 요구되거나, 주제가
지정학·돈·권력일 때 쓴다.

> **한국어판 최대 차이:** 원본 스타일의 시그니처인 "소품 위 레터프레스
> 텍스트"를 **한글로 쓸 수 없다.** 생성 모델이 한글을 못 그린다. 아래
> 대체 전략을 따른다.

## 스타일 키

이미 생성된 재사용 스타일 키가 있다 — 다시 만들지 말고 잡 id를 이미지
레퍼런스로 붙인다:

```
STYLE KEY (diorama): 0561c26f-ad53-44da-815d-a8796d32d864
```

새 키가 필요하면 이 프롬프트로 만든다 (`generate_image`, `nano_banana_pro`,
16:9):

```
Cinematic vintage paper diorama style swatch, documentary collage
aesthetic: a miniature three-dimensional landscape built entirely from
aged sepia newspaper sheets and cardboard, torn edges, layered paper
canyon walls of old newsprint, monochrome archival photo cutouts of
anonymous suited figures standing among the paper structures with black
censor bars over their eyes, one dominant burnt-orange paper prop as the
single color accent against the sepia world, distressed letterpress print
texture, warm tungsten documentary lighting with deep shadows, macro
tilt-shift lens look with shallow depth of field, film grain and dust.
Handcrafted physical paper materials only — no letters, no words, no
numbers, no logos, no Korean characters, no Hangul. Non-photorealistic
scene content, no live-action people, stylized paper craft world.
```

## STYLE 토큰 (모든 클립 프롬프트를 이걸로 연다)

```
cinematic vintage paper diorama, aged sepia newsprint world, monochrome
halftone print, monochrome archival cutout figures with black censor bars
over their eyes, single burnt-orange accent, distressed letterpress,
warm tungsten light, macro tilt-shift shallow depth of field, film grain,
handcrafted stop-motion paper feel, non-photorealistic, no live-action
```

## 소품 타이포그래피 — 한국어판 규칙

원본은 소품에 짧은 레터프레스 텍스트를 얹는 게 시그니처다("EXPIRED",
"1,000", "WHO BLINKS?"). 한국어판은 이렇게 처리한다:

| 상황 | 처리 |
|---|---|
| 한글 문구를 소품에 얹고 싶다 | **금지.** 조립 후 오버레이 레이어로 얹는다 |
| 숫자를 얹고 싶다 | **아라비아 숫자만 허용** (`1953`, `15`, `2026`). 비교적 안정적으로 렌더된다. 그래도 결과를 눈으로 확인 |
| 영문 단어를 얹고 싶다 | 가능하지만 **1~2단어까지**. 한국 시청자 대상 영상에 영문 라벨이 자연스러운지 먼저 판단 |
| 신문 헤드라인 | 글자 없는 조판 — 텍스트 자리를 하프톤 블록·먹칠 바로 |
| 도장·스탬프 | 글자 없이 **형태만**(원형 인장, 잉크 번짐). 문구는 오버레이로 |

숫자 하나를 의도적으로 넣을 때의 네거티브 예외 구문:

```
No text anywhere except the numerals "1953". No Korean characters, no Hangul,
no gibberish letters, no captions, no watermark.
```

**질문 훅을 소품에 얹는 연출**(원본의 "WHO BLINKS?" 같은)은 한국어판에서
이렇게 바꾼다: 소품에는 **빈 종이나 먹칠된 자리**를 만들어두고, 조립 후
그 자리에 한글 문구를 얹는다. 카메라가 그 소품을 클로즈업하는 타이밍을
프롬프트에 명시해두면 오버레이 붙일 지점이 명확해진다.

## 재사용 소품 에셋

플레인 배경에 1:1로, 스타일 키를 참조해 생성된 것들 — 스타일 키와 함께 추가
`image_references`로 넘기고 프롬프트에 "the X from the reference image"라고
써서 클립 사이에 물체가 변형되지 않게 한다:

| 소품 | 잡 id |
|---|---|
| 종이 미사일 (오렌지 탄두) | 0cb0ada4-5376-44fe-8950-822425825336 |
| 낡은 신문 1면 (검열바 인물) | 4cf403d1-6791-4661-af13-7d61330accdd |
| 화약통 + 도화선 | 68d803d1-3876-4410-9be4-9d800f6913be |
| 지도자 컷아웃 3인 (미/러/중) | bd35a771-ddd9-456f-827a-18027293d1b0 |

※ 위 소품 중 문구가 인쇄된 것(화약통의 "WHO BLINKS?")은 영문이다. 한국어
영상에서 그대로 쓰면 어색할 수 있으니, 필요하면 문구 없는 버전을 새로 만든다.

새 소품: `generate_image` + `nano_banana_pro`, 1:1, 스타일 키 첨부,
"Single reusable prop asset, centered on a plain warm off-white paper
background… Nothing else in frame. No letters, no Hangul."

## 엔진: seedance_2_0 (레퍼런스급)

```
generate_video
  model: "seedance_2_0"
  duration: 10
  resolution: "720p"        # 45크레딧; 1080p = 90크레딧
  mode: "std"
  aspect_ratio: "16:9"
  genre: "noir"             # 클립 전반에 일관된 어두운 그레이딩
  generate_audio: true      # 네이티브 SFX/드론 사운드 디자인 — 유지할 것
  medias: [ { value: "<스타일 키>", role: "image_references" }, …소품들 ]
```

시댄스는 프롬프트 안의 컷("Shot 1 … Cut to shot 2 …")을 실행하고, "speed
ramp", "FPV", "whip pan"을 문자 그대로 읽고, 진짜 불꽃·불티를 아름답게
렌더한다. 네이티브 오디오(도화선 타는 소리, 드론, 임팩트)는 조립 후
나레이션 아래에서도 살아남는다 — 프롬프트에서 설계할 것
("Sound design: … No speech.").

`gemini_omni`(30크레딧)가 폴백이다. 특이하게, 시댄스가 거부하는 **알아볼 수
있는 정치인 얼굴**을 묘사만으로 렌더한다(모더레이션 노트 참조).

## 페이크 원테이크 블록 프롬프트 형태

모든 클립 = 하나의 연속 카메라 무브. 모든 경계를 모션블러에 숨겨서 하드컷이
끊기지 않은 한 샷처럼 읽히게 한다:

```
<STYLE 토큰> — shot as ONE continuous high-energy FPV camera move with
aggressive speed ramps.
The shot: [emerges from motion-blurred <이전 요소>] … [3초마다 임팩트 순간
하나: slam / stamp / shockwave / snap] … [ends fully motion-blurred
mid-<dive/whip/fall/flare>].
Composition: keep the lower ~17% of the frame visually quiet — no key subject
in that band.
Sound design: [구체적인 다이제틱 이벤트 3~5개]. No speech.
No text anywhere. No Korean characters, no Hangul, no gibberish letters,
no captions, no watermark, no photorealism, no live-action.
```

작업 예시 (한국어판 오프닝 블록 — 텍스트를 뺀 버전):

```
…shot as ONE continuous high-energy FPV camera move with aggressive speed
ramps.
The shot: from black, EXTREME slow-motion macro of a halftone-printed
human eye on newsprint as a thick black censor bar SLAMS down over it
like a guillotine, paper dust exploding on impact. Violent speed-ramp
pull-back reveals it is a giant newspaper front-page portrait of an elderly
statesman in a dark suit; a gust RIPS the page away revealing a second
portrait — a compact stern figure — ripped away again to a third, each rip
faster than the last. The camera then DIVES at full speed into a tearing gap
in a giant aged document as a burnt-orange circular ink stamp punches down
across it, ink spreading through the fibers; the lens plunges through the
torn paper into swirling dust, ending mid-dive fully motion-blurred.
Composition: keep the lower ~17% of the frame visually quiet.
Sound design: guillotine slam with dust whump, three accelerating page
rips, one massive stamp punch, rushing paper wind. No speech.
No text anywhere. No Korean characters, no Hangul, no gibberish letters,
no captions, no watermark, no photorealism, no live-action.
```

원본과 비교하면 도장에 찍히던 "EXPIRED" 글자가 **형태만 있는 원형 인장**으로
바뀌었다. "만료"라는 한글이 필요하면 조립 후 그 프레임에 오버레이로 얹는다.

## 모더레이션 맵 (실전에서 얻은 것)

- **영상 프롬프트에 정치인 실명 → 잡 실패.** 시댄스에서 제출은 되는데 렌더에서
  죽는다. 실명은 TTS 나레이션에서는 괜찮다.
- **알아볼 수 있는 정치인 얼굴 클로즈업** (실명 없이 묘사만 해도) → 시댄스 실패.
  **`gemini_omni`는 렌더한다** — 얼굴이 정면으로 나오는 블록은 제미나이로
  돌리되 같은 스타일 키를 유지한다.
- 미들샷/전신의 "빨간 넥타이를 맨 지도자", "체구가 작은 러시아 인물",
  "동아시아 정치인" 같은 묘사는 **양쪽 엔진 모두 통과.** 눈 위 검열바는
  에디토리얼 룩을 살리는 동시에 초상권 문제도 완화한다.
- **"버섯구름" → nsfw 플래그.** 다른 실루엣으로 대체한다(모래시계가 잘 통했고
  마감 시한이라는 주제에도 더 맞았다).
- 서버가 스타일라이즈드 프롬프트를 `preset_recommendation` 알림으로 가로챈다
  (3D RENDER / IN THE DARK / DROWN IN MUSIC / FREE FALL…). 절대 수락하지 말고
  `retry_literal_with`의 `declined_preset_id`를 넣어 재제출한다. 이 id는 그
  프리셋 하나만 억제하므로, 새 프롬프트가 다른 프리셋을 건드릴 수 있다.

### 한국 관련 추가 주의

- 실존 한국 정치인·기업인은 위 규칙이 그대로 적용된다. 협찬·광고 영상이면
  아예 넣지 않는 게 안전하다.
- 북한 관련 소재(군사 퍼레이드, 미사일 등)는 nsfw/폭력 플래그 확률이 높다.
  추상 실루엣이나 지도 형태로 우회한다.
- 태극기·한글 현판 등은 렌더 품질 문제가 겹친다. 국가를 표현해야 하면 지도
  실루엣이나 단색 컬러 코딩을 쓴다.

## 음악

이 MCP를 통해 쓸 수 있는 독립 음악 모델은 없다(sonilo_music은 게임
파이프라인 전용 — 거절하고 대체하지 말 것). 선택지: 시댄스의 네이티브
드론/SFX 베드에 의존하거나(대개 충분하다), 외부 생성기(Suno/Udio)에 브리프를
주고 로컬에서 믹스한다.

레퍼런스와 잘 맞았던 브리프: 약 46 BPM 심장박동 펄스, 서브베이스 드론 + 낮은
첼로, 고음역 거의 없음, 8초 호흡 스웰, 크게 열고, 러닝타임 80% 지점에 클라이맥스
하나, 급격히 무음으로 감쇠.
