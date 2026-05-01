"""Import service for creating projects from raw text files."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pulp_builder.models.story_project import ImportInfo, StoryProject
from pulp_builder.services.parser import DeterministicParser, StoryParser
from pulp_builder.structures.registry import StoryStructureRegistry
from pulp_builder.utils.ids import make_project_id


class ImportService:
    """Build `StoryProject` objects from imported text."""

    def __init__(
        self,
        registry: StoryStructureRegistry | None = None,
        parser: StoryParser | None = None,
    ) -> None:
        self._registry = registry or StoryStructureRegistry()
        self._parser = parser or DeterministicParser()

    def import_story_file(
        self,
        file_path: str | Path,
        story_form_id: str,
        project_title: str | None = None,
    ) -> StoryProject:
        """Read a .txt file and import it as a story project."""

        path = Path(file_path)
        raw_story_text = path.read_text(encoding="utf-8")
        title = project_title or path.stem.replace("_", " ").strip().title() or "Untitled Project"
        return self.import_story_text(
            raw_story_text=raw_story_text,
            source_filename=path.name,
            story_form_id=story_form_id,
            project_title=title,
        )

    def import_story_text(
        self,
        raw_story_text: str,
        source_filename: str,
        story_form_id: str,
        project_title: str | None = None,
    ) -> StoryProject:
        """Create a story project from raw story text."""

        if not self._registry.has_form(story_form_id):
            raise ValueError(f"Unknown story form: {story_form_id}")

        story_form = self._registry.get_form(story_form_id)
        parse_result = self._parser.parse(raw_story_text=raw_story_text, story_form=story_form)

        now = datetime.now(timezone.utc)
        selected_node_id = self._first_component_id(parse_result.root_nodes)

        return StoryProject(
            project_id=make_project_id(now),
            title=project_title or "Untitled Project",
            story_form_id=story_form_id,
            story_form_label=story_form["label"],
            created_at=now,
            updated_at=now,
            import_info=ImportInfo(
                source_filename=source_filename,
                imported_at=now,
                parser_version=self._parser.version,
            ),
            raw_story_text=parse_result.raw_story_text,
            root_nodes=parse_result.root_nodes,
            selected_node_id=selected_node_id,
            dirty=False,
        )

    @staticmethod
    def _first_component_id(root_nodes: list) -> str | None:
        for quarter in root_nodes:
            if quarter.children:
                return quarter.children[0].node_id
        return None
