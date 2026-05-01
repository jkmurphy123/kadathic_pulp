"""LLM text rewriting service for selected story components."""

from __future__ import annotations

from dataclasses import dataclass

from pulp_builder.services.llm_connection import LLMConnectionService


STYLE_GUIDANCE = {
    "howard_adventure": (
        "Write in sword-and-sorcery pulp style: muscular prose, physical danger, treachery, "
        "violent stakes, and grim momentum."
    ),
    "lovecraft_weird": (
        "Write in weird-cosmic dread style: uncanny detail, investigative tone, mounting dread, "
        "and ominous implication."
    ),
    "hybrid_weird_adventure": (
        "Write in weird-adventure pulp style: fast mission-driven pacing, physical peril, "
        "betrayal pressure, and uncanny horror undertones."
    ),
}


@dataclass(slots=True)
class RewriteRequest:
    """Inputs for component rewrite."""

    story_form_id: str
    story_form_label: str
    component_title: str
    component_description: str
    guidance_prompt: str
    source_text: str


class LLMRewriteService:
    """Rewrite selected component text with style/context-aware prompting."""

    def __init__(self, llm_connection: LLMConnectionService | None = None) -> None:
        self._llm = llm_connection or LLMConnectionService()

    def rewrite(self, provider_id: str, model: str, request: RewriteRequest) -> str:
        """Rewrite source text based on project style and selected component context."""

        style_instruction = STYLE_GUIDANCE.get(
            request.story_form_id,
            "Write in vivid pulp style while preserving key facts and intent.",
        )
        system_prompt = (
            "You are an expert pulp fiction editor. Rewrite text while preserving core meaning, "
            "improving clarity and atmosphere, and matching required story structure intent."
        )
        user_prompt = (
            f"Project Story Form: {request.story_form_label} ({request.story_form_id})\n"
            f"Selected Lester Dent Component: {request.component_title}\n"
            f"Component Description: {request.component_description or '(none)'}\n"
            f"Guidance Prompt: {request.guidance_prompt or '(none)'}\n"
            f"Style Direction: {style_instruction}\n\n"
            "Task:\n"
            "Rewrite the source text so it strongly reflects the selected component intent. "
            "Keep the same core events and facts, but improve tone, specificity, and tension.\n\n"
            "Source Text:\n"
            f"{request.source_text.strip()}\n"
        )

        rewritten = self._llm.generate_text(
            provider_id=provider_id,
            model=model,
            user_prompt=user_prompt,
            system_prompt=system_prompt,
        )
        return rewritten.strip()
