"""슬랙 음성 메모(오디오 첨부)를 텍스트로 바꿔주는 드롭인 모듈.

slack-claude-bridge 에 넣어서 쓴다. 브리지 코드를 몰라도 되도록,
바깥에서 필요한 건 함수 두 개뿐이다.

    from slack_audio import is_audio_file, transcribe_slack_audio

    # 첨부 처리하는 자리에서:
    audio = [f for f in files if is_audio_file(f)]
    if audio:
        text = transcribe_slack_audio(audio[0], slack_bot_token)
        # text 를 사용자 메시지 본문으로 써서 기존 경로로 계속 진행

의존성은 표준 라이브러리만으로도 동작한다. 전사 엔진은 있는 것부터 골라 쓴다:
faster-whisper(로컬) → Groq → OpenAI. 셋 다 없으면 무엇이 없어서 실패했는지
분명히 알려주는 예외를 던진다.

오프라인 자체점검:  python3 slack_audio.py --selftest
"""

from __future__ import annotations

import json
import mimetypes
import os
import tempfile
import urllib.error
import urllib.request
import uuid
from pathlib import Path

__all__ = [
    "is_audio_file",
    "describe_attachment",
    "download_slack_file",
    "transcribe_slack_audio",
    "TranscriptionError",
]

# 슬랙 음성 클립은 audio/mp4(.m4a) 로 온다. 다른 오디오도 같이 받아준다.
AUDIO_MIME_PREFIX = "audio/"
AUDIO_SUBTYPES = {"slack_audio", "slack_video"}  # 허들 클립도 오디오 트랙이 있다
AUDIO_EXTENSIONS = {
    ".m4a", ".mp3", ".mp4", ".wav", ".ogg", ".oga", ".opus",
    ".webm", ".flac", ".aac", ".amr", ".mpga",
}

DEFAULT_LANGUAGE = "ko"
MAX_DOWNLOAD_BYTES = 200 * 1024 * 1024  # 200MB 방어선


class TranscriptionError(RuntimeError):
    """전사 실패. 메시지에 '무엇이 없어서 실패했는지'를 담는다."""


# --------------------------------------------------------------- 첨부 판별


def is_audio_file(file_obj: dict) -> bool:
    """슬랙 file 객체가 오디오인지 판단한다.

    mimetype 이 비어 오는 경우가 있어 subtype·filetype·확장자까지 본다.
    """
    if not isinstance(file_obj, dict):
        return False

    mimetype = (file_obj.get("mimetype") or "").lower()
    if mimetype.startswith(AUDIO_MIME_PREFIX):
        return True

    if (file_obj.get("subtype") or "").lower() in AUDIO_SUBTYPES:
        return True

    filetype = (file_obj.get("filetype") or "").lower()
    if filetype and f".{filetype}" in AUDIO_EXTENSIONS:
        return True

    name = (file_obj.get("name") or file_obj.get("title") or "").lower()
    return Path(name).suffix in AUDIO_EXTENSIONS


def describe_attachment(file_obj: dict) -> str:
    """에러 메시지에 쓸 설명. '이미지 없음' 대신 실제 타입을 밝히기 위한 것."""
    if not isinstance(file_obj, dict):
        return "알 수 없는 첨부"
    name = file_obj.get("name") or file_obj.get("title") or "이름없음"
    mimetype = file_obj.get("mimetype") or file_obj.get("filetype") or "타입미상"
    size = file_obj.get("size")
    if isinstance(size, int):
        return f"{name} ({mimetype}, {size / 1024:.1f} KB)"
    return f"{name} ({mimetype})"


# ----------------------------------------------------------------- 다운로드


