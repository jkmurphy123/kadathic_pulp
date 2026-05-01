# Pulp Structure Builder: Project Design

## 1. Project Summary

Pulp Structure Builder is a Python + NiceGUI application that helps a user transform a rough, unstructured story idea into a structured pulp-fiction outline.

The app is aimed at short, lurid, high-pressure pulp fiction inspired by adventure stories, weird tales, sword-and-sorcery, cosmic horror, and hybrid weird adventure. The first supported structural family is a Lester Dent-inspired pulp formula organized into four escalating story quarters.

The user begins with a raw text file containing a few paragraphs of story material. The app imports the text, asks the user to choose a story form, parses the raw material, maps it onto the selected structure, and inserts placeholders where important story components are missing.

The user can then work through the structure from left to right, filling gaps, expanding vague sections, and eventually exporting a complete structured story outline or rough draft.

## 2. Primary User Workflow

1. User launches the NiceGUI app.
2. User clicks `Import Story`.
3. Import dialog opens.
4. User selects a story form:
   - Howard Adventure
   - Lovecraft Weird Tale
   - Hybrid Weird Adventure
5. User browses for or uploads a `.txt` file containing rough story material.
6. App reads the file.
7. App creates a new project using the selected form.
8. App maps raw story text onto the selected pulp structure.
9. App inserts placeholders for missing required components.
10. Left panel displays the full expandable story structure.
11. User clicks a structure component.
12. Right panel displays details, guidance, extracted material, and an editable text area.
13. User fills in missing sections.
14. Project is saved as a single JSON file.
15. User can reload the project later.
16. User exports the structured story as a text file.

## 3. UI Design

The interface has four panels.

```text
+-------------------------------------------------------------+
| Top Panel: project controls, story form, filename, buttons  |
+-----------------------------+-------------------------------+
| Left Panel                  | Right Panel                   |
| Expandable structure tree   | Selected component details    |
|                             | Large editable story text     |
|                             | Guidance and questions        |
+-----------------------------+-------------------------------+
| Bottom Panel: status messages: Info / Warning / Error       |
+-------------------------------------------------------------+
```

### 3.1 Top Panel

Purpose:

- Control major project actions.
- Show current project metadata.
- Keep the current story form visible.
- Show whether the project has unsaved changes.

Controls and fields:

```text
Project: <project title>
Story Form: <fixed form after import>
Imported File: <filename>
State: Saved / Unsaved Changes

[Import Story] [Save Project] [Load Project] [Export Text]
```

Rules:

- Before import, story form may be blank.
- During import, story form is selected.
- After import, story form is fixed for that project.
- Changing story form after import is out of scope for the first version.
- If there are unsaved changes and the user imports a new file, show a warning.

### 3.2 Import Dialog

Purpose:

- Create a new structured story project from raw text.

Fields:

```text
Story Form:
  - Howard Adventure
  - Lovecraft Weird Tale
  - Hybrid Weird Adventure

Story Text File:
  [Browse / Upload .txt]

[Import] [Cancel]
```

Behavior:

- Validate that a story form is selected.
- Validate that a text file is provided.
- Read the text file.
- Create a project using the selected form.
- Parse and map raw content to structure.
- Insert placeholders.
- Close dialog.
- Refresh all UI panels.
- Add status messages.

### 3.3 Left Structure Panel

Purpose:

- Display the selected pulp structure.
- Let the user navigate the story.

The panel contains an expandable tree:

```text
Opening Menace
  Hook with Menace
  Hero Desire
  Initial Trouble
  Hint of Deeper Menace

Deepening Trouble
  First Attempt
  First Complication
  Clue or Pattern
  Rising Stakes

Trap and Terrible Revelation
  Reversal
  Betrayal or False Safety
  Terrible Revelation
  Deathtrap or Contact

Payoff and Final Sting
  Final Confrontation
  Cost of Survival
  Resolution
  Final Sting
```

Visual indicators:

- Missing/placeholder item.
- User has entered story text.
- Optional item.
- Required item.

Suggested indicator strategy:

```text
[!] Required placeholder
[✓] Has story text
[?] Optional placeholder
```

### 3.4 Right Detail Panel

Purpose:

- Display and edit the selected structure component.

Fields:

```text
Title:
Parent Quarter:
Description:
Required:
Placeholder:
Missing Reason:
Guidance:
Suggested Questions:
Extracted Evidence:

Story Text:
[large textarea]
```

Behavior:

- Updates when the selected tree node changes.
- Text area edits update the current project model.
- App marks project as dirty after edits.
- The user can write into placeholder sections directly.
- When text is entered into a placeholder, it may remain marked as originally placeholder but should also gain a completion indicator.

Recommended model fields:

```text
is_placeholder: true/false
was_placeholder: true/false
completion_state: missing | partial | drafted | complete
```

### 3.5 Bottom Status Panel

Purpose:

- Show short user-facing messages.

Message types:

```text
Info
Warning
Error
```

Examples:

```text
INFO: Imported story_idea.txt using Hybrid Weird Adventure.
WARNING: Terrible Revelation is missing. Placeholder inserted.
ERROR: Could not read selected file.
```

Implementation:

- Keep a small rolling list of recent messages.
- Use simple color-coded styles.
- Do not over-engineer the first version.

## 4. Story Forms

The app supports three forms. All are based on the same four-quarter Lester Dent-inspired structure, but the guidance differs by genre.

## 4.1 Common Lester Dent-Inspired Chassis

Top-level structure:

```text
1. Opening Menace
2. Deepening Trouble
3. Trap and Terrible Revelation
4. Payoff and Final Sting
```

### Quarter 1: Opening Menace

Purpose:

- Start with energy.
- Introduce danger, desire, or mystery.
- Give the protagonist a reason to move.

Common components:

```text
Hook with Menace
Hero Desire
Initial Trouble
Hint of Deeper Menace
```

### Quarter 2: Deepening Trouble

Purpose:

- The protagonist acts.
- Trouble doubles.
- The apparent problem becomes bigger.

Common components:

```text
First Attempt
First Complication
Clue or Pattern
Rising Stakes
```

### Quarter 3: Trap and Terrible Revelation

Purpose:

- The hero gets closer to the truth.
- The obvious plan fails.
- A reversal exposes the deeper threat.

Common components:

```text
Reversal
Betrayal or False Safety
Terrible Revelation
Deathtrap or Contact
```

### Quarter 4: Payoff and Final Sting

Purpose:

- The story resolves through confrontation, escape, revelation, doom, or ironic survival.
- The ending leaves a strong final image.

Common components:

```text
Final Confrontation
Cost of Survival
Resolution
Final Sting
```

## 4.2 Howard Adventure Mode

Tone:

- Sword-and-sorcery adventure.
- Physical danger.
- Hostile places.
- Treachery.
- Ancient evil.
- Brutal escape or victory.
- Ironic ending.

Biases:

```text
Hero type: barbarian, thief, mercenary, warrior, outlaw, wanderer
Menace type: sorcerer, monster, cult, decadent city, cursed relic, ancient ruin
Ending type: violent survival, grim victory, ironic escape
```

Howard-specific guidance examples:

```text
Hook with Menace:
Open with danger in motion: a chase, ambush, tavern fight, execution, storm, raid, or corpse.

Hero Desire:
What does the hero want right now? Treasure, revenge, rescue, escape, glory, survival, or forbidden knowledge?

Terrible Revelation:
What ancient power, sorcery, monstrous bloodline, or human treachery is really behind the trouble?

Final Sting:
What is lost, mocked, destroyed, or left ominously unresolved after the hero survives?
```

## 4.3 Lovecraft Weird Tale Mode

Tone:

- Weird tale.
- Dread.
- Testimony or confession.
- Strange anomaly.
- Investigation.
- Forbidden knowledge.
- Cosmic or ancestral revelation.
- Psychological collapse.

Biases:

```text
Hero type: scholar, antiquarian, doctor, explorer, narrator, heir, journalist
Menace type: cosmic entity, ancient race, forbidden manuscript, cult, dream, impossible place, hereditary curse
Ending type: doom, madness, dread, suppressed testimony, final uncanny sign
```

Lovecraft-specific guidance examples:

```text
Hook with Menace:
Open with a reason the narrator must confess, warn, destroy evidence, or explain a disappearance.

Hero Desire:
What does the narrator seek? Proof, explanation, inheritance, lost records, scientific truth, or forbidden history?

Terrible Revelation:
What truth proves that humanity is smaller, older, less central, or less safe than believed?

Final Sting:
What final detail proves the horror continues?
```

## 4.4 Hybrid Weird Adventure Mode

Tone:

- Fast adventure plus uncanny dread.
- Mission into danger.
- Human treachery.
- Ancient horror.
- Physical crisis.
- Costly survival.

Biases:

```text
Hero type: explorer, sailor, thief, mercenary, occult investigator, treasure hunter
Menace type: cursed ruin, cult, monster, forbidden island, lost city, ancient machine, alien relic
Ending type: costly escape, partial victory, dread residue
```

Hybrid-specific guidance examples:

```text
Hook with Menace:
Open with a dangerous mission, object, map, corpse, warning, or impossible event.

Hero Desire:
What practical goal pulls the hero forward?

Terrible Revelation:
What hidden horror makes the mission more dangerous than greed, rescue, or survival alone?

Final Sting:
What sign shows the ancient horror was not fully destroyed?
```

## 5. Data Model

Use Pydantic.

### 5.1 Project Model

Suggested model:

```python
class StoryProject(BaseModel):
    project_id: str
    title: str
    story_form_id: str
    story_form_label: str
    created_at: datetime
    updated_at: datetime
    import_info: ImportInfo
    raw_story_text: str
    root_nodes: list[StoryNode]
    selected_node_id: str | None = None
    dirty: bool = False
```

### 5.2 Import Info

```python
class ImportInfo(BaseModel):
    source_filename: str
    imported_at: datetime
    parser_version: str
```

### 5.3 Story Node

```python
class StoryNode(BaseModel):
    node_id: str
    parent_id: str | None = None
    title: str
    node_type: Literal["quarter", "component"]
    order_index: int
    description: str = ""
    guidance_prompt: str = ""
    suggested_questions: list[str] = Field(default_factory=list)
    required: bool = True
    is_placeholder: bool = False
    was_placeholder: bool = False
    missing_reason: str = ""
    completion_state: Literal["missing", "partial", "drafted", "complete"] = "missing"
    extracted_evidence: list[ExtractedEvidence] = Field(default_factory=list)
    story_text: str = ""
    children: list["StoryNode"] = Field(default_factory=list)
```

### 5.4 Extracted Evidence

```python
class ExtractedEvidence(BaseModel):
    source: Literal["paragraph", "sentence", "keyword", "manual"]
    text: str
    confidence: float = 0.0
    notes: str = ""
```

### 5.5 Status Message

```python
class StatusMessage(BaseModel):
    message_id: str
    created_at: datetime
    level: Literal["info", "warning", "error"]
    text: str
```

## 6. JSON Save Format

One JSON file should contain everything needed to reconstruct the app state.

Example skeleton:

```json
{
  "project_id": "project-20260430-001",
  "title": "The Serpent Below the Moon",
  "story_form_id": "hybrid_weird_adventure",
  "story_form_label": "Hybrid Weird Adventure",
  "created_at": "2026-05-01T09:00:00",
  "updated_at": "2026-05-01T09:20:00",
  "import_info": {
    "source_filename": "story_idea.txt",
    "imported_at": "2026-05-01T09:00:00",
    "parser_version": "deterministic-v1"
  },
  "raw_story_text": "Original imported text goes here.",
  "selected_node_id": "q1-hook-with-menace",
  "dirty": false,
  "root_nodes": [
    {
      "node_id": "q1",
      "title": "Opening Menace",
      "node_type": "quarter",
      "children": []
    }
  ]
}
```

## 7. Parser Design

The initial parser should be deliberately simple and deterministic.

### 7.1 Parser Inputs

```text
raw_story_text
story_form_id
story_structure_template
```

### 7.2 Parser Outputs

```text
StoryProject
```

### 7.3 Processing Steps

1. Normalize line endings.
2. Split text into paragraphs.
3. Tokenize simple sentences.
4. Detect possible character names.
5. Detect possible settings.
6. Detect possible event/action phrases.
7. Detect possible ending phrases.
8. Match evidence to structure components.
9. Fill best-fit components.
10. Insert placeholders for missing required components.
11. Preserve the complete raw input.

