---
name: attendance
description: MEC&WIP 출석체크 실행. "출석체크", "출석체크 해줘", "출첵", "출첵 해줘", "/attendance" 요청 시 사용.
---

다음 명령을 Bash로 실행하세요:

```bash
C:/Users/PSH/AppData/Local/Python/pythoncore-3.14-64/python.exe C:/Users/PSH/.claude/scripts/mecnwip_attendance.py
```

결과를 사용자에게 알려주세요:
- "출석체크 완료!" → 성공
- "오늘 이미 출석체크 완료" → 오늘 이미 함
- "주말 — 출석체크 건너뜀" → 주말
- ERROR → 실패 내용 알림
