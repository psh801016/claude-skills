#!/usr/bin/env python3
"""Hermes Agent 음성명령(STT) 설정 교정 도구.

슬랙 음성 메모가 전사되지 않는 문제를 고친다. config.yaml 의 `stt:` 블록만
건드리고 나머지(채널·에이전트·모델·TTS 설정)는 바이트 단위로 그대로 둔다.

기본 동작은 dry-run 이다. 실제로 쓰려면 --apply 를 붙여야 한다.

    python3 hermes-voice-fix.py                 # 뭘 바꿀지 보기만
    python3 hermes-voice-fix.py --apply         # 백업 뜨고 반영
    python3 hermes-voice-fix.py --rollback      # 마지막 백업으로 되돌리기

Hermes 가 도커로 떠 있으면 컨테이너 안에서 실행해야 한다:

    docker cp hermes-voice-fix.py <container>:/tmp/
    docker exec -it <container> python3 /tmp/hermes-voice-fix.py --apply
"""

from __future__ import annotations

import argparse
import difflib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEFAULT_CONFIG = Path.home() / ".hermes" / "config.yaml"

# 프로바이더별로 필요한 자격증명. 앞에 있는 것부터 우선 채택한다.
PROVIDER_KEYS = {
    "groq": ["GROQ_API_KEY"],
    "openai": ["VOICE_TOOLS_OPENAI_KEY", "OPENAI_API_KEY"],
    "local": [],
}

# 한국어에서 base/tiny 는 실사용이 어렵다. 로컬로 갈 때만 올린다.
WEAK_LOCAL_MODELS = {None, "", "tiny", "base"}
LOCAL_MODEL_TARGET = "small"


# ---------------------------------------------------------------- YAML 로딩


class YamlIO:
    """ruamel 이 있으면 주석·키 순서를 보존하고, 없으면 PyYAML 로 내려간다."""

    def __init__(self) -> None:
        self.preserves_comments = False
        self._impl = None
        try:
            from ruamel.yaml import YAML

            impl = YAML()
            impl.preserve_quotes = True
            impl.indent(mapping=2, sequence=4, offset=2)
            self._impl = impl
            self.preserves_comments = True
            self.backend = "ruamel.yaml"
        except ImportError:
            try:
                import yaml as pyyaml
            except ImportError:
                die(
                    "PyYAML 도 ruamel.yaml 도 없습니다.\n"
                    "  pip install ruamel.yaml   (주석 보존 — 권장)\n"
                    "  pip install pyyaml        (주석 유실)"
                )
            self._impl = pyyaml
            self.backend = "pyyaml"

    def load(self, text: str):
        if self.preserves_comments:
            return self._impl.load(text) or {}
        return self._impl.safe_load(text) or {}

    def dump(self, data) -> str:
        buf = io.StringIO()
        if self.preserves_comments:
            self._impl.dump(data, buf)
        else:
            self._impl.safe_dump(data, buf, allow_unicode=True, sort_keys=False)
        return buf.getvalue()


# ------------------------------------------------------------------ 유틸


