"""Import service for creating projects from raw text files."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re

from pulp_builder.models.story_project import ImportInfo, StoryProject
from pulp_builder.services.llm_parser import LLMFirstPassParser
from pulp_builder.services.parser import DeterministicParser, StoryParser
from pulp_builder.structures.registry import StoryStructureRegistry
from pulp_builder.utils.ids import make_project_id


class ImportService:
    """Build `StoryProject` objects from imported text."""

    def __init__(
        self,
        registry: StoryStructureRegistry | None = None,
        parser: StoryParser | None = None,
        drafts_dir: str | Path = "Drafts",
    ) -> None:
        self._registry = registry or StoryStructureRegistry()
        self._parser = parser or DeterministicParser()
        self._llm_first_pass_parser = LLMFirstPassParser()
        self._drafts_dir = Path(drafts_dir)

    def import_story_file(
        self,
        file_path: str | Path,
        story_form_id: str,
        project_title: str | None = None,
        use_llm_first_pass: bool = False,
        llm_provider_id: str | None = None,
        llm_model: str | None = None,
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
            use_llm_first_pass=use_llm_first_pass,
            llm_provider_id=llm_provider_id,
            llm_model=llm_model,
        )

    def import_story_text(
        self,
        raw_story_text: str,
        source_filename: str,
        story_form_id: str,
        project_title: str | None = None,
        use_llm_first_pass: bool = False,
        llm_provider_id: str | None = None,
        llm_model: str | None = None,
    ) -> StoryProject:
        """Create a story project from raw story text."""

        if not self._registry.has_form(story_form_id):
            raise ValueError(f"Unknown story form: {story_form_id}")

        story_form = self._registry.get_form(story_form_id)

        llm_first_pass_text = ""
        llm_first_pass_draft_path = ""
        llm_first_pass_warning = ""
        parser_version = self._parser.version

        if use_llm_first_pass and llm_provider_id and llm_model:
            artifacts = self._llm_first_pass_parser.generate_first_pass_text(
                raw_story_text=raw_story_text,
                story_form=story_form,
                provider_id=llm_provider_id,
                model=llm_model,
            )
            llm_first_pass_text = artifacts.first_pass_text
            llm_first_pass_warning = artifacts.warning
            parser_version = self._parser.version

            if llm_first_pass_text.strip():
                try:
                    llm_first_pass_draft_path = self._save_llm_first_pass_draft(
                        project_title=project_title or source_filename,
                        source_filename=source_filename,
                        provider_id=llm_provider_id,
                        model=llm_model,
                        raw_story_text=raw_story_text,
                        generated_text=llm_first_pass_text,
                    )
                except Exception as exc:
                    msg = f"Could not save LLM first-pass draft: {exc}"
                    llm_first_pass_warning = f"{llm_first_pass_warning} | {msg}".strip(" |")

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
                parser_version=parser_version,
                llm_first_pass_used=bool(use_llm_first_pass and llm_provider_id and llm_model),
                llm_first_pass_provider=llm_provider_id,
                llm_first_pass_model=llm_model,
                llm_first_pass_text=llm_first_pass_text,
                llm_first_pass_draft_path=llm_first_pass_draft_path,
                llm_first_pass_warning=llm_first_pass_warning,
            ),
            raw_story_text=parse_result.raw_story_text,
            root_nodes=parse_result.root_nodes,
            selected_node_id=selected_node_id,
            dirty=False,
            llm_provider=llm_provider_id,
            llm_model=llm_model,
        )

    def _save_llm_first_pass_draft(
        self,
        project_title: str,
        source_filename: str,
        provider_id: str,
        model: str,
        raw_story_text: str,
        generated_text: str,
    ) -> str:
        """Persist LLM first-pass text into Drafts/ using project title."""

        safe_title = re.sub(r"[^A-Za-z0-9]+", "_", project_title.strip()).strip("_").lower() or "untitled_project"
        self._drafts_dir.mkdir(parents=True, exist_ok=True)
        draft_path = self._drafts_dir / f"{safe_title}_llm_first_pass.txt"
        header = (
            f"Project: {project_title}\n"
            f"Source: {source_filename}\n"
            f"Provider: {provider_id}\n"
            f"Model: {model}\n\n"
            "=== ORIGINAL RAW TEXT ===\n"
            f"{raw_story_text.strip()}\n\n"
            "=== LLM FIRST-PASS BREAKDOWN ===\n"
            f"{generated_text.strip()}\n"
        )
        draft_path.write_text(header, encoding="utf-8")
        return str(draft_path)

    @staticmethod
    def _first_component_id(root_nodes: list) -> str | None:
        for quarter in root_nodes:
            if quarter.children:
                return quarter.children[0].node_id
        return None
