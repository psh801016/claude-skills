# [작업지시 — 코덱스] slack-claude-bridge 음성명령 처리 추가

> 작성: Claude (2026-08-05) · 대상: 코덱스(로컬, `C:\Users\PSH` 접근 가능)
> 이 문서 하나만 읽고 처음부터 다시 설계하지 말 것. 진단은 끝나 있다.

---

## 0. 배경 — 이미 확정된 사실 (재조사 금지)

**증상**: 슬랙 `#hermes-자비스` 에 음성 메모를 보내면 전사되지 않고 실패한다.

```
⏳ 답변 생성 중.
❌ 첨부 이미지 전달 실패
지원되는 이미지 첨부가 없습니다.
```

**슬랙 원본 실측** (2026-08-05 확인, 재확인 불필요):

| 항목 | 값 |
|---|---|
| 채널 | `#hermes-자비스` (`C0BHUNMETDJ`) |
| 부모 메시지 ts | `1785846192.903279` (2026-08-04 21:23:12 KST) |
| 첨부 | `오디오 클립 (2026-08-04 21:23:09).m4a` |
| mimetype | **`audio/mp4`** · 301.6 KB · `subtype: slack_audio` |
| 봇 응답 | 21:23:16 — 업로드 **4초 뒤** |

**확정된 원인**: 브리지의 첨부 처리기가 **이미지 mimetype 만 통과시키는 필터**라
`audio/mp4` 가 걸러진다. 4초 만에 떨어진 것은 다운로드 실패가 아니라 필터에서
즉시 걸렸다는 뜻이다. **음성→텍스트(STT) 단계가 파이프라인에 아예 없다.**

**아닌 것들** (이미 배제됨, 다시 파지 말 것):
- 이 봇은 Nous Research 의 Hermes Agent 제품이 **아니다.** `C:\Users\PSH\slack-claude-bridge` 다.
  → `~/.hermes/config.yaml`, `stt_enabled`, `stt.language` 는 이 환경에 존재하지 않는다.
- `files:read` 스코프 누락이 **직접 원인은 아니다.** (필터가 먼저 걸렀다.)
  단, 오디오 분기를 붙인 뒤 파일을 실제로 받으려면 필요하다 — §4 참조.

---

## 1. 목표

브리지가 슬랙 음성 메모를 받으면 **전사해서 텍스트 명령과 똑같이 처리**하게 만든다.

완료 조건: 슬랙에 음성 메모를 보내면 봇이 그 내용을 알아듣고 평소처럼 응답한다.

---

## 2. 제약 (ASURA 규칙 — 반드시 지킬 것)

- **승인 없이 프로세스 재시작·종료 금지.** 재시작이 필요하면 그 사실을 보고하고 멈춘다.
- 파일 쓰기는 **아래 명시된 파일에만.** 그 외 파일 수정 금지.
- **fail-loud**: 실행 실패한 항목은 실패했다고 명시한다. 조용히 넘어가지 않는다.
- 출력은 원문 그대로. 요약 금지.
- 손대기 전 **백업 필수** (§3-2).

---

## 3. 작업 단계

### Step 0 — 첨부 처리 코드 위치 특정 (조회 전용)

아래를 실행하고 **출력 원문을 그대로** 보고할 것. 아직 아무것도 고치지 않는다.

```powershell
Select-String -Path C:\Users\PSH\slack-claude-bridge\*.py `
  -Pattern 'mimetype|image/|지원되는 이미지|첨부 이미지|files' -Context 3,3
```

```powershell
Get-ChildItem C:\Users\PSH\slack-claude-bridge -Filter *.py |
  Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
```

목표: **`지원되는 이미지 첨부가 없습니다` 문자열이 있는 파일과 줄번호**, 그리고
그 주변에서 `files` 를 순회하며 mimetype 을 검사하는 함수를 특정한다.

### Step 1 — 모듈 배치

`slack_audio.py` 를 브리지 폴더에 넣는다. (이 문서와 같은 폴더에 있다.)

```powershell
Copy-Item <이 문서 폴더>\slack_audio.py C:\Users\PSH\slack-claude-bridge\slack_audio.py
```

**인코딩 주의**: 이 파일에는 한글 문자열이 있다. **UTF-8 로 저장돼야 한다.**
(이 브리지 환경에서 과거 cp949 로 한글이 `?` 로 깨진 이력이 있다.) 복사 후 확인:

```powershell
python C:\Users\PSH\slack-claude-bridge\slack_audio.py --selftest
```

**기대: `11/11 통과`.** 여기서 실패하면 다음으로 넘어가지 말고 출력을 보고할 것.

### Step 2 — 백업

```powershell
Copy-Item C:\Users\PSH\slack-claude-bridge\<Step0에서찾은파일>.py `
  C:\Users\PSH\slack-claude-bridge\<파일>.py.bak-20260805
```

### Step 3 — 분기 삽입

Step 0 에서 찾은 첨부 처리 자리에 아래를 넣는다. **기존 이미지 경로는 그대로 두고,
오디오 분기를 앞에 추가**하는 형태다.