def die(msg: str) -> "NoReturn":  # type: ignore[valid-type]
    print(f"\n[중단] {msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg: str) -> None:
    print(f"[경고] {msg}")


def info(msg: str) -> None:
    print(f"  {msg}")


def load_env_files() -> dict:
    """도커로 돌 때 API 키가 셸 환경엔 없고 .env 에만 있는 경우를 잡는다."""
    found = {}
    candidates = [
        Path.home() / ".hermes" / ".env",
        Path.home() / ".hermes" / "hermes.env",
        Path("/app/.env"),
    ]
    for path in candidates:
        if not path.is_file():
            continue
        try:
            for raw in path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                found.setdefault(key.strip(), value.strip().strip("'\""))
        except OSError:
            continue
    return found


def resolve_credentials() -> dict:
    env = dict(load_env_files())
    env.update(os.environ)  # 실제 환경변수가 항상 우선
    return env


def _is_blank_token(token) -> bool:
    if token is None:
        return False
    if isinstance(token, list):
        return bool(token) and all(_is_blank_token(t) for t in token)
    return not getattr(token, "value", "x").strip()


def map_set(node, key, value) -> None:
    """키를 넣되, 블록 끝 빈 줄이 새 키 앞으로 끼어들지 않게 한다.

    ruamel 은 마지막 키의 '값 뒤 코멘트'로 빈 줄을 들고 있어서, 그냥 추가하면
    새 키가 빈 줄 뒤에 붙어 다음 블록과 붙어버린다. 빈 줄을 잠시 떼었다가
    새 마지막 키로 옮겨 원래 문서 모양을 지킨다.
    """
    if key in node:
        node[key] = value
        return

    parked = _park_trailing_blank(node)
    node[key] = value

    if parked is not None:
        node.ca.items.setdefault(key, [None, None, None, None])[2] = parked


def _park_trailing_blank(node):
    """블록 맨 끝에 붙은 빈 줄을 떼어내 반환한다.

    빈 줄은 가장 깊이 중첩된 마지막 키에 붙어 있을 수 있어서 끝까지 내려간다.
    (예: stt.local.model 뒤의 빈 줄은 stt 가 아니라 local 이 들고 있다)
    """
    if not hasattr(node, "ca") or not len(node):
        return None

    last = list(node.keys())[-1]
    item = node.ca.items.get(last)
    if item and _is_blank_token(item[2]):
        parked = item[2]
        item[2] = None
        return parked

    nested = node[last]
    if isinstance(nested, dict):
        return _park_trailing_blank(nested)
    return None


def ensure_map(parent, key):
    """중간 딕셔너리를 만들되 이미 있으면 절대 덮어쓰지 않는다."""
    current = parent.get(key)
    if isinstance(current, dict):
        return current
    if current is not None:
        die(
            f"config.yaml 의 `{key}` 가 딕셔너리가 아니라 {type(current).__name__} 입니다. "
            "수동 확인이 필요합니다 — 아무것도 건드리지 않았습니다."
        )
    empty = type(parent)() if hasattr(parent, "ca") else {}
    map_set(parent, key, empty)
    return parent[key]


def set_if_changed(node, key, value, path: str, changes: list) -> None:
    old = node.get(key, "<없음>")
    if old == value:
        return
    map_set(node, key, value)
    changes.append(f"{path}: {old!r} → {value!r}")


# ------------------------------------------------------------- 프로바이더


def pick_provider(requested: str, current: str | None, creds: dict) -> tuple[str, list]:
    """쓸 수 있는 프로바이더를 고른다. 키가 없는 곳으로는 절대 옮기지 않는다."""
    notes = []

    def usable(name: str) -> bool:
        return all_keys_present(name, creds)

    if requested != "auto":
        if not usable(requested):
            needed = " 또는 ".join(PROVIDER_KEYS[requested])
            die(
                f"--provider {requested} 를 지정했지만 {needed} 를 찾을 수 없습니다.\n"
                "키를 먼저 넣거나 --provider auto 로 두세요. "
                "키 없는 프로바이더로 바꾸면 음성이 아예 안 됩니다."
            )
        return requested, notes

    # auto: 이미 쓸 수 있는 설정이면 건드리지 않는 게 가장 안전하다.
    if current and usable(current):
        notes.append(f"현재 프로바이더 '{current}' 가 이미 유효 — 변경하지 않음")
        return current, notes

    for candidate in ("groq", "openai", "local"):
        if usable(candidate):
            if current and current != candidate:
                notes.append(
                    f"'{current}' 는 API 키가 없어 사용 불가 → '{candidate}' 로 전환"
                )
            return candidate, notes

    return "local", notes


def all_keys_present(provider: str, creds: dict) -> bool:
    keys = PROVIDER_KEYS.get(provider)
    if keys is None:
        return False
    if not keys:
        return True
    return any(creds.get(k) for k in keys)


# -------------------------------------------------------------- 핵심 로직


def build_changes(cfg, lang: str, requested_provider: str, creds: dict) -> list:
    changes: list = []
    stt = ensure_map(cfg, "stt")

    set_if_changed(stt, "enabled", True, "stt.enabled", changes)
    set_if_changed(stt, "language", lang, "stt.language", changes)

    provider, notes = pick_provider(requested_provider, stt.get("provider"), creds)
    for note in notes:
        info(note)
    set_if_changed(stt, "provider", provider, "stt.provider", changes)

    # 언어 힌트는 선택된 프로바이더 블록에만 박는다. 다른 블록은 놔둔다.
    block = ensure_map(stt, provider)

    if provider == "local":
        set_if_changed(block, "language", lang, "stt.local.language", changes)
        model = block.get("model")
        if model in WEAK_LOCAL_MODELS:
            set_if_changed(
                block, "model", LOCAL_MODEL_TARGET, "stt.local.model", changes
            )
            info(
                f"로컬 모델 {model!r} 는 한국어 정확도가 낮아 "
                f"{LOCAL_MODEL_TARGET!r} 로 올립니다 (첫 실행 시 모델 다운로드)"
            )
    elif provider == "groq":
        set_if_changed(block, "language", lang, "stt.groq.language", changes)
        if not block.get("model"):
            set_if_changed(
                block, "model", "whisper-large-v3-turbo", "stt.groq.model", changes
            )
    elif provider == "openai":
        set_if_changed(block, "language", lang, "stt.openai.language", changes)

    return changes


def show_diff(before: str, after: str) -> None:
    diff = list(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile="config.yaml (현재)",
            tofile="config.yaml (변경 후)",
            n=3,
        )
    )
    if not diff:
        print("  (직렬화 결과 차이 없음)")
        return
    print()
    for line in diff:
        sys.stdout.write(line)
    print()


