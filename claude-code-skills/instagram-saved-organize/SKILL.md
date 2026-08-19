---
name: instagram-saved-organize
description: "인스타 보관함(Saved) 저장 게시물을 claude-in-chrome으로 전량 읽어 카테고리 분류→폴더 자동 생성→graphql(X-FB-LSD 헤더)로 자동 저장. 트리거 '보관함 정리'/'인스타 보관함 정리'. 월2회 정기(반자동: 로그인 브라우저 세션 필요)."
---

# 인스타 보관함 자동 정리 (Instagram Saved → Collections)

ASURA님(@nana80psh)이 인스타에 저장(보관)한 게시물을 주제별 컬렉션(폴더)에 **자동으로 넣는다**. 2026-07-07 방법 확립(대량 자동 저장 성공).

## 언제
- 사용자가 "보관함 정리" / "인스타 보관함 정리" 라고 할 때.
- 월2회 정기검토(1·15일) 리마인더 후 사용자가 PC에서 트리거할 때.

## ★ 핵심 제약 (반자동인 이유)
- **로그인된 크롬 세션 + 실시간 토큰(fb_dtsg, lsd)**이 필요 → 무인 헤드리스 브리지에선 불가. **claude-in-chrome(대화형)** 으로만.
- 봇방어: **1초당 1개** 페이싱 필수(초과 시 error 1357004/HTML 소프트차단 → 세션 로그아웃 위험). feed 연속읽기도 과하면 차단(8페이지씩 나눠 읽기).
- 그 크롬 탭을 **열어둔 채** 백그라운드 루프가 돈다(닫으면 멈춤 → window.__qi부터 재개).

## 절차 (claude-in-chrome)
1. 탭에서 `https://www.instagram.com/nana80psh/saved/all-posts/` 열고 로그인 확인(로그아웃이면 사용자에게 재로그인 요청 — 비번/OAuth 대행 금지).
2. **저장 게시물 전량 읽기**(캡션 포함): `GET /api/v1/feed/saved/posts/?count=50&max_id=<next>` 반복. headers `X-IG-App-ID:936619743392459`, credentials include. 응답 `items[].media.{code,pk,user.username,caption.text}` + `next_max_id`. **8페이지씩** 나눠 window.__data에 누적(CDP eval 45s 한도 회피, detached 루프면 무관).
3. **분류** (2026-08-05 개정 — 키워드 규칙 매칭에서 모델 판단으로 교체):
   `username + caption`(+ 캡션이 없으면 썸네일)을 보고 아래 카테고리 중 하나로 직접 판정한다.
   키워드 테이블을 만들어 매칭하지 않는다 — 규칙은 항상 예외에서 터지고, 예전 방식은
   캡션 없는 릴스를 대부분 "기타"로 흘려보냈다(구방식의 자인된 한계).

   | 카테고리 | 무엇이 들어가나 |
   |---|---|
   | 건축·전시 | 건물·공간·전시부스·행사장 |
   | AI 워크플로우·도구 | 모델·툴·파이프라인·프롬프트 기법 |
   | AI 이미지·아트 | 생성 이미지 결과물 |
   | AI 영상 | 생성 영상 결과물 |
   | 3D·Blender | 모델링·렌더·시뮬레이션 |
   | 아나모픽 LED | 아나모픽·포리스펙티브 LED 사이니지 |
   | 인터랙티브·이머시브 | 체험형 설치·미디어아트 |
   | 그래픽·모션·타이포 | 2D 그래픽·모션·타이포그래피 |
   | 제품·공간·오브제 | 가구·제품·오브제 |
   | 레퍼런스·기타 | **위 어디에도 확실히 안 들어갈 때만** |

   - "레퍼런스·기타"는 미매칭 자동 낙하 지점이 아니라 **적극적 판정**이다. 여기로 보낼 땐
     이유를 한 줄 남긴다.
   - 애매하면 억지로 밀어넣지 말고 그대로 두고 보고에 올린다. 오분류는 사용자가 옮기며 조정한다.
4. **폴더 확인/생성**: `GET /api/v1/collections/list/?collection_types=["MEDIA"]` **페이지네이션**(한번에 6개, next_max_id로 전량). 없는 카테고리는 `POST /api/v1/collections/create/` body `name=...` headers `X-CSRFToken`+`X-IG-App-ID`.
5. **증분(월2회 새 저장분만)**: 이전 처리한 code 집합을 `slack-claude-bridge/insta_saved_seen.json`(또는 AUSURA)에 저장 → 이번엔 새 code만 처리. **파일이 없으면(첫 실행) 전량을 신규로 처리하고 완료 시 파일을 새로 생성한다.** (전량 재처리는 idempotent라 무해하나 느림·불필요.)
6. **자동 저장(핵심)** — 각 게시물을 해당 폴더에 add:
   - 토큰 추출(페이지 소스 정규식): `fb_dtsg`=`"DTSGInitialData",[],{"token":"([^"]+)"`, `lsd`=`"LSD",[],{"token":"([^"]+)"`, `csrf`=쿠키 `csrftoken`.
   - `media_id` = **shortcode를 base64 디코드**(알파벳 `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_`, n=n*64+idx). = media pk. (검증됨, 피드 pk와 일치)
   - `POST /api/graphql` form-urlencoded body:
     `av=17841401657762943&__a=1&fb_dtsg=<dtsg>&lsd=<lsd>&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=PolarisAPIEditCollectionAddMediaMutation&variables=<{"input":{"collection_id","media_id","actor_id":"17841401657762943","client_mutation_id"}}>&server_timestamps=true&doc_id=27261476466806134`
   - **필수 헤더**: `Content-Type: application/x-www-form-urlencoded`, `X-CSRFToken`, `X-IG-App-ID:936619743392459`, **`X-FB-LSD:<lsd>`**(핵심 — 이거 빠지면 1357004), `X-ASBD-ID:129477`, `X-FB-Friendly-Name:PolarisAPIEditCollectionAddMediaMutation`.
   - 성공판정: 응답에 `xig_media_collection_add_media` 포함. `1357004`/`<`(HTML)/`for (;;);` → rate → 멈추고 ~40s 쿨다운 후 재개.
   - **페이싱 1초/개**. detached async 루프(`(async()=>{...})()`)로 window에 큐+토큰 두고 백그라운드 실행, `window.__qi/__ok/__fail` 폴링. actor_id `17841401657762943`는 @nana80psh 계정 pk.
7. 완료 후 요약 보고(폴더별 개수). seen.json 갱신.

## 주의
- 계정 리스크: 페이싱 지키면 안전(363개 연속 0실패 실증). 절대 무지연 연타 금지.
- 폴더 이동은 idempotent(이미 있으면 무해). 오분류는 사용자가 옮기며 조정.
- 상세 실증·레시피: memory `project_instagram_saved_organize`, AUSURA `AI-Sessions/wiki/playbooks/user-routines.md`.
