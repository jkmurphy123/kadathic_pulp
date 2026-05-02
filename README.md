# Pulp Structure Builder

Python + NiceGUI application for turning rough story ideas into structured pulp outlines.

## Implemented So Far

- Milestone 1: project skeleton, Pydantic models, structure registry/forms, tests
- Milestone 2: deterministic parser and import service with placeholders
- Milestone 3: JSON save/load and text exporter
- Milestone 4: NiceGUI four-panel shell with sample project and node-detail interaction
- Milestone 5: Import Story dialog with story-form selection, `.txt` upload, parser integration, and status feedback
- Milestone 6: Editable detail panel, dirty-state tracking, and Save/Load Project actions from the UI
- Milestone 7: Export Story dialog integrated with text exporter and status feedback
- Milestone 8: Placeholder/completion badges, project title editing, cleaner UI styling, and parser interface extension points
- Milestone 9: `agent_foundry` LLM integration with provider/model dropdowns, Test LLM Connection, and optional LLM first-pass import guidance

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pip install -e /home/ubuntu/projects/kadathic_core
```

## Run Tests

```bash
pytest
```

## Launch App

```bash
python -m pulp_builder.app
```

## New Project From Template

- Use `New Project` in the top panel to create a project without importing user text.
- Choose project name and story form.
- The app loads a built-in tagged template from `templates/<story_form>.txt` and builds the structure.
- This is useful for starting from a clean style scaffold before adding your own story text.

## App Config Persistence

- App-level LLM defaults are saved in `config/app_config.json`.
- The file is updated when:
  - a story import succeeds
  - a project save succeeds
- On the next app launch/session, those provider/model defaults are loaded automatically.

## Configurable Styles

- Story styles are now loaded from `config/app_config.json` under `story_forms`.
- On first app start, defaults are seeded into that file.
- To add a new style, add a new object in `story_forms` with:
  - `id`
  - `label`
  - `summary`
  - `quarters` and `components` (same structure shape as existing forms)
- Restart the app after editing the config file.

## LLM Provider Notes

- `Mock` works offline and is useful for validating UI wiring.
- `Ollama` uses `OLLAMA_BASE_URL` (default `http://localhost:11434`).
- `OpenAI-Compatible` uses:
  - `OPENAI_COMPAT_BASE_URL` (default `https://api.openai.com`)
  - `OPENAI_COMPAT_API_KEY_ENV` (default `OPENAI_API_KEY`)

## LLM First-Pass Import

- Project name is set in the `Import Story` dialog and shown read-only in the top panel.
- In `Import Story`, enable `Use LLM first pass` to generate a recommended Lester Dent breakdown draft only.
- The draft is saved to `Drafts/<project_name>_llm_first_pass.txt` and includes both original raw text and the LLM breakdown.
- You can edit that file, then use `Import Tagged Draft` to map it into the structure.
- Tagged parser supports:
  - `## Quarter Name`
  - `- Component Title: summary text`
  - `- Story Text: full section text` (applies to the most recent component line)

## LLM Rewrite

- In the right detail panel, use `LLM Rewrite` under the story text box.
- It rewrites the current text using:
  - selected project story form style
  - currently selected Lester Dent component title/description/guidance
  - currently selected LLM provider/model

## Apply Tags

- In the right detail panel, use `Apply Tags` to process inline bracket instructions.
- Add tags in story text like:
  - `[add room description here]`
  - `[add ominous sound cue]`
- Clicking `Apply Tags` replaces each bracket tag with LLM-generated text.
- All non-tag text remains unchanged.
