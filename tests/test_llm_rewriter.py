from pulp_builder.services.llm_rewriter import LLMRewriteService, RewriteRequest


class StubLLMConnection:
    def __init__(self) -> None:
        self.last_provider = ""
        self.last_model = ""
        self.last_user_prompt = ""
        self.last_system_prompt = ""

    def generate_text(self, provider_id: str, model: str, user_prompt: str, system_prompt: str | None = None) -> str:
        self.last_provider = provider_id
        self.last_model = model
        self.last_user_prompt = user_prompt
        self.last_system_prompt = system_prompt or ""
        return "rewritten text"


def test_llm_rewriter_builds_contextual_prompt() -> None:
    stub = StubLLMConnection()
    service = LLMRewriteService(llm_connection=stub)

    rewritten = service.rewrite(
        provider_id="mock",
        model="mock-model",
        request=RewriteRequest(
            story_form_id="lovecraft_weird",
            story_form_label="Lovecraft Weird Tale",
            component_title="Hint of Deeper Menace",
            component_description="Signal unseen dread.",
            guidance_prompt="What detail suggests something older and worse?",
            source_text="The doctor walked down the corridor.",
        ),
    )

    assert rewritten == "rewritten text"
    assert stub.last_provider == "mock"
    assert stub.last_model == "mock-model"
    assert "Hint of Deeper Menace" in stub.last_user_prompt
    assert "Lovecraft Weird Tale" in stub.last_user_prompt
    assert "doctor walked down the corridor" in stub.last_user_prompt
