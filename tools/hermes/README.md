# Hermes 음성명령 복구 절차

> ## ⚠️ 먼저 읽을 것 — 이 도구는 ASURA 환경에 적용되지 않는다 (2026-08-05 확인)
>
> 이 폴더의 `hermes-voice-fix.py` 는 **Nous Research 의 Hermes Agent 제품**
> (`~/.hermes/config.yaml` 을 쓰는 그것) 을 전제로 만들었다.
>
> 그런데 슬랙에서 실제로 응답하는 `Hermes · 자비스` 봇은 그 제품이 아니라
> **ASURA 가 직접 만든 로컬 파이썬 브리지 `C:\Users\PSH\slack-claude-bridge`** 다.
> 근거: 에러 문구가 GitHub 전체 코드 검색 0건(자체 코드 문자열), 같은 채널에서
> `server.py`·`commands.py`·`watchdog.ps1`·`bridge.log` 디버깅, 봇이 스스로
> "로컬 자비스" 라 칭하며 `G:\내 드라이브\` 에 산출물 기록.
>
> **따라서 아래 2단계(config.yaml 편집)는 이 환경에서 할 일이 없다.**
> 실제로 고칠 곳은 브리지의 첨부 처리 코드다 — 맨 아래 "실제 고칠 지점" 참조.
>
> 이 문서의 1단계(`files:read` 스코프)와 STT 개념은 어느 구현이든 유효하다.
> 스크립트는 나중에 Hermes Agent 제품을 실제로 쓰게 될 때를 위해 남겨둔다.

**증상** — 슬랙에서 Hermes·자비스에게 음성 메모를 보내면 전사되지 않고 이렇게 끝난다:

```
⏳ 답변 생성 중.
❌ 첨부 이미지 전달 실패
지원되는 이미지 첨부가 없습니다.
```

> **아래 1·2단계는 Hermes Agent 제품을 쓸 때의 절차다.** ASURA 환경의 실제
> 원인은 맨 아래 "실제 고칠 지점" 에 있다 — 봇이 4초 만에 실패한 것으로 보아
> 다운로드 실패가 아니라 **mimetype 필터에서 즉시 걸린 것**이다.

---

## 1단계 — 슬랙 `files:read` 스코프 (구현과 무관하게 필요)

첨부를 내려받으려면 어떤 구현이든 이 스코프가 있어야 한다. 없으면 봇이 대화는
해도 업로드된 파일을 못 읽는다. 이번 건의 직접 원인은 아니었지만(필터가 먼저
걸렀다), 오디오 분기를 붙인 뒤 실제로 파일을 받으려면 반드시 필요하다.

Hermes 공식 트러블슈팅의 관련 항목:

> Bot can chat but can't read uploaded images/files — Add `files:read`, then **reinstall** the app.

할 일:

1. <https://api.slack.com/apps> → 해당 앱 → **OAuth & Permissions**
2. **Bot Token Scopes** 에 추가
   - `files:read` — 음성 노트·오디오 포함한 첨부 다운로드 권한
   - `files:write` — 봇이 음성으로 답하게 할 경우에만
3. **Reinstall to Workspace** 를 반드시 누른다
   스코프만 추가하고 재설치를 안 하면 기존 토큰에 권한이 안 붙는다. 여기서 대부분 막힌다.

> 이 단계는 웹 콘솔 작업이라 스크립트로 자동화할 수 없다.

---

## 2단계 — 한국어 전사 설정 (`hermes-voice-fix.py`)

1단계만 하면 음성이 들어오긴 하는데, Hermes 기본 언어 힌트가 `en` 이라
한국어 발화를 영어로 강제 전사해 결과가 깨진다.

`hermes-voice-fix.py` 는 `config.yaml` 의 **`stt:` 블록만** 고친다.
채널·에이전트·모델·TTS·크론 설정은 건드리지 않는다.

### 먼저: 설정이 어디 있는지 확인 (도커일 때 중요)

PC 에 도커로 띄운 경우, `config.yaml` 이 **컨테이너 안에만** 있으면
컨테이너를 다시 만들 때(`docker compose up -d --force-recreate`, 이미지 업데이트 등)
설정이 통째로 날아간다. 먼저 확인한다:

```powershell
docker ps                                          # 컨테이너 이름 확인
docker inspect <container> --format "{{json .Mounts}}"
```

- 출력에 `.hermes` 가 호스트 경로로 **바인드 마운트돼 있으면** → 호스트 쪽 파일을
  직접 고치면 되고, 재생성해도 살아남는다
- 마운트가 **없으면** → 아래처럼 컨테이너 안에서 고치되, 이건 그 컨테이너에만
  남는다. 재생성 예정이면 마운트를 먼저 걸든지, 고친 뒤 `docker cp` 로 호스트에
  빼두는 게 안전하다

### 실행

**마운트가 있는 경우** — 호스트에서 그냥 실행:

```powershell
python hermes-voice-fix.py --config "<마운트된 호스트 경로>\config.yaml"
python hermes-voice-fix.py --config "<마운트된 호스트 경로>\config.yaml" --apply
```

**마운트가 없는 경우** — 컨테이너 안에서 실행:

```powershell
docker cp hermes-voice-fix.py <container>:/tmp/
docker exec -it <container> pip install ruamel.yaml                   # 주석 보존용 (권장)
docker exec -it <container> python3 /tmp/hermes-voice-fix.py          # 미리보기
docker exec -it <container> python3 /tmp/hermes-voice-fix.py --apply  # 반영
docker cp <container>:/root/.hermes/config.yaml .\config.yaml.backup  # 사본 확보
```

> 컨테이너 안 홈 경로는 이미지에 따라 `/root` 또는 `/home/<user>` 다.
> `docker exec <container> sh -c 'echo $HOME'` 로 확인하면 된다.
> 스크립트는 `~` 를 알아서 풀기 때문에 대개 `--config` 없이 그냥 돌려도 된다.

**기본이 dry-run 이다.** `--apply` 없이는 파일을 쓰지 않는다. 먼저 diff 를 보고 판단하면 된다.
윈도우 호스트에서 직접 돌려도 동작한다(파이썬 3만 있으면 된다).

### 옵션

| 옵션 | 기본 | 설명 |
|---|---|---|
| `--apply` | 꺼짐 | 실제 반영. 없으면 dry-run |
| `--lang` | `ko` | 전사 언어. 자동감지는 `--lang ""` |
| `--provider` | `auto` | `auto`\|`local`\|`groq`\|`openai` |
| `--config` | `~/.hermes/config.yaml` | 설정 파일 경로 |
| `--rollback` | — | 백업 복원 (인자 없으면 최근 것) |

### 프로바이더 자동 선택

`auto` 는 **쓸 수 있는 것만** 고른다. 환경변수와 `~/.hermes/.env` 를 같이 본다.

1. 현재 설정된 프로바이더가 이미 유효하면 → **그대로 둔다**
2. `GROQ_API_KEY` 있으면 → `groq` (`whisper-large-v3-turbo`)
3. `VOICE_TOOLS_OPENAI_KEY` 또는 `OPENAI_API_KEY` 있으면 → `openai`
4. 아무것도 없으면 → `local` (faster-whisper)

`--provider groq` 처럼 명시했는데 키가 없으면 **거부하고 종료한다.**
키 없는 프로바이더로 갈아타면 음성이 아예 안 되기 때문이다.

로컬로 갈 경우 모델이 `tiny`/`base` 면 `small` 로 올린다. 한국어에서 `base` 는
실사용이 어렵다. 첫 실행 시 모델을 내려받는다.

> 로컬 전사는 컨테이너에 할당된 자원을 쓴다. Docker Desktop 은 기본 할당이
> 넉넉하지 않으니, 로컬 모델을 올릴 거면 Settings → Resources 에서 메모리를
> 확인한다(`small` 은 2GB 안팎, `medium` 은 5GB 안팎). 전사할 때마다 CPU 를
> 오래 물기 때문에, PC 로 다른 작업을 하는 중이라면 Groq 무료 티어가 쾌적하다.

### 안전장치

- **dry-run 기본** — `--apply` 전엔 아무것도 안 쓴다
- **백업** — `config.yaml.bak.<날짜-시각>` 를 먼저 뜬다
- **원자적 쓰기** — 임시파일에 쓰고 재파싱 검증까지 통과해야 `rename` 으로 교체.
  중간에 죽어도 원본이 깨지지 않는다
- **주석 보존** — `ruamel.yaml` 이 있으면 주석과 키 순서를 지킨다.
  없으면 PyYAML 로 동작하되 **주석이 사라진다고 경고**한다.
  주석을 지키려면 먼저 `pip install ruamel.yaml`
- **파싱 실패 시 중단** — 깨진 YAML 이면 손대지 않고 종료
- **`stt` 밖은 안 건드림** — 다른 블록은 값·순서 그대로
- **멱등** — 이미 맞게 돼 있으면 "변경 없음" 만 출력

---

## 3단계 — 반영 및 확인

```powershell
docker restart <container>                      # 또는 docker compose restart
docker exec -it <container> hermes config       # 실제 반영값 확인
```

슬랙에서 음성 메모를 보내 확인한다.

### 결과별 판단

| 나온 결과 | 원인 | 조치 |
|---|---|---|
| 여전히 `첨부 이미지 전달 실패` | 1단계 미완 | `files:read` 추가 후 **재설치** 했는지 확인 |
| 첨부는 통과, 엉뚱한 영어로 전사 | `stt.language` 미반영 | `hermes config` 로 값 확인, 재시작 여부 확인 |
| `STT provider unavailable` 계열 | 폴백(local→groq→openai) 전부 실패 | API 키 또는 faster-whisper 설치 확인 |
| 전사는 되는데 정확도가 낮음 | 모델이 약함 | Groq 로 전환하거나 로컬 모델 상향 |

문제가 생기면 되돌린 뒤 재시작하면 원상복구된다:

```powershell
docker exec -it <container> python3 /tmp/hermes-voice-fix.py --rollback
docker restart <container>
```

컨테이너를 새로 만들어버렸다면 그냥 스크립트를 다시 한 번 돌리면 된다.

---

## 출처

- [Slack | Hermes Agent](https://github.com/nousresearch/hermes-agent/blob/main/website/docs/user-guide/messaging/slack.md) — `files:read` 스코프, 재설치 요구사항, 음성 자동 전사
- [Voice & TTS | Hermes Agent](https://hermes-agent.nousresearch.com/docs/user-guide/features/tts/) — STT 프로바이더, 환경변수, 폴백 순서
- [cli-config.yaml.example](https://github.com/NousResearch/hermes-agent/blob/main/cli-config.yaml.example) — `stt:` 키 구조와 기본값

---

## 실제 고칠 지점 — `slack-claude-bridge` (ASURA 환경)

### 실측 근거 (슬랙 원본, 2026-08-05 확인)

- 채널 `#hermes-자비스` (`C0BHUNMETDJ`), 부모 메시지 `1785846192.903279`
- 첨부: `오디오 클립 (2026-08-04 21:23:09).m4a` — **`audio/mp4`, 301.6 KB**
- 봇 응답 2건이 **4초 만에** 도착: `⏳ 답변 생성 중.` → `❌ 첨부 이미지 전달 실패`

