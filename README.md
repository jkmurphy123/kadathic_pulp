# Pulp Structure Builder

Python + NiceGUI application for turning rough story ideas into structured pulp outlines.

## Implemented So Far

- Milestone 1: project skeleton, Pydantic models, structure registry/forms, tests
- Milestone 2: deterministic parser and import service with placeholders
- Milestone 3: JSON save/load and text exporter
- Milestone 4: NiceGUI four-panel shell with sample project and node-detail interaction
- Milestone 5: Import Story dialog with story-form selection, `.txt` upload, parser integration, and status feedback

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
