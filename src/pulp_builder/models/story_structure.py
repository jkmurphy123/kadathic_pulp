"""Story structure domain models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


CompletionState = Literal["missing", "partial", "drafted", "complete"]
NodeType = Literal["quarter", "component"]


class ExtractedEvidence(BaseModel):
    """Extracted snippet tied to a story component."""

    source: Literal["paragraph", "sentence", "keyword", "manual"]
    text: str
    confidence: float = 0.0
    notes: str = ""


class StoryNode(BaseModel):
    """Tree node representing either a quarter or component."""

    node_id: str
    parent_id: str | None = None
    title: str
    node_type: NodeType
    order_index: int
    description: str = ""
    guidance_prompt: str = ""
    suggested_questions: list[str] = Field(default_factory=list)
    required: bool = True
    is_placeholder: bool = False
    was_placeholder: bool = False
    missing_reason: str = ""
    completion_state: CompletionState = "missing"
    extracted_evidence: list[ExtractedEvidence] = Field(default_factory=list)
    story_text: str = ""
    children: list["StoryNode"] = Field(default_factory=list)
