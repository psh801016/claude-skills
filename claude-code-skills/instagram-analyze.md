# Instagram 계정 분석 + 자료 정리 스킬

인스타그램 계정을 Apify MCP로 스크래핑하여 분석 대시보드를 만들고, 이미지를 Google Drive에 카테고리별로 정리합니다.

## 입력값
사용자 입력: **$ARGUMENTS**

- URL 형태: `https://www.instagram.com/USERNAME/` → USERNAME 추출
- @형태: `@USERNAME` → USERNAME 추출  
- 계정명만: `USERNAME` → 그대로 사용

입력값이 없으면 분석할 Instagram 계정 URL 또는 @계정명을 물어본다.

---

## 실행 절차

### STEP 1 — 계정명 파싱
- 입력값에서 Instagram username을 추출한다
- URL 형태(`https://www.instagram.com/USERNAME/`)와 `@USERNAME` 형태 모두 처리

### STEP 2 — Apify로 프로필 스크래핑
`mcp__Apify__call-actor`를 두 번 호출한다:

**2-A. 프로필 정보 수집**
```json
{
  "actorId": "apify/instagram-scraper",
  "input": {
    "directUrls": ["https://www.instagram.com/{USERNAME}/"],
    "resultsType": "details",
    "resultsLimit": 1
  }
}
```

**2-B. 게시물 피드 수집**
```json
{
  "actorId": "apify/instagram-scraper", 
  "input": {
    "directUrls": ["https://www.instagram.com/{USERNAME}/"],
    "resultsType": "posts",
    "resultsLimit": 50
  }
}
```

두 런이 완료될 때까지 `mcp__Apify__get-actor-run`으로 상태를 확인하고, 완료되면 `mcp__Apify__get-actor-output`으로 결과를 가져온다.

> ⚠️ get-actor-output 시 `fields` 파라미터로 필요한 필드만 요청해 토큰 초과를 방지:
> - 프로필: `id, username, fullName, biography, followersCount, followsCount, postsCount`
> - 게시물: `shortCode, caption, likesCount, commentsCount, timestamp, type, displayUrl, url`
> - `images` 필드는 요청하지 않는다 (토큰 초과 원인)

### STEP 3 — 데이터 분석 및 가공
수집된 데이터에서 아래 항목을 계산한다:
- 팔로워 수, 팔로잉 수, 총 게시물 수
- 게시물당 평균 좋아요 / 평균 댓글
- 참여율 ER = (평균 좋아요 + 평균 댓글) / 팔로워 × 100
- 게시물 유형 분포 (Sidecar 캐러셀 / Image / Video)
- 날짜별 게시 빈도
- 해시태그 빈도 분석 (caption에서 추출)
- 좋아요 TOP 9 게시물
- 업종·제품 키워드를 파악해 카테고리 분류 (8~10개 카테고리 자동 제안)

### STEP 4 — 분석 대시보드 HTML 생성
`C:\Users\PSH\Desktop\{USERNAME}_분석리포트.html`에 다음을 포함하는 다크 테마 HTML을 생성한다:

**필수 섹션:**
1. 헤더 — 계정명, 팔로워/팔로잉/게시물 수, 프로필 요약
2. 핵심 지표 카드 4개 — 평균 좋아요, 평균 댓글, 참여율(ER), 최다 좋아요
3. Chart.js 차트 3개:
   - 도넛: 게시물 유형 분포
   - 라인: 최근 좋아요 추이 (최신순)
   - 바: 날짜별 게시물 수
4. 해시태그 빈도 바 (상위 12개)
5. TOP 9 게시물 그리드 (좋아요 순, Instagram 링크)
6. 최근 게시물 갤러리 (최대 24개, Instagram 링크)
7. 인사이트 카드 6개 — 분석 결과 기반 한국어 개선 제안

**스타일 기준:**
- 배경: `#0f0f1a`, 카드: `#1a1a2e`
- 메인 컬러: `#e91e8c` (계정 성격에 따라 조정)
- Chart.js 4.4.0 CDN 사용
- 모바일 반응형

