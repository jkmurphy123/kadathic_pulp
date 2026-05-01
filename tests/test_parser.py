from pulp_builder.services.parser import DeterministicParser
from pulp_builder.structures.registry import StoryStructureRegistry


def _component_nodes(root_nodes):
    return [component for quarter in root_nodes for component in quarter.children]


def test_parser_preserves_raw_input_text() -> None:
    raw_text = "Aria finds a map in the ruined tower.\n\nA cult follows her into the jungle."
    form = StoryStructureRegistry().get_form("hybrid_weird_adventure")

    result = DeterministicParser().parse(raw_story_text=raw_text, story_form=form)

    assert result.raw_story_text == raw_text


def test_parser_inserts_placeholders_for_missing_required_components() -> None:
    raw_text = "Karn runs through the city after a knife fight."
    form = StoryStructureRegistry().get_form("howard_adventure")

    result = DeterministicParser().parse(raw_story_text=raw_text, story_form=form)
    components = _component_nodes(result.root_nodes)

    placeholder_count = sum(1 for node in components if node.required and node.is_placeholder)

    assert placeholder_count > 0


def test_parser_assigns_at_least_one_component_when_text_has_clues() -> None:
    raw_text = (
        "Professor Hale seeks proof in a crumbling archive and discovers a cursed manuscript.\n\n"
        "At dawn, the ritual reveals the truth and he barely survives."
    )
    form = StoryStructureRegistry().get_form("lovecraft_weird")

    result = DeterministicParser().parse(raw_story_text=raw_text, story_form=form)
    components = _component_nodes(result.root_nodes)

    populated = [node for node in components if node.story_text.strip()]

    assert len(populated) >= 1
    assert any(node.extracted_evidence for node in populated)


def test_parser_uses_tagged_outline_format_when_present() -> None:
    raw_text = (
        "## Opening Menace\n"
        "- Hook with Menace: A doctor meets a girl clutching a doll in an asylum.\n"
        "- Hero Desire: The doctor wants to uncover her history.\n"
        "- Initial Trouble: The asylum director pressures the doctor to proceed.\n"
        "- Hint of Deeper Menace: The doll appears linked to a dead twin.\n"
    )
    form = StoryStructureRegistry().get_form("lovecraft_weird")

    result = DeterministicParser().parse(raw_story_text=raw_text, story_form=form)
    components = _component_nodes(result.root_nodes)

    hook = next(node for node in components if node.node_id == "q1-hook-with-menace")
    hero_desire = next(node for node in components if node.node_id == "q1-hero-desire")

    assert "doctor meets a girl" in hook.story_text.lower()
    assert "wants to uncover her history" in hero_desire.story_text.lower()
    assert hook.is_placeholder is False


def test_parser_story_text_tag_overrides_component_summary() -> None:
    raw_text = (
        "## Opening Menace\n"
        "- Hook with Menace: Short summary line.\n"
        "- Story Text: Full raw section text for hook with menace goes here.\n"
    )
    form = StoryStructureRegistry().get_form("howard_adventure")

    result = DeterministicParser().parse(raw_story_text=raw_text, story_form=form)
    components = _component_nodes(result.root_nodes)
    hook = next(node for node in components if node.node_id == "q1-hook-with-menace")

    assert hook.story_text == "Full raw section text for hook with menace goes here."
    assert hook.extracted_evidence
    assert hook.extracted_evidence[0].notes == "Assigned from explicit Story Text tag."
