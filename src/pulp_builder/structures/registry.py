"""Story form registry."""

from __future__ import annotations

from pulp_builder.structures.lester_dent import build_all_story_forms


class StoryStructureRegistry:
    """In-memory registry for available story forms."""

    def __init__(self) -> None:
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
