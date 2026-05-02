"""Story form registry."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from pulp_builder.structures.lester_dent import build_all_story_forms

if TYPE_CHECKING:
    from pulp_builder.services.app_config_store import AppConfigStore


class StoryStructureRegistry:
    """In-memory registry for available story forms."""

    def __init__(
        self,
        forms: list[dict[str, Any]] | None = None,
        config_store: "AppConfigStore | None" = None,
    ) -> None:
        if forms is not None:
            self._forms = self._forms_from_list(forms)
            return

        if config_store is None:
            from pulp_builder.services.app_config_store import AppConfigStore

            store = AppConfigStore()
        else:
            store = config_store
        config = store.load()
        if config.story_forms:
            self._forms = self._forms_from_list(config.story_forms)
        else:
            self._forms = build_all_story_forms()

    def list_forms(self) -> list[dict]:
        """Return all story forms as list sorted by label."""

        return sorted(self._forms.values(), key=lambda item: item["label"])

    def get_form(self, form_id: str) -> dict:
        """Return one story form by ID."""

        if form_id not in self._forms:
            raise KeyError(f"Unknown story form: {form_id}")
        return self._forms[form_id]

    def has_form(self, form_id: str) -> bool:
        """Check whether the form exists."""

        return form_id in self._forms

    @staticmethod
    def _forms_from_list(forms: list[dict[str, Any]]) -> dict[str, dict]:
        normalized: dict[str, dict] = {}
        for form in forms:
            form_id = form.get("id")
            if isinstance(form_id, str) and form_id:
                normalized[form_id] = form
        if normalized:
            return normalized
        return build_all_story_forms()