```python
from slack_audio import is_audio_file, describe_attachment, transcribe_slack_audio

# --- 첨부 분기 ---
audio_files = [f for f in files if is_audio_file(f)]

if audio_files:
    try:
        spoken = transcribe_slack_audio(
            audio_files[0], SLACK_BOT_TOKEN, language="ko"
        )
    except Exception as exc:
        say(f"❌ 음성 전사 실패\n{exc}")      # fail-loud
        return
    user_text = f"{user_text}\n{spoken}".strip() if user_text else spoken
    # 이후는 텍스트 명령과 완전히 동일한 경로로 진행

elif image_files:
    ...   # 기존 이미지 처리 그대로

elif files:
    # "이미지 없음" 으로 뭉뚱그리지 말고 실제로 뭐가 왔는지 밝힌다
    say("❌ 지원하지 않는 첨부: "
        + ", ".join(describe_attachment(f) for f in files))
```

**변수명은 브리지 실제 코드에 맞출 것.** `files` / `user_text` / `say` /
`SLACK_BOT_TOKEN` 은 자리표시자다. 실제 이름으로 바꿔서 넣는다.

`SLACK_BOT_TOKEN` 은 `xoxb-` 로 시작하는 **봇 토큰**이어야 한다. 앱 토큰
(`xapp-`) 이나 유저 토큰이 아니다.

### Step 4 — 전사 엔진 확보

`slack_audio.py` 는 있는 것부터 자동으로 고른다: faster-whisper(로컬) → Groq → OpenAI.

현재 무엇이 쓸 수 있는지 확인:

```powershell
python -c "import faster_whisper; print('faster-whisper OK')"
echo "GROQ_API_KEY: $([bool]$env:GROQ_API_KEY)"
echo "OPENAI: $([bool]($env:VOICE_TOOLS_OPENAI_KEY + $env:OPENAI_API_KEY))"
```

셋 다 없으면 하나는 갖춰야 한다. **판단 근거:**

- **Groq 권장** — 무료 티어가 있고 빠르다(수 초). `GROQ_API_KEY` 환경변수만 넣으면 된다.
- **로컬 faster-whisper** — 키가 필요 없지만 CPU 로 30초짜리 클립에 수십 초가 걸릴 수 있다.
  ⚠️ **이 브리지에는 워치독이 붙어 있다.** 전사가 오래 걸려 응답이 지연되면 워치독이
  브리지를 재시작할 수 있으니, 로컬로 갈 거면 워치독 타임아웃을 먼저 확인할 것.
  한국어는 `base` 로 부족하니 `small` 이상이어야 하고, 그만큼 더 느리다.

키 설치는 **ASURA 승인 사항**이다. 임의로 결제·가입하지 말 것.

### Step 5 — 검증

1. `python slack_audio.py --selftest` → `11/11 통과`
2. 브리지 재시작은 **승인 후에.** 승인 없이 재시작 금지(§2).
3. 재시작 승인이 나면 슬랙에 **실제 음성 메모**를 보내 확인한다.
   - 성공: 봇이 말한 내용을 알아듣고 응답
   - 실패: 봇이 뱉은 에러 원문을 그대로 보고

### Step 6 — 롤백 (문제 발생 시)

```powershell
Copy-Item C:\Users\PSH\slack-claude-bridge\<파일>.py.bak-20260805 `
  C:\Users\PSH\slack-claude-bridge\<파일>.py -Force
```
재시작은 역시 승인 후.

---

## 4. 사람이 해야 하는 것 (코덱스가 못 함)

슬랙 앱에 **`files:read` 스코프**가 없으면 오디오 분기를 붙여도 파일을 못 받는다.
`slack_audio.py` 는 이 경우를 감지해서 이렇게 알려준다:

> 파일 대신 HTML 이 내려왔습니다 — 토큰에 files:read 권한이 없습니다.

이 메시지가 뜨면 ASURA 가 직접:
1. <https://api.slack.com/apps> → 해당 앱 → **OAuth & Permissions**
2. Bot Token Scopes 에 `files:read` 추가
3. **Reinstall to Workspace** (재설치 안 하면 기존 토큰에 권한이 안 붙는다)

---

## 5. 완료 보고 형식

```
[완료] Step 0~5 중 어디까지
[변경 파일] 경로 + 줄번호 범위
[selftest] 11/11 통과 여부
[전사 엔진] 무엇을 쓰기로 했는지
[실패 항목] 있으면 원문 그대로 (fail-loud)
[승인 대기] 재시작 / API 키 등
```

---

## 6. 참고 — `slack_audio.py` 가 이미 처리하는 것

다시 구현하지 말 것. 검증까지 끝나 있다(판별 11건 + 다운로드 6건).

- 오디오 판별: mimetype → subtype → filetype → 확장자 순 폴백
  (슬랙이 mimetype 을 비워 보내는 경우 대응)
- 슬랙 비공개 파일 다운로드: `url_private_download` + Bearer 인증
- 권한 없을 때 슬랙이 **HTTP 200 으로 주는 로그인 HTML** 을 파일로 오인하지 않고 차단
- 전사 엔진 자동 폴백 + 전부 실패 시 "무엇이 없어서 실패했는지" 전부 적어서 예외
- 임시 파일 정리
- 표준 라이브러리만 사용 (`requests`·SDK 불필요)

**미검증**: 전사 엔진 실호출(키·오디오가 없어 못 돌려봄). Step 5 가 그 검증이다.
