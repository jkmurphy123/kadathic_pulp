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
