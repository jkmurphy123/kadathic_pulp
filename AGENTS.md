# AGENTS.md

## Project: Pulp Structure Builder

You are building a Python + NiceGUI application that helps a user turn a raw story idea into a structured pulp-fiction outline. The first supported structure is a Lester Dent-inspired pulp formula with variants for Howard-style sword-and-sorcery adventure, Lovecraft-style weird tale, and Hybrid weird-adventure pulp.

The user will import an unstructured text file containing rough story material. The app will parse it, fit it as best as possible into the selected pulp structure, insert placeholders for missing required elements, and let the user edit each story component through a four-panel UI. The project should be implemented in small, testable milestones.

## Core Goals

1. Provide a NiceGUI web UI with four major panels:
   - Narrow top control panel.
   - Left story-structure tree panel with expandable pieces.
   - Right detail/editor panel for the selected story component.
   - Narrow bottom status panel with color-coded Info, Warning, and Error messages.

2. Support importing a raw text file:
   - User selects a fixed story form during import.
   - User browses for a `.txt` story idea file.
   - App parses the raw input into a structured JSON story project.
   - App inserts placeholders where required structure pieces are missing.
   - Once imported, the story form is fixed for that project.

3. Support editing:
   - Selecting a structure item in the left tree refreshes the right panel.
   - The right panel shows metadata for the selected component.
   - The right panel includes a large text area where the user can write or revise that story section.
   - Edits are persisted into the project JSON.

4. Support save/load:
   - Story structure, imported source text, selected story form, extracted notes, placeholders, user-entered story text, and status metadata are saved in one JSON file.
   - The JSON file should be easy to load between sessions.

5. Support export:
   - Export a readable `.txt` outline/draft organized by the selected pulp structure.

## Development Style

- Use Python 3.11+.
- Use NiceGUI for the front end.
- Keep business logic separate from UI code.
- Prefer small modules with clear responsibilities.
- Use Pydantic models for project/story data validation.
- Use pytest for unit tests.
- Do not hard-code logic into UI callbacks if it belongs in services or models.
- Make milestones independently runnable and testable.
- Favor simple deterministic parsing first. Do not require an LLM in Milestone 1.
- The app will use the agent_foundry library for LLM access (found in /home/ubuntu/projects/kadathic_core/src/agent_foundry/). All LLM access will be through this library. 

## Suggested Project Layout

```text
pulp_structure_builder/
  AGENTS.md
  README.md
  pyproject.toml
  src/
    pulp_builder/
      __init__.py
      app.py
      ui/
        __init__.py
        layout.py
        top_panel.py
        structure_panel.py
        detail_panel.py
        status_panel.py
        import_dialog.py
      models/
        __init__.py
        story_project.py
        story_structure.py
        status_message.py
      structures/
        __init__.py
        registry.py
        lester_dent.py
      services/
        __init__.py
        importer.py
        parser.py
        project_store.py
        exporter.py
        status_bus.py
      utils/
        __init__.py
        ids.py
  tests/
    test_structures.py
    test_parser.py
    test_project_store.py
    test_exporter.py
```

## Non-Negotiable Architecture Rules

1. `models/` contains Pydantic data models only.
2. `structures/` defines reusable story forms and their required components.
3. `services/` contains parsing, import, save/load, export, and status logic.
4. `ui/` contains NiceGUI layout and event handlers.
5. `app.py` wires everything together.
6. UI should never be the sole source of truth. The current story project model is the source of truth.
7. All generated IDs for story nodes must be stable once created.
8. Placeholders must be explicit in the JSON, not inferred only by empty text.

## Data Model Requirements

The saved project JSON must include:

- Project metadata.
- Selected story form.
- Import metadata.
- Original raw story text.
- A hierarchical story structure suitable for the left panel.
- Per-component details suitable for the right panel.
- Placeholder flags and guidance prompts.
- User-edited story text for each component.
- Status/history metadata if useful.

The application must be able to reconstruct the full UI state from this JSON.

## Story Forms