### STEP 5 — Google Drive 이미지 폴더 구조 제안
수집된 게시물 내용을 분석해 8~10개 카테고리를 자동 제안하고, 아래 폴더 구조를 `G:\내 드라이브\{USERNAME}\`에 생성한다:

```powershell
$folders = @(
  "01_{카테고리A}",
  "02_{카테고리B}",
  ...
  "08_매장_홍보",
  "09_포스터_디자인자료"
)
foreach ($f in $folders) {
  New-Item -ItemType Directory -Path "G:\내 드라이브\{USERNAME}\$f" -Force | Out-Null
}
```

### STEP 6 — 브라우저에서 이미지 일괄 다운로드 (선택)
> Apify CDN URL은 IP 인증 제한으로 직접 다운로드 불가 → 브라우저 세션을 활용

Chrome MCP로 Instagram 계정 페이지를 열고:

1. `mcp__Claude_in_Chrome__navigate` → `https://www.instagram.com/{USERNAME}/`
2. Instagram 내부 API로 전체 게시물의 CDN URL을 브라우저 세션 기준으로 수집:
   ```javascript
   // /api/v1/users/web_profile_info/?username={USERNAME} 로 userId 획득
   // /api/v1/feed/user/{userId}/?count=50 로 미디어 URL 수집 (페이지네이션)
   ```
3. 각 게시물을 `{카테고리폴더}_{제목}_{날짜}.jpg` 파일명으로 매핑
4. 페이지에 File System Access API 버튼을 주입:
   ```javascript
   // 사용자가 Google Drive 폴더 선택 → fetch+blob으로 직접 파일 쓰기
   // window.showDirectoryPicker() → dirHandle.getDirectoryHandle() → fileHandle.createWritable()
   ```
5. 사용자에게 버튼 클릭 안내 → 자동 분류 저장

### STEP 7 — 포스터 디자인 자료 생성
`G:\내 드라이브\{USERNAME}\09_포스터_디자인자료\` 안에 4개 파일 생성:
- `브랜드_가이드.html` — 계정 분석 기반 색상·톤앤매너·키워드
- `카피_뱅크.html` — 카테고리별 포스터 문구 + 해시태그 뱅크
- `클로드디자인_프롬프트.html` — 카테고리별 Claude Design 요청 프롬프트 템플릿
- `홍보포스터_MD.html` — 계정 특성에 맞춘 포스터 목업 4~6종
- `수강생모집_MD.html` — 클래스/강의 모집 포스터 목업 (해당 시)

---

## 실행 순서 요약

```
1. username 파싱
2. Apify 프로필 스크래핑 (details)
3. Apify 게시물 스크래핑 (posts, max 50)
   └─ 두 런 동시 시작 → 완료 대기
4. 데이터 분석 (ER, 해시태그, 카테고리 추출)
5. 분석 HTML 생성 → Desktop 저장
6. Google Drive 폴더 구조 생성
7. Chrome MCP 이미지 다운로드 버튼 주입
8. 포스터 디자인 자료 4~5개 파일 생성
```

---

## 오류 처리

| 상황 | 대응 |
|------|------|
| Apify 런 FAILED | `mcp__Apify__get-actor-run`으로 에러 확인 후 재시도 1회 |
| 토큰 초과 | `fields` 파라미터로 필드 제한, images 필드 제외 |
| G:\내 드라이브 없음 | Desktop에 폴더 생성 후 사용자에게 안내 |
| Chrome MCP 미연결 | 다운로드 스크립트(.ps1) 생성으로 대체 |
| CDN 403 오류 | File System Access API 버튼 방식으로 전환 |
| 비공개 계정 | 스크래핑 불가 안내, 공개 계정만 가능 설명 |

---

## 출력물 목록

실행 완료 시 다음 파일들이 생성됩니다:

```
Desktop/
└── {USERNAME}_분석리포트.html        ← 분석 대시보드

G:\내 드라이브\{USERNAME}\
├── 01_{카테고리}/                     ← 이미지 폴더들
├── ...
├── 0N_{카테고리}/
├── {USERNAME}_분석리포트.html         ← 사본
└── 09_포스터_디자인자료\
    ├── 브랜드_가이드.html
    ├── 카피_뱅크.html
    ├── 클로드디자인_프롬프트.html
    ├── 홍보포스터_MD.html
    └── 수강생모집_MD.html
```

---

## 참고 — Apify Actor ID

| 스크래퍼 | Actor ID | 비고 |
|----------|----------|------|
| 인스타그램 (공식) | `apify/instagram-scraper` | 99.8% 성공률, 270K 사용자 |
| 인스타그램 대안 | `zuzka/instagram-scraper` | 백업용 |
