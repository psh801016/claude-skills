<!-- notebooklm/SKILL.md 에서 분리. 원문 그대로이며 내용 변경 없음. -->

## Command Output Formats

Commands with `--json` return structured data for parsing:

**Create notebook:**
```bash
$ notebooklm create "Research" --json
{"notebook": {"id": "abc123de-...", "title": "Research", "created_at": null}}