def download_slack_file(file_obj: dict, token: str, dest_dir: str | None = None) -> Path:
    """슬랙 비공개 파일을 받아 로컬 경로를 돌려준다.

    url_private_download 는 봇 토큰 Bearer 인증이 필요하다(`files:read` 스코프).
    인증 없이 받으면 파일 대신 로그인 HTML 이 내려온다 — 그 경우를 잡아낸다.
    """
    url = file_obj.get("url_private_download") or file_obj.get("url_private")
    if not url:
        raise TranscriptionError(
            "첨부에 url_private_download 가 없습니다. "
            "봇이 파일 정보를 못 받은 상태입니다 (files:read 스코프 확인)."
        )
    if not token:
        raise TranscriptionError("슬랙 봇 토큰이 비어 있습니다.")

    request = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}"}
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            content_type = (response.headers.get("Content-Type") or "").lower()
            payload = response.read(MAX_DOWNLOAD_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise TranscriptionError(
            f"슬랙 파일 다운로드 실패 (HTTP {exc.code}). "
            "files:read 스코프를 추가한 뒤 앱을 재설치했는지 확인하세요."
        ) from exc
    except urllib.error.URLError as exc:
        raise TranscriptionError(f"슬랙 파일 다운로드 실패: {exc.reason}") from exc

    if len(payload) > MAX_DOWNLOAD_BYTES:
        raise TranscriptionError("첨부가 너무 큽니다 (200MB 초과).")

    # 권한이 없으면 슬랙이 200 으로 로그인 페이지를 준다. 조용히 넘어가면 안 된다.
    if "text/html" in content_type:
        raise TranscriptionError(
            "파일 대신 HTML 이 내려왔습니다 — 토큰에 files:read 권한이 없습니다. "
            "스코프 추가 후 반드시 앱을 재설치(Reinstall)하세요."
        )
    if not payload:
        raise TranscriptionError("빈 파일을 받았습니다.")

    suffix = Path(file_obj.get("name") or "").suffix
    if not suffix:
        suffix = mimetypes.guess_extension(file_obj.get("mimetype") or "") or ".m4a"

    target_dir = Path(dest_dir or tempfile.gettempdir())
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"slack-audio-{uuid.uuid4().hex}{suffix}"
    path.write_bytes(payload)
    return path


# ------------------------------------------------------------------- 전사


def _transcribe_faster_whisper(path: Path, language: str, model_size: str) -> str:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise TranscriptionError("faster-whisper 미설치") from exc

    model = WhisperModel(model_size, device="auto", compute_type="int8")
    segments, _ = model.transcribe(str(path), language=language or None, vad_filter=True)
    return " ".join(segment.text.strip() for segment in segments).strip()


def _post_multipart(url: str, token: str, path: Path, fields: dict) -> dict:
    """의존성 없이 multipart/form-data 전송 (requests 없이 동작하도록)."""
    boundary = f"----slackaudio{uuid.uuid4().hex}"
    parts: list[bytes] = []

    for key, value in fields.items():
        if value is None or value == "":
            continue
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n"
            f"{value}\r\n".encode()
        )

    parts.append(
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n".encode()
    )
    parts.append(path.read_bytes())
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    body = b"".join(parts)

    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise TranscriptionError(f"전사 API 오류 (HTTP {exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise TranscriptionError(f"전사 API 연결 실패: {exc.reason}") from exc


def _transcribe_groq(path: Path, language: str, api_key: str) -> str:
    result = _post_multipart(
        "https://api.groq.com/openai/v1/audio/transcriptions",
        api_key,
        path,
        {"model": "whisper-large-v3-turbo", "language": language, "response_format": "json"},
    )
    return (result.get("text") or "").strip()


def _transcribe_openai(path: Path, language: str, api_key: str) -> str:
    result = _post_multipart(
        "https://api.openai.com/v1/audio/transcriptions",
        api_key,
        path,
        {"model": "gpt-4o-transcribe", "language": language, "response_format": "json"},
    )
    return (result.get("text") or "").strip()


def transcribe_file(
    path: Path,
    language: str = DEFAULT_LANGUAGE,
    provider: str = "auto",
    local_model: str = "small",
) -> str:
    """오디오 파일을 텍스트로. provider='auto' 면 쓸 수 있는 것부터 시도한다."""
    groq_key = os.environ.get("GROQ_API_KEY")
    openai_key = os.environ.get("VOICE_TOOLS_OPENAI_KEY") or os.environ.get(
        "OPENAI_API_KEY"
    )

    if provider == "local":
        return _transcribe_faster_whisper(path, language, local_model)
    if provider == "groq":
        if not groq_key:
            raise TranscriptionError("GROQ_API_KEY 가 없습니다.")
        return _transcribe_groq(path, language, groq_key)
    if provider == "openai":
        if not openai_key:
            raise TranscriptionError("VOICE_TOOLS_OPENAI_KEY / OPENAI_API_KEY 가 없습니다.")
        return _transcribe_openai(path, language, openai_key)

    attempts: list[str] = []
    for name, runner in (
        ("faster-whisper(로컬)", lambda: _transcribe_faster_whisper(path, language, local_model)),
        ("Groq", (lambda: _transcribe_groq(path, language, groq_key)) if groq_key else None),
        ("OpenAI", (lambda: _transcribe_openai(path, language, openai_key)) if openai_key else None),
    ):
        if runner is None:
            attempts.append(f"{name}: API 키 없음")
            continue
        try:
            text = runner()
            if text:
                return text
            attempts.append(f"{name}: 빈 결과")
        except TranscriptionError as exc:
            attempts.append(f"{name}: {exc}")

    raise TranscriptionError(
        "전사할 수 있는 엔진이 없습니다. 시도 내역 — " + " / ".join(attempts)
    )


def transcribe_slack_audio(
    file_obj: dict,
    slack_token: str,
    language: str = DEFAULT_LANGUAGE,
    provider: str = "auto",
    local_model: str = "small",
    keep_file: bool = False,
) -> str:
    """슬랙 오디오 첨부 하나를 받아 전사 텍스트를 돌려준다."""
    path = download_slack_file(file_obj, slack_token)
    try:
        text = transcribe_file(path, language, provider, local_model)
    finally:
        if not keep_file:
            path.unlink(missing_ok=True)

    if not text:
        raise TranscriptionError("전사 결과가 비어 있습니다 (무음이거나 인식 실패).")
    return text


# -------------------------------------------------------------- 자체점검


def _selftest() -> int:
    """네트워크 없이 판별 로직만 검증한다."""
    checks: list[tuple[str, bool]] = []

    # 실제 슬랙이 보낸 음성 클립 (2026-08-04 21:23, F0BNR5K1S5N)
    voice = {
        "name": "오디오 클립 (2026-08-04 21:23:09).m4a",
        "mimetype": "audio/mp4",
        "filetype": "m4a",
        "size": 308838,
        "subtype": "slack_audio",
    }
    checks.append(("실제 음성 클립 인식", is_audio_file(voice) is True))
    checks.append(
        ("설명 문자열에 실제 타입 노출", "audio/mp4" in describe_attachment(voice))
    )

    # mimetype 이 비어 오는 경우 — 확장자로 건져야 한다
    checks.append(
        ("mimetype 없음 → 확장자로 판별", is_audio_file({"name": "memo.ogg"}) is True)
    )
    checks.append(
        ("filetype 만 있음", is_audio_file({"filetype": "mp3"}) is True))

    # 오디오가 아닌 것들은 걸러야 한다
    checks.append(("이미지 제외", is_audio_file({"mimetype": "image/png"}) is False))
    checks.append(
        ("PDF 제외", is_audio_file({"mimetype": "application/pdf", "name": "a.pdf"}) is False)
    )
    checks.append(("빈 dict", is_audio_file({}) is False))
    checks.append(("dict 아님", is_audio_file(None) is False))

    # 다운로드 사전조건
    try:
        download_slack_file({"mimetype": "audio/mp4"}, "xoxb-test")
        checks.append(("URL 없으면 예외", False))
    except TranscriptionError as exc:
        checks.append(("URL 없으면 예외", "url_private_download" in str(exc)))

    try:
        download_slack_file({"url_private_download": "https://x/y.m4a"}, "")
        checks.append(("토큰 없으면 예외", False))
    except TranscriptionError as exc:
        checks.append(("토큰 없으면 예외", "토큰" in str(exc)))

    # 프로바이더 강제 시 키 없으면 명확히 실패
    try:
        saved = os.environ.pop("GROQ_API_KEY", None)
        transcribe_file(Path("/nonexistent.m4a"), provider="groq")
        checks.append(("키 없는 groq 강제 → 예외", False))
    except TranscriptionError as exc:
        checks.append(("키 없는 groq 강제 → 예외", "GROQ_API_KEY" in str(exc)))
    finally:
        if saved:
            os.environ["GROQ_API_KEY"] = saved

    width = max(len(name) for name, _ in checks)
    failed = 0
    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name.ljust(width)}")
        failed += 0 if ok else 1

    print(f"\n{len(checks) - failed}/{len(checks)} 통과")
    return 1 if failed else 0


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