### 7.4 Simple Heuristics

Possible character detection:

```text
- Capitalized words or two-word capitalized phrases.
- Phrases after words like "named", "called", "known as".
```

Possible setting detection:

```text
temple, ruin, city, island, cave, tomb, jungle, tower, village, library,
archive, sea, ship, desert, mountain, castle, cellar, laboratory
```

Possible menace detection:

```text
monster, beast, serpent, cult, curse, ghost, god, demon, witch, sorcerer,
madness, dream, corpse, blood, scream, shadow, star, relic, idol
```

Possible action/event detection:

```text
finds, discovers, steals, escapes, fights, kills, follows, enters,
opens, betrays, reveals, summons, dies, survives, flees
```

Possible ending detection:

```text
dies, escapes, survives, goes mad, destroys, buries, burns, loses,
betrays, returns, vanishes, laughs, screams, waits
```

### 7.5 Mapping Strategy

A simple first version can map paragraphs by scoring.

Each structure component has keyword hints. For example:

```python
{
    "hook_with_menace": ["corpse", "attack", "danger", "chase", "scream", "blood"],
    "hero_desire": ["wants", "seeks", "treasure", "rescue", "revenge", "escape"],
    "terrible_revelation": ["truth", "reveals", "ancient", "curse", "god", "cosmic"],
    "final_sting": ["still", "again", "returns", "not dead", "dreams", "waits"]
}
```

For each paragraph:

1. Score paragraph against each component.
2. Assign paragraph to highest-scoring component if above threshold.
3. If nothing clears threshold, assign to a general notes/evidence bucket or leave as raw preserved text only.
4. Required components with no assigned evidence become placeholders.

## 8. Project Store

### 8.1 Save

Input:

```text
StoryProject
target path
```

Behavior:

- Serialize model to JSON.
- Use pretty indentation.
- Update `updated_at`.
- Set dirty false after successful save.

### 8.2 Load

Input:

```text
project JSON path
```

Behavior:

- Load JSON.
- Validate with Pydantic.
- Restore app state.

## 9. Exporter

Export target:

```text
.txt
```

Export format:

```text
Title: <project title>
Story Form: <story form label>
Imported From: <source filename>

# Opening Menace

## Hook with Menace

Description:
<description>

Guidance:
<guidance>

Story Text:
<story_text or placeholder marker>

Suggested Questions:
- ...
```

Placeholder format:

```text
[PLACEHOLDER: This required component has not been filled yet.]
Missing reason: ...
Guidance: ...
```

## 10. Status System

Create a small `StatusBus` service.

Responsibilities:

- Add info/warning/error messages.
- Maintain recent messages.
- Let UI refresh bottom panel.
- Optionally expose `latest(level=None)`.

Suggested methods:

```python
status.info("Imported story idea.")
status.warning("Terrible Revelation placeholder inserted.")
status.error("Could not load file.")
```

## 11. NiceGUI Implementation Notes

### 11.1 App State

Use a simple app state object:

```python
class AppState:
    current_project: StoryProject | None
    selected_node_id: str | None
    status_messages: list[StatusMessage]
```

The UI reads from and writes to this state.

### 11.2 Refresh Strategy

Keep it simple:

- `refresh_top_panel()`
- `refresh_structure_panel()`
- `refresh_detail_panel()`
- `refresh_status_panel()`

NiceGUI supports refreshable UI sections. Use `@ui.refreshable` where helpful.

### 11.3 Tree Selection

The tree should store each node ID. When clicked:

1. Set selected node ID.
2. Find node in current project.
3. Refresh detail panel.

### 11.4 Text Editing

When the text area changes:

1. Update selected node `story_text`.
2. Update completion state.
3. Mark project dirty.
4. Refresh top panel status.

Do not save automatically in the first version unless explicitly chosen.

## 12. Milestones

## Milestone 1: Models and Structure Registry

Build:

- Project skeleton.
- Pydantic models.
- Structure registry.
- Lester Dent base components.
- Three story forms.

Tests:

- Registry contains all three forms.
- Each form has four quarters.
- Each required component has guidance.
- Model validation works.

Deliverable:

- `pytest` passes.
- No UI required yet.

## Milestone 2: Import and Parser

Build:

- Import service.
- Deterministic parser.
- Placeholder creation.
- Basic paragraph/evidence assignment.

Tests:

- Raw text is preserved.
- Missing required components become placeholders.
- At least one paragraph can be assigned to a component.
- Story form is fixed in the created project.

Deliverable:

- CLI or test fixture can import a `.txt` file into a valid project model.

## Milestone 3: Save/Load/Export

Build:

- JSON project store.
- Text exporter.

Tests:

- Save/load round trip.
- Export contains headings.
- Export contains placeholders.
- Export contains user story text.

Deliverable:

- A parsed project can be saved, loaded, and exported.

## Milestone 4: NiceGUI Layout Shell

Build:

- App shell.
- Four panels.
- Static sample project.
- Left tree.
- Right detail view.
- Bottom status area.

Tests:

- Minimal unit tests remain passing.
- Manual launch works.

Deliverable:

- `python -m pulp_builder.app` opens the UI.
- Selecting a node updates the detail panel.

## Milestone 5: Import Dialog

Build:

- Import Story button.
- Import dialog.
- Story form dropdown.
- File upload/browse.
- Parser integration.
- Status messages.

Deliverable:

- User can import a `.txt` file from UI and see the structured result.

## Milestone 6: Editing and Dirty State

Build:

- Editable story text area.
- Update selected node on edit.
- Mark dirty.
- Save project from UI.
- Load project from UI.

Deliverable:

- User can edit, save, reload, and continue.

## Milestone 7: Export from UI

Build:

- Export Text button.
- Export service integration.
- Status messages.

Deliverable:

- User can export a `.txt` version of the structured story.

## Milestone 8: Polish

Build:

- Placeholder badges.
- Completion indicators.
- Better panel sizing.
- Project title editing.
- More helpful guidance prompts.
- Basic keyboard or selection polish if desired.

Deliverable:

- Comfortable first usable version.

### Milestone 9: agent_foundry connection
- Integrate `agent_foundry` enough to connect to an LLM and support AI-guided text updating
- Add a LLM Provider drop down to top panel
- Add a LLM Model drop down to top panel
- Add a Test LLM Connection button to top panel
- remember these choices when the project is saved

## 13. Future Enhancements

Future parser improvements:

- LLM-assisted import.
- Character extraction with roles and arcs.
- Scene beat generation.
- Missing-section question wizard.
- Auto-suggested section drafts.
- Structure conversion between forms.
- Multiple pulp structures beyond Lester Dent.
- Project comparison.
- Export to Markdown.
- Export to StoryCodex-compatible JSON.

Future UI improvements:

- Component completion dashboard.
- Character list panel.
- Timeline view.
- Drag/drop reordering.
- Split raw source view.
- Inline notes.
- Version snapshots.

## 14. Initial Codex Prompt

Use this prompt to start Milestone 1:

```text
You are working in a new Python project called Pulp Structure Builder.

Read AGENTS.md and docs/project_design.md.

Implement Milestone 1 only:
- Create the project skeleton.
- Add pyproject.toml with NiceGUI, Pydantic, pytest dependencies.
- Create Pydantic models for story projects, story nodes, extracted evidence, import info, and status messages.
- Create a story structure registry.
- Implement three Lester Dent-inspired story forms:
  - howard_adventure
  - lovecraft_weird
  - hybrid_weird_adventure
- Each story form must have four top-level quarters:
  - Opening Menace
  - Deepening Trouble
  - Trap and Terrible Revelation
  - Payoff and Final Sting
- Each quarter must contain required components with descriptions and guidance prompts.
- Add pytest tests for model validation and registry contents.
- Do not implement the NiceGUI UI yet except for placeholder files if useful.
- Keep business logic separate from future UI code.
- Run pytest and fix failures.
```

## 15. Design Principle

The app should feel like a pulp editor’s workbench: rough manuscript scraps come in, a clean story chassis appears, and the missing pieces glow like hot rivets waiting to be hammered into place.
