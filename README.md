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

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run Tests

```bash
pytest
```

## Launch App

```bash
python -m pulp_builder.app
```