4초 만에 실패했다는 건 다운로드를 오래 시도하다 죽은 게 아니라, **필터에서
즉시 걸렀다**는 뜻이다. 즉 첨부 처리기가 이미지 mimetype 만 통과시킨다.

### 패치 방향

`C:\Users\PSH\slack-claude-bridge` 의 첨부 처리 부분 (`server.py` 또는
`commands.py` 중 `files` 를 순회하며 mimetype 을 보는 곳):

```
현재: files[] 중 image/* 만 골라냄 → 없으면 "지원되는 이미지 첨부가 없습니다"

변경: mimetype 으로 분기
  audio/*  또는 subtype == "slack_audio"
    → url_private_download 를 Bearer 토큰으로 다운로드 (files:read 필요)
    → STT 전사 (faster-whisper 로컬 / Groq / OpenAI)
    → 전사 텍스트를 사용자 메시지 본문으로 주입해 기존 경로로 진행
  image/*  → 기존 경로 그대로
  그 외    → 실제 첨부 타입을 밝힌 에러
             ("지원되지 않는 첨부: application/pdf" 처럼)
```

### 주의

- 슬랙이 붙여주는 `files[].transcription` 필드에 **기대지 말 것.** 한국어 음성
  클립엔 전사가 안 붙는 경우가 많다. 자체 STT 를 태워야 한다.
- 한국어 전사는 언어를 `ko` 로 고정하는 편이 정확하다. 자동감지에 맡기면
  짧은 발화에서 영어로 오판하는 일이 있다.
- 로컬 faster-whisper 를 쓸 경우 `base` 는 한국어 실사용이 어렵다. `small` 이상.
- 에러 메시지를 "이미지" 로 뭉뚱그린 것이 이번 오진의 출발점이었다. 실제 받은
  mimetype 을 그대로 노출하도록 바꾸면 다음 디버깅이 훨씬 빨라진다.

### 다음 단계

브리지의 첨부 처리 함수(위 분기가 있는 곳)를 붙여주면 그 코드에 맞춘 패치를
작성한다. `slack-claude-bridge` 는 GitHub 저장소로 올라와 있지 않아 이 세션에서
직접 열 수 없다.
