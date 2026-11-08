"""발주 원본 폴더를 일러로 열어 반려 점검표 자동 검사(audit_order.jsx)를 돌린다. 저장하지 않는다.

  python audit_order.py "<폴더>"      → C:/mvv/out/_audit.txt 를 출력하고 마지막 줄 AUDIT_PASS/AUDIT_FAIL, exit 0/1
사용자 문서가 열려 있으면 run.ps1 이 ABORT(exit 2) 한다 — 그때는 사용자에게 닫아 달라고 한 뒤 다시.
"""
import subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 2:
        print("AUDIT_FAIL 폴더 경로가 필요"); return 1
    folder = Path(sys.argv[1]).resolve()
    if not folder.is_dir():
        print(f"AUDIT_FAIL 폴더 없음: {folder}"); return 1
    out = Path("C:/mvv/out"); out.mkdir(parents=True, exist_ok=True)
    (out / "audit_order.txt").write_text(folder.as_posix() + "\n", encoding="utf-8")
    jsx = out / "audit_order.jsx"; jsx.write_text((HERE / "audit_order.jsx").read_text(encoding="utf-8-sig"), encoding="utf-8-sig")
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(HERE / "run.ps1"), "-Jsx", str(jsx)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print("AUDIT_FAIL run.ps1 exit", r.returncode, (r.stdout or "").strip()[-300:]); return 1
    res = (out / "_audit.txt").read_text(encoding="utf-8")
    print(res)
    return 0 if res.strip().splitlines()[-1].startswith("AUDIT_PASS") else 1


if __name__ == "__main__":
    sys.exit(main())
