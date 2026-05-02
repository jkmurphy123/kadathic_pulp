from pulp_builder.services.llm_tag_applier import LLMTagApplierService, TagApplyRequest


class StubLLMConnection:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate_text(self, provider_id: str, model: str, user_prompt: str, system_prompt: str | None = None) -> str:
        self.prompts.append(user_prompt)
        if "room description" in user_prompt:
            return "the chamber stank of bleach and old rain"
        if "ominous sound" in user_prompt:
            return "a damp metallic tapping echoed beyond the ward door"
        return "replacement"


def test_apply_tags_replaces_each_bracket_and_preserves_other_text() -> None:
    service = LLMTagApplierService(llm_connection=StubLLMConnection())

    original = (
        "The doctor crossed the corridor, [add room description here], and paused. "
        "Then [add ominous sound cue] before opening the iron door."
    )
    updated, count = service.apply_tags(
        provider_id="mock",
        model="mock-model",
        request=TagApplyRequest(
            story_form_id="lovecraft_weird",
            story_form_label="Lovecraft Weird Tale",
            component_title="Hint of Deeper Menace",
            component_description="Signal rising dread.",
            guidance_prompt="What detail foreshadows worse danger?",
            source_text=original,
        ),
    )

    assert count == 2
    assert "[add room description here]" not in updated
    assert "[add ominous sound cue]" not in updated
    assert "The doctor crossed the corridor," in updated
    assert "before opening the iron door." in updated


def test_apply_tags_no_tags_returns_original_text() -> None:
    service = LLMTagApplierService(llm_connection=StubLLMConnection())
    original = "No bracket tags in this line."

    updated, count = service.apply_tags(
        provider_id="mock",
        model="mock-model",
        request=TagApplyRequest(
            story_form_id="howard_adventure",
            story_form_label="Howard Adventure",
            component_title="Hook with Menace",
            component_description="",
            guidance_prompt="",
            source_text=original,
        ),
    )

    assert count == 0
    assert updated == original
