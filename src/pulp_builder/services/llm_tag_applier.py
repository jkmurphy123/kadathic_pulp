"""LLM tag application service for inline bracket instructions."""

from __future__ import annotations

from dataclasses import dataclass
import re

from pulp_builder.services.llm_connection import LLMConnectionService


TAG_PATTERN = re.compile(r"\[([^\[\]\n]+)\]")

STYLE_GUIDANCE = {
    "howard_adventure": "Use sword-and-sorcery pulp tone with vivid physical detail and danger.",
    "lovecraft_weird": "Use uncanny, dread-heavy weird tone with eerie sensory detail.",
    "hybrid_weird_adventure": "Use fast weird-adventure pulp tone with danger and ominous undertones.",
}


@dataclass(slots=True)
class TagApplyRequest:
    """Inputs for tag substitution."""

    story_form_id: str
    story_form_label: str
    component_title: str
    component_description: str
    guidance_prompt: str
    source_text: str


class LLMTagApplierService:
    """Replace bracketed inline instructions with LLM-generated text."""

    def __init__(self, llm_connection: LLMConnectionService | None = None) -> None:
        self._llm = llm_connection or LLMConnectionService()

    def apply_tags(self, provider_id: str, model: str, request: TagApplyRequest) -> tuple[str, int]:
        """Apply all bracket tags and return updated text + replacement count."""

        matches = list(TAG_PATTERN.finditer(request.source_text))
        if not matches:
            return request.source_text, 0

        style_instruction = STYLE_GUIDANCE.get(
            request.story_form_id,
            "Use vivid pulp prose and preserve continuity.",
        )
        system_prompt = (
            "You are a precise fiction editor. "
            "Return only the replacement text for each instruction, no brackets and no commentary."
        )

        replacements: list[str] = []
        for match in matches:
            instruction = match.group(1).strip()
            user_prompt = (
                f"Story Form: {request.story_form_label} ({request.story_form_id})\n"
                f"Selected Component: {request.component_title}\n"
                f"Component Description: {request.component_description or '(none)'}\n"
                f"Guidance Prompt: {request.guidance_prompt or '(none)'}\n"
                f"Style Direction: {style_instruction}\n\n"
                "Task: Write only the exact replacement text for this inline instruction.\n"
                "Do not include brackets. Do not include explanations.\n\n"
                f"Inline Instruction: {instruction}\n"
            )
            generated = self._llm.generate_text(
                provider_id=provider_id,
                model=model,
                user_prompt=user_prompt,
                system_prompt=system_prompt,
            ).strip()
            replacements.append(generated if generated else instruction)

        parts: list[str] = []
        cursor = 0
        for match, replacement in zip(matches, replacements):
            parts.append(request.source_text[cursor:match.start()])
            parts.append(replacement)
            cursor = match.end()
        parts.append(request.source_text[cursor:])
        return "".join(parts), len(matches)

