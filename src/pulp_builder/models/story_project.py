"""Project-level data models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from pulp_builder.models.story_structure import StoryNode


class ImportInfo(BaseModel):
    """Metadata about imported source text."""

    source_filename: str
    imported_at: datetime
    parser_version: str
    llm_first_pass_used: bool = False
    llm_first_pass_provider: str | None = None
    llm_first_pass_model: str | None = None
    llm_first_pass_text: str = ""
    llm_first_pass_draft_path: str = ""
    llm_first_pass_warning: str = ""


class StoryProject(BaseModel):
    """Full persisted project model."""

    project_id: str
    title: str
    story_form_id: str
    story_form_label: str
    created_at: datetime
    updated_at: datetime
    import_info: ImportInfo
    raw_story_text: str
    root_nodes: list[StoryNode] = Field(default_factory=list)
    selected_node_id: str | None = None
    dirty: bool = False
    llm_provider: str | None = None
    llm_model: str | None = None
