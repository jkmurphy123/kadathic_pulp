"""LLM provider configuration and connection testing via agent_foundry."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(slots=True)
class LLMTestResult:
    """Result of testing an LLM provider connection."""

    success: bool
    provider_id: str
    model: str
    message: str
    response_preview: str = ""


class LLMConnectionService:
    """Thin integration layer over agent_foundry provider adapters."""

    _PROVIDER_LABELS = {
        "mock": "Mock (Local Test)",
        "ollama": "Ollama",
        "openai_compatible": "OpenAI-Compatible",
    }

    _MODEL_SUGGESTIONS = {
        "mock": ["mock-model"],
        "ollama": ["llama3.1:8b", "qwen2.5:7b", "mistral:7b"],
        "openai_compatible": ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"],
    }

    def list_provider_options(self) -> dict[str, str]:
        """Return provider options for UI dropdowns."""

        return dict(self._PROVIDER_LABELS)

    def model_options_for_provider(self, provider_id: str) -> list[str]:
        """Return suggested models for a provider."""

        return list(self._MODEL_SUGGESTIONS.get(provider_id, []))

    def default_provider_id(self) -> str:
        """Return default provider ID for new projects."""

        return "mock"

    def default_model_for_provider(self, provider_id: str) -> str:
        """Return default model for a provider."""

        options = self.model_options_for_provider(provider_id)
        if options:
            return options[0]
        return "mock-model"

    def test_connection(self, provider_id: str, model: str) -> LLMTestResult:
        """Run health check and one minimal chat turn to confirm provider works."""

        try:
            provider = self._build_provider(provider_id=provider_id, model=model)
        except Exception as exc:
            return LLMTestResult(
                success=False,
                provider_id=provider_id,
                model=model,
                message=f"Provider setup failed: {exc}",
            )

        try:
            health = provider.health_check()
        except Exception as exc:
            return LLMTestResult(
                success=False,
                provider_id=provider_id,
                model=model,
                message=f"Health check failed: {exc}",
            )

        if not health.healthy:
            return LLMTestResult(
                success=False,
                provider_id=provider_id,
                model=model,
                message=health.message,
            )

        try:
            from agent_foundry.providers.base import ProviderChatRequest, ProviderMessage

            response = provider.chat(
                ProviderChatRequest(
                    model=model,
                    messages=[
                        ProviderMessage(
                            role="user",
                            content="Reply in one short line confirming connectivity.",
                        )
                    ],
                )
            )
        except Exception as exc:
            return LLMTestResult(
                success=False,
                provider_id=provider_id,
                model=model,
                message=f"Generation test failed: {exc}",
            )

        preview = (response.text or "").strip().replace("\n", " ")[:120]
        return LLMTestResult(
            success=True,
            provider_id=provider_id,
            model=model,
            message="Connection and generation test succeeded.",
            response_preview=preview,
        )


    def generate_text(
        self,
        provider_id: str,
        model: str,
        user_prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        """Run one provider chat generation and return text."""

        provider = self._build_provider(provider_id=provider_id, model=model)
        from agent_foundry.providers.base import ProviderChatRequest, ProviderMessage

        messages: list[ProviderMessage] = []
        if system_prompt:
            messages.append(ProviderMessage(role="system", content=system_prompt))
        messages.append(ProviderMessage(role="user", content=user_prompt))

        response = provider.chat(
            ProviderChatRequest(
                model=model,
                messages=messages,
            )
        )
        return response.text
    def _build_provider(self, provider_id: str, model: str):
        """Instantiate one configured agent_foundry provider adapter."""

        if provider_id == "mock":
            from agent_foundry.providers.mock import MockProvider

            return MockProvider(provider_id=provider_id, model=model or "mock-model")

        if provider_id == "ollama":
            from agent_foundry.providers.ollama import OllamaProvider

            return OllamaProvider(
                provider_id=provider_id,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                model=model,
            )

        if provider_id == "openai_compatible":
            from agent_foundry.providers.openai_compatible import OpenAICompatibleProvider

            return OpenAICompatibleProvider(
                provider_id=provider_id,
                base_url=os.getenv("OPENAI_COMPAT_BASE_URL", "https://api.openai.com"),
                api_key_env=os.getenv("OPENAI_COMPAT_API_KEY_ENV", "OPENAI_API_KEY"),
                model=model,
            )

        raise ValueError(f"Unsupported provider: {provider_id}")
