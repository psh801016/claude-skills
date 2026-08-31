<!-- notebooklm/SKILL.md 에서 분리. 원문 그대로이며 내용 변경 없음. -->

## Generation Types

All generate commands support:
- `-s, --source` to use specific source(s) instead of all sources
- `--language` to set output language (defaults to configured language or 'en')
- `--json` for machine-readable output (returns `task_id` and `status`)
- `--retry N` to automatically retry on rate limits with exponential backoff (supported on all subcommands **except** `mind-map`)
- `--prompt-file PATH` to read description/query from a file (supported on `ask`, `generate` subcommands except `mind-map`, and `source add-research`; mutually exclusive with positional argument; use for long prompts)

| Type | Command | Options | Download |
|------|---------|---------|----------|
| Podcast | `generate audio` | `--format [deep-dive\|brief\|critique\|debate]`, `--length [short\|default\|long]` | .mp3 |
| Video | `generate video` | `--format [explainer\|brief\|cinematic]` (⁴), `--style [auto\|classic\|whiteboard\|kawaii\|anime\|watercolor\|retro-print\|heritage\|paper-craft]` | .mp4 |
| Slide Deck | `generate slide-deck` | `--format [detailed\|presenter]`, `--length [default\|short]` (²) | .pdf / .pptx |
| Slide Revision | `generate revise-slide "prompt" --artifact <id> --slide N` | `--wait`, `--notebook` | *(re-downloads parent deck)* |
| Infographic | `generate infographic` | `--orientation [landscape\|portrait\|square]`, `--detail [concise\|standard\|detailed]`, `--style [auto\|sketch-note\|professional\|bento-grid\|editorial\|instructional\|bricks\|clay\|anime\|kawaii\|scientific]` | .png |
| Report | `generate report` | `--format [briefing-doc\|study-guide\|blog-post\|custom]`, `--append "extra instructions"` (¹) | .md |
| Mind Map | `generate mind-map` | `--kind [interactive\|note-backed]` (³) *(default: note-backed; flips to interactive in v0.8.0)* | .json |
| Data Table | `generate data-table` | description required | .csv |
| Quiz | `generate quiz` | `--difficulty [easy\|medium\|hard]`, `--quantity [fewer\|standard\|more]` | .json/.md/.html |
| Flashcards | `generate flashcards` | `--difficulty [easy\|medium\|hard]`, `--quantity [fewer\|standard\|more]` | .json/.md/.html |

¹ `--append` only customizes the built-in templates. With `--format custom`, pass the prompt as the positional `DESCRIPTION` argument (`notebooklm generate report "PROMPT" --format custom`); `--append` is silently ignored in that mode (the CLI prints a warning).

³ **Two kinds of mind map (issue #1256).** `generate mind-map --kind note-backed` (today's default) creates the **note-backed** kind — a JSON node tree, generated synchronously. `generate mind-map --kind interactive` creates the newer **interactive** studio artifact (what the web app now makes); it is polled to completion. Both emit the same `{mind_map, note_id, kind}` JSON, list under `artifact list --type mind-map`, and export via `download mind-map`. `--instructions` applies only to the note-backed kind. **The default `--kind` switches to `interactive` in v0.8.0**; omitting `--kind` prints a one-time stderr notice (silence with `NOTEBOOKLM_QUIET_DEPRECATIONS=1`).

⁴ **Cinematic video (Veo 3).** `generate video --format cinematic` generates AI documentary footage via Veo 3; it **ignores `--style`**, takes ~30-40 min, and requires a Google AI Ultra subscription. Also exposed as the `generate cinematic-video` alias (which forces `--format cinematic` and a longer default timeout). Download with `download video` or the `download cinematic-video` alias.

² **Portrait / vertical slide decks via prompt.** Slide-deck has no `--orientation` flag (unlike infographic). Treat portrait decks as skill-level prompt guidance, not a typed CLI/API contract: NotebookLM currently honors orientation cues written into the `DESCRIPTION` positional argument. Including phrases like `"9:16 portrait"`, `"vertical layout"`, `"portrait mobile format"`, or `"vertical 9:16 layout"` can make NotebookLM render each slide as a 9:16 portrait image. Empirically:

- The `.pptx` canvas itself may stay 16:9, but each slide's embedded image can be rendered as 9:16 portrait — useful for vertical/mobile video material extracted via `python-pptx`.
- Orientation is steered once at generation time. `generate revise-slide` edits content within an existing slide but does not change its orientation; if a slide falls back to landscape (occasional inconsistency), regenerate the whole deck rather than revising the single page.
- Combine with an explicit page count in the prompt (e.g. `"Create exactly 8 pages, using a vertical 9:16 portrait layout"`) for the most predictable output.

```bash