def write_atomically(path: Path, text: str, yio: YamlIO) -> None:
    """임시파일 → 검증 → rename. 중간에 죽어도 원본이 깨지지 않는다."""
    tmp_fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".hermes-stt-")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())

        # 쓴 결과가 실제로 파싱되는지 확인한 뒤에만 교체한다.
        reparsed = yio.load(tmp_path.read_text(encoding="utf-8"))
        if not isinstance(reparsed, dict) or "stt" not in reparsed:
            raise ValueError("재파싱 결과가 올바르지 않습니다")

        if path.exists():
            shutil.copystat(path, tmp_path)
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def do_rollback(config: Path, explicit: str | None) -> int:
    if explicit:
        backup = Path(explicit)
    else:
        backups = sorted(config.parent.glob(f"{config.name}.bak.*"))
        if not backups:
            die(f"{config.parent} 에 백업이 없습니다.")
        backup = backups[-1]

    if not backup.is_file():
        die(f"백업 파일을 찾을 수 없습니다: {backup}")

    shutil.copy2(backup, config)
    print(f"[완료] {backup.name} → {config.name} 복원했습니다.")
    print("       Hermes 를 재시작해야 반영됩니다.")
    return 0


def restart_hint() -> None:
    print("\n다음: Hermes 재시작 후 슬랙에서 음성 메모를 보내 확인하세요.")
    if shutil.which("docker"):
        print("  docker restart <container>       또는  docker compose restart")
    elif in_container():
        # 컨테이너 안에서는 docker CLI 가 안 보인다. 호스트에서 재시작해야 한다.
        print("  (호스트 쪽에서)  docker restart <container>")
        print("  주의: config.yaml 이 볼륨에 마운트돼 있지 않으면 컨테이너를")
        print("        재생성할 때 이 변경이 사라집니다. README '먼저' 절 참고.")
    if shutil.which("systemctl"):
        print("  systemctl restart hermes")
    if shutil.which("hermes"):
        print("\n반영값 확인:  hermes config")


