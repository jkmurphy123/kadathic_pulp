"""Project JSON persistence service."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pulp_builder.models.story_project import StoryProject


class ProjectStore:
    """Save and load `StoryProject` objects as JSON."""

    def save(self, project: StoryProject, target_path: str | Path) -> Path:
        """Persist project to disk and return saved path."""

        path = Path(target_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        project.updated_at = datetime.now(timezone.utc)
        project.dirty = False
        payload = project.model_dump_json(indent=2)
        path.write_text(f"{payload}\n", encoding="utf-8")
        return path

    def load(self, source_path: str | Path) -> StoryProject:
        """Load and validate a project JSON file."""

        path = Path(source_path)
        raw = path.read_text(encoding="utf-8")
        return StoryProject.model_validate_json(raw)