Implement three variants at first:

1. `howard_adventure`
   - Sword-and-sorcery adventure pulp.
   - Bias toward physical danger, hostile settings, treachery, ancient horror, violent survival, ironic ending.

2. `lovecraft_weird`
   - Weird tale pulp.
   - Bias toward testimony, anomaly, investigation, forbidden pattern, contact, collapse, final dread image.

3. `hybrid_weird_adventure`
   - Weird adventure pulp.
   - Bias toward mission, descent, betrayal, ancient truth, physical crisis, costly survival, final sting.

All three should be built on a Lester Dent-style four-quarter chassis. These should be saved in a config file as additional varients will be added in the future

## Lester Dent-Inspired Chassis

Each story form should be organized into four top-level quarters:

1. Opening Menace
2. Deepening Trouble
3. Trap and Terrible Revelation
4. Payoff and Final Sting

Each quarter contains several required components. Each component should include:

- ID
- Title
- Short description
- Guidance prompt
- Required/optional flag
- Placeholder status
- Extracted evidence from raw input, if any
- User story text

## Parser Requirements

Start with a simple deterministic parser. It should:

- Read raw text.
- Split it into paragraphs.
- Extract candidate names using simple heuristics.
- Extract possible settings using simple keyword matching.
- Extract possible events using action-oriented keywords.
- Look for ending/cost words such as “dies”, “escapes”, “betrays”, “revealed”, “survives”, “madness”, “curse”, “treasure”, etc.
- Assign raw material to the best matching structure components.
- Leave placeholders for missing components.
- Preserve all original source text.

The first version does not need to be brilliant. It needs to be transparent, testable, and easy to improve.

## Placeholder Requirements

When the parser cannot confidently fill a required component, create a placeholder with:

- `is_placeholder: true`
- Empty or minimal `story_text`
- A `missing_reason`
- A `guidance_prompt`
- Optional `suggested_questions`

Example:

```json
{
  "id": "q3-terrible-revelation",
  "title": "Terrible Revelation",
  "is_placeholder": true,
  "missing_reason": "The imported story idea does not yet reveal the deeper horror or hidden truth.",
  "guidance_prompt": "What truth makes the visible danger only the surface of something worse?",
  "suggested_questions": [
    "What ancient force, curse, cult, monster, or secret is behind the trouble?",
    "Why is this revelation worse than the protagonist expected?",
    "How does this change the final danger?"
  ],
  "story_text": ""
}
```

## UI Requirements

### Top Panel

Show:

- Current project name.
- Selected story form.
- Imported source filename.
- Unsaved changes indicator.
- Buttons:
  - Import Story
  - Save Project
  - Load Project
  - Export Story

### Import Dialog

Show:

- Story form dropdown:
  - Howard Adventure
  - Lovecraft Weird Tale
  - Hybrid Weird Adventure
- Browse/upload control for a `.txt` file.
- Import/Cancel buttons.

Rules:

- The story form selected during import becomes fixed for that project.
- Changing form after import is not supported in the first version.
- The app may create a new project on import.
- Existing unsaved work should trigger a warning before replacement.

### Left Panel

Show:

- Expandable tree of the story structure.
- Four top-level quarters.
- Child components under each quarter.
- Visual marker for placeholders/missing parts.
- Visual marker for components with user-entered text.
- Clicking a node selects it and refreshes the right panel.

### Right Panel

Show details for the selected component:

- Title.
- Quarter/parent info.
- Description.
- Required/optional flag.
- Placeholder status.
- Missing reason, if any.
- Guidance prompt.
- Suggested questions.
- Extracted evidence from the import, if any.
- Large text area for user story text. Should be scrollable as there might be much text.
- Save/update behavior should persist text into the current project model.

### Bottom Status Panel

Show recent status messages:

- Info
- Warning
- Error

Use color-coded visual treatment. Keep the implementation simple and NiceGUI-native.

## Export Requirements

Export a readable text file:

```text
Title: <project title>
Story Form: <selected form>
Imported From: <filename>

# Opening Menace

## Hook with Menace
<story text or [PLACEHOLDER] + guidance>

...
```

Export should include placeholders clearly so the user can see what still needs work.

## Testing Requirements

Write tests for:

1. Structure registry returns all expected story forms.
2. Each story form has four top-level quarters.
3. Required components include guidance prompts.
4. Parser preserves raw input.
5. Parser creates placeholders for missing required components.
6. Import service creates a valid project.
7. Save/load round trip preserves project data.
8. Exporter generates readable text with placeholders.

## Milestone Development Plan

### Milestone 1: Data Models and Structure Registry

Build:
- Pydantic models.
- Story form registry.
- Lester Dent-inspired structures for the three modes.
- Tests for registry and model validation.

Acceptance:
- `pytest` passes.
- A script or test can instantiate each story form.
- Each story form has four top-level quarters and required child components.

### Milestone 2: Import and Deterministic Parser

Build:
- Text import service.
- Simple deterministic parser.
- Placeholder insertion.
- Tests.

Acceptance:
- Given a rough story text file, the importer creates a valid project JSON model.
- Missing required components are represented as placeholders.
- Original raw text is preserved.

### Milestone 3: Save, Load, and Export

Build:
- Project JSON save/load service.
- Text export service.
- Tests for round trip and export.

Acceptance:
- Project can be saved and loaded without data loss.
- Exported text clearly shows filled sections and placeholders.

### Milestone 4: NiceGUI Layout Shell

Build:
- Four-panel NiceGUI app shell.
- Static sample project loaded from code or fixture.
- Left tree selection updates right detail panel.
- Bottom status panel displays messages.

Acceptance:
- App launches with `python -m pulp_builder.app`.
- Layout matches the four-panel design.
- Selecting nodes in the left panel updates the right panel.

### Milestone 5: Import Dialog Integration

Build:
- Import Story button and dialog.
- Story form dropdown.
- File upload/browse support.
- Import service integration.
- Status messages.

Acceptance:
- User can import a `.txt` file from the UI.
- Imported project appears in left/right panels.
- Top panel displays selected story form and source filename.

### Milestone 6: Editing and Persistence

Build:
- Editable right-panel text area.
- Dirty-state tracking.
- Save/load from UI.
- Status messages for save/load.

Acceptance:
- User edits a component and saves.
- Reloading the project restores the edit.
- Unsaved changes are visible in top panel.

### Milestone 7: Export from UI

Build:
- Export Text button.
- Export service integration.
- User-facing status feedback.

Acceptance:
- User can export a readable text file from the UI.
- Export includes placeholders and guidance.

### Milestone 8: Polish and Extensibility

Build:
- Placeholder badges.
- Component completion indicators.
- Basic project title editing.
- Cleaner styling.
- Extension points for future LLM-assisted parsing.

Acceptance:
- UI is comfortable to use.
- Data model and parser design allow future LLM plug-in replacement.

### Milestone 9: agent_foundry connection
- Integrate `agent_foundry` enough to connect to an LLM and support AI-guided text updating
- Add a LLM Provider drop down to top panel
- Add a LLM Model drop down to top panel
- Add a Test LLM Connection button to top panel
- remember these choices when the project is saved

## Coding Standards

- Use type hints.
- Keep functions small.
- Prefer explicit names over clever names.
- Avoid global mutable state except a deliberate app-state object.
- Keep UI callbacks thin.
- Add tests with every new service/model.
- Update README when commands or workflows change.

## Run Commands

Suggested commands:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m pulp_builder.app
```

## Dependencies

Suggested initial dependencies:

```toml
nicegui
pydantic
pytest
pytest-cov
```

Optional later dependencies:

```toml
rapidfuzz
spacy
openai
ollama
```

Do not add optional dependencies until a milestone requires them.

## Expected First Deliverable

Start with Milestone 1 only. Create the project skeleton, data models, story structure registry, and tests. Do not build the full UI until the models and structures are stable.
