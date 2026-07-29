# 바미싱 PVC 플렉스 현수막

사용자가 `바미싱`, `상하단 바미싱`, `프레임 안 보이는 현수막`, `프레임 없는 플렉스`를 선언하면 이 문서를 전시부스 분류기와 함께 읽는다.

## 판정과 우선순위

1. 사용자의 바미싱 선언은 해당 그래픽면의 시공 사실이다. CGI에서 프레임처럼 보이는 약한 선보다 우선한다.
2. 바미싱은 독립 그래픽면 마감이다. 해당 면을 옥타늄 인필, 블럭 패널, 목공벽으로 재분류하지 않는다.
3. 상·하단 장력 바는 숨겨진 시공 방식일 뿐 화면에 보이는 물체가 아니다. 프롬프트에 바·레일·프레임을 그리게 하지 않는다.
4. 현수막 면과 구조 빔은 반드시 별도 구역으로 판정한다. 원본 또는 사용자 선언에서 보이는 맥시마 세로 빔만 별도 `maxima` 구역으로 남길 수 있다.

## 그래픽면 표현 계약

바미싱 그래픽면에만 다음 앵커를 쓴다.

`the source-confirmed graphic zone reads as one continuous full-bleed opaque PVC flex banner face tensioned by concealed sewn pole pockets at the top and bottom, with the internal rods fully hidden inside the rod-pocket sleeves; the visible graphic face remains smooth, near-planar and uniformly taut across its exact source-defined rectangle, with realism limited to fine low-sheen vinyl-scrim microtexture and soft even grazing-light response, while the exact original artwork and every source-visible division remain preserved`

`bar-missing`은 한국 현장어 `바미싱`을 영어 단어처럼 옮긴 표현이라 생성 모델 입력에 쓰지 않는다. 생성 프롬프트에서는 실제 제작 방식을 뜻하는 `concealed sewn top-and-bottom pole pockets` 또는 `rod-pocket sleeves with the internal rods fully hidden`만 사용한다.

바미싱 그래픽면에는 다음을 넣지 않는다.

- visible top bar, bottom bar, side rail, base rail, aluminum perimeter frame, exposed Octanorm post, silver edge profile
- block-panel seam, rigid panel thickness, recessed joint, screw, rivet, grommet, eyelet, visible stitch line, deep fold, sharp wrinkle, or any new division not present in the source
- graphic-face border를 만드는 새 포털·캐노피·벽체·기둥

## 맥시마 빔과의 결합

이 사용자의 전시 작업에서 `맥시마 빔`은 항상 내부발광 구조 부재다. 그것을 바미싱 그래픽면의 프레임이나 별도 라이트박스로 재설계하지 않고, **그래픽면과 인접한 별도 발광 골격 구역**으로 표현한다.

맥시마가 있는 이미지에서는 현수막 재질 보정 문단을 단독 출력하거나 단독 입력하라고 안내하지 않는다. 현수막만 다루는 짧은 문장이 발광·빔 형상 지시를 밀어내면 모델이 맥시마를 비발광 청색 구조 또는 일반 패널 테두리로 바꾸기 때문이다. 복사용 Magnific 문장은 항상 `모든 원본 맥시마 빔의 내부발광·형상·코어 폭·위치 고정` 문장과 `현수막 평면 재질` 문장을 하나의 연속 프롬프트에 함께 넣는다.

`each source-visible Maxima beam remains the exact original internally illuminated structural member, consisting only of an opaque deep-cobalt low-sheen aluminum casing and the single narrow flush translucent opal diffuser core already visible in Image 1; preserve the exact source casing-to-core ratio, luminous-pixel footprint, beam silhouette and junctions, with controlled local cyan spill limited to only the immediately adjacent banner edge and floor already affected in Image 1`

빔 라이트를 강화하라는 요청이 있으면, 원본 코어 폭을 유지한 채 코어 휘도와 원본에 이미 존재하는 인접 반사만 강화한다. 코어 폭·발광 픽셀 면적·케이싱 폭·개구부 면적은 바꾸지 않는다.

사용자 실사 시공사진 전수판독 결과, 현수막과 맥시마는 다음처럼 분리한다.

- 맥시마: 실제 두께와 측면 리턴이 있는 발광 구조빔. 불투명 청색 케이싱과 같은 실루엣 안의 연속 오팔 확산 발광면으로 읽고, 반복 LED 점 없이 완만한 실사 밝기 편차만 허용한다.
- 현수막: 맥시마 안쪽 또는 뒤쪽의 별도 불투명 PVC 플렉스 인쇄면. 상·하단 숨은 바미싱 장력으로 팽팽하고 거의 평면인 인쇄면을 유지하며, 저광택 비닐 스크림과 균일한 사광 반응만 미세하게 표현한다. 프린트 면 자체는 발광시키지 않는다.
- 상부 집게형 스포트라이트, 레드카펫, 모니터, 카운터 구성, 은색 시스템 프로파일은 참조사진의 별도 시공요소다. Image 1에 이미 있는 요소만 유지하고 다른 장면으로 가져오지 않는다.

## 혼합부스 조립 게이트

1. 바미싱 현수막 면: 위 바미싱 앵커 하나만.
2. 맥시마 빔 면: 원본에서 보이는 빔에만 맥시마 앵커 하나만.
3. 옥타늄 또는 블럭 표현은 해당 구조 증거 또는 사용자 선언이 있는 별도 구역에만 쓴다.
4. 프롬프트 전 확인: 바미싱 면에 `frame`, `rail`, `base rail`, `post`, `panel seam`, `joint`가 남아 있으면 반려하고 다시 조립한다.
5. 원본 그래픽·텍스트·로고는 최종 후보 위에 원본 아트워크로 복원한다.
