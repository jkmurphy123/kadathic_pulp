# Pulp Structure Builder

Python + NiceGUI application for turning rough story ideas into structured pulp outlines.

## Milestone 1 Status

Implemented:
- Project skeleton
- Pydantic models
- Lester Dent-inspired structure registry with three forms
- Pytest coverage for models and structure definitions

## Local Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```