def in_container() -> bool:
    if Path("/.dockerenv").exists():
        return True
    try:
        return "docker" in Path("/proc/1/cgroup").read_text(encoding="utf-8")
    except OSError:
        return False


# ------------------------------------------------------------------ main


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Hermes 음성명령(STT) 설정 교정 — stt 블록만 건드립니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--apply", action="store_true", help="실제로 파일에 반영 (기본은 dry-run)"
    )
    parser.add_argument(
        "--lang",
        default="ko",
        help='전사 언어 힌트 (기본 ko). 자동감지는 "" 로 두세요.',
    )
    parser.add_argument(
        "--provider",
        default="auto",
        choices=["auto", "local", "groq", "openai"],
        help="auto(기본)는 사용 가능한 API 키를 보고 안전하게 고릅니다.",
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="config.yaml 경로")
    parser.add_argument(
        "--rollback",
        nargs="?",
        const="",
        metavar="BACKUP",
        help="백업으로 되돌립니다 (인자 없으면 가장 최근 백업)",
    )
    args = parser.parse_args()

    config = Path(args.config).expanduser()

    if args.rollback is not None:
        return do_rollback(config, args.rollback or None)

    yio = YamlIO()
    print(f"config : {config}")
    print(f"YAML   : {yio.backend}")
    if not yio.preserves_comments:
        warn(
            "PyYAML 로 동작합니다 — 저장 시 config.yaml 의 주석과 키 순서가 사라집니다.\n"
            "        설정값 자체는 그대로지만, 주석을 지키려면 먼저 "
            "`pip install ruamel.yaml` 후 다시 실행하세요."
        )

    if config.is_file():
        original = config.read_text(encoding="utf-8")
    else:
        warn(f"{config} 가 없습니다. stt 블록만 있는 파일을 새로 만듭니다.")
        original = ""

    try:
        cfg = yio.load(original)
    except Exception as exc:  # noqa: BLE001
        die(f"config.yaml 파싱 실패 — 손대지 않았습니다.\n        {exc}")

    if not isinstance(cfg, dict):
        die("config.yaml 최상위가 매핑이 아닙니다. 수동 확인이 필요합니다.")

    creds = resolve_credentials()
    available = [p for p in ("groq", "openai") if all_keys_present(p, creds)]
    print(f"자격증명: {', '.join(available) if available else '없음 (로컬 전사만 가능)'}")
    print("\n계획된 변경:")

    changes = build_changes(cfg, args.lang, args.provider, creds)

    if not changes:
        print("  없음 — 이미 올바르게 설정돼 있습니다.")
        print(
            "\n그래도 음성이 안 되면 원인은 config 가 아니라 "
            "슬랙 `files:read` 스코프입니다. README 1단계를 확인하세요."
        )
        return 0

    for change in changes:
        info(change)

    updated = yio.dump(cfg)
    show_diff(original, updated)

    if not args.apply:
        print("dry-run 입니다. 위 내용이 맞으면 --apply 를 붙여 다시 실행하세요.")
        return 0

    backup = config.parent / f"{config.name}.bak.{time.strftime('%Y%m%d-%H%M%S')}"
    config.parent.mkdir(parents=True, exist_ok=True)
    if config.is_file():
        shutil.copy2(config, backup)
        print(f"[백업] {backup}")

    try:
        write_atomically(config, updated, yio)
    except Exception as exc:  # noqa: BLE001
        die(
            f"쓰기 실패 — 원본은 그대로입니다.\n        {exc}\n"
            f"        필요하면: python3 {sys.argv[0]} --rollback"
        )

    print(f"[완료] {config} 반영했습니다.")
    print(f"       되돌리려면: python3 {sys.argv[0]} --rollback")
    restart_hint()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
