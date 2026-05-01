"""Persistence for app-level settings across sessions."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class AppConfig(BaseModel):
    """App-level persisted settings."""

    llm_provider: str | None = None
    llm_model: str | None = None


class AppConfigStore:
    """Load/save app-level config JSON."""

    def __init__(self, path: str | Path = "config/app_config.json") -> None:
        self.path = Path(path)

    def load(self) -> AppConfig:
        """Load app config or return defaults when missing/invalid."""

        if not self.path.exists():
            return AppConfig()
        try:
            raw = self.path.read_text(encoding="utf-8")
            return AppConfig.model_validate_json(raw)
        except Exception:
            return AppConfig()

    def save(self, config: AppConfig) -> Path:
        """Persist app config and return written path."""

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(f"{config.model_dump_json(indent=2)}\n", encoding="utf-8")
        return self.path
