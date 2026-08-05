# Hermes 음성명령 복구 절차

**증상** — 슬랙에서 Hermes·자비스에게 음성 메모를 보내면 전사되지 않고 이렇게 끝난다:

```
⏳ 답변 생성 중.
❌ 첨부 이미지 전달 실패
지원되는 이미지 첨부가 없습니다.
```

**원인은 두 겹이다. 1단계가 진짜 원인이고, 2단계는 1단계를 고쳐야 드러난다.**

---

## 1단계 — 슬랙 `files:read` 스코프 (필수, 수동)

봇이 이벤트는 받아서 `답변 생성 중`까지 갔는데 **첨부 파일 자체를 못 내려받은** 상태다.
파일을 못 받으니 전사(STT)는 시작조차 못 한다. 에러 문구가 "이미지"인 건 첨부 실패
메시지가 이미지 기준으로 적혀 있어서일 뿐, 이미지 문제가 아니다.

Hermes 공식 트러블슈팅에 같은 증상이 그대로 있다:

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
