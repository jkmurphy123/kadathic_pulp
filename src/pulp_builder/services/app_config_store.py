"""Persistence for app-level settings across sessions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic import Field

from pulp_builder.structures.lester_dent import default_story_forms


class AppConfig(BaseModel):
    """App-level persisted settings."""

    llm_provider: str | None = None
    llm_model: str | None = None
    story_forms: list[dict[str, Any]] = Field(default_factory=default_story_forms)


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
            loaded = AppConfig.model_validate_json(raw)
            # If the file was created before story forms were configurable,
            # keep backward compatibility by injecting defaults.
            if not loaded.story_forms:
                loaded.story_forms = default_story_forms()
            return loaded
        except Exception:
            return AppConfig()

    def save(self, config: AppConfig) -> Path:
        """Persist app config and return written path."""

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(f"{config.model_dump_json(indent=2)}\n", encoding="utf-8")
        return self.path

    def ensure_exists(self) -> Path:
        """Ensure config file exists on disk with current defaults."""

        config = self.load()
        return self.save(config)
