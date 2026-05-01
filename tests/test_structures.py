from pulp_builder.structures.registry import StoryStructureRegistry


EXPECTED_FORMS = {
    "howard_adventure",
    "lovecraft_weird",
    "hybrid_weird_adventure",
}
EXPECTED_QUARTERS = [
    "Opening Menace",
    "Deepening Trouble",
    "Trap and Terrible Revelation",
    "Payoff and Final Sting",
]


def test_registry_contains_expected_forms() -> None:
    registry = StoryStructureRegistry()

    forms = registry.list_forms()
    form_ids = {item["id"] for item in forms}

    assert form_ids == EXPECTED_FORMS


def test_each_form_has_four_expected_quarters() -> None:
    registry = StoryStructureRegistry()

    for form_id in EXPECTED_FORMS:
        form = registry.get_form(form_id)
        quarter_titles = [quarter["title"] for quarter in form["quarters"]]

        assert len(form["quarters"]) == 4
        assert quarter_titles == EXPECTED_QUARTERS


def test_required_components_include_guidance_prompts() -> None:
    registry = StoryStructureRegistry()

    for form_id in EXPECTED_FORMS:
        form = registry.get_form(form_id)
        for quarter in form["quarters"]:
            for component in quarter["components"]:
                if component["required"]:
                    assert component["guidance_prompt"].strip()
