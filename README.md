# Claude Skills

A practical collection of reusable skills, prompts, and verification utilities
for AI-assisted work. The collection focuses on repeatable workflows rather
than one-off chat prompts.

## Included areas

- Architectural drawing interpretation and 3D wall construction
- Interior, exhibition, lighting, material, and person-compositing workflows
- Cross-model review and adaptive model/effort selection
- Instagram saved-item organization and account-analysis guidance
- Notion, NotebookLM, and workflow-automation playbooks

The skills are organised for two environments:

- `claude-code-skills/` contains skills intended for Claude Code workflows.
- `claude-desktop-skills/` contains skills and small utilities used in desktop
  agent workflows.

Each skill documents its own trigger conditions, operating constraints, and
verification criteria. Some skills require separate third-party tools,
credentials, or local services; review the relevant `SKILL.md` before use.

## Use

Copy only the skill directory you need into the skills location used by your
agent runtime, then read its `SKILL.md` before running any included script.
Do not commit credentials, browser profiles, API tokens, or generated output
that contains private data.

## Contributing

Issues and pull requests are welcome for reproducible fixes, clearer
verification, and new reusable workflows. Please keep changes narrowly scoped
and document any external dependency or required validation step.

## License

Released under the [MIT License](LICENSE).
