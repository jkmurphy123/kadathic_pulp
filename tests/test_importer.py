from pulp_builder.services.importer import ImportService


def _component_nodes(root_nodes):
    return [component for quarter in root_nodes for component in quarter.children]


def test_import_service_creates_valid_project(tmp_path) -> None:
    text = "Nessa seeks the idol in a drowned temple.\n\nA traitor reveals the map is cursed."
    file_path = tmp_path / "story_idea.txt"
    file_path.write_text(text, encoding="utf-8")

    service = ImportService()
    project = service.import_story_file(file_path=file_path, story_form_id="hybrid_weird_adventure")

    assert project.story_form_id == "hybrid_weird_adventure"
    assert project.story_form_label == "Hybrid Weird Adventure"
    assert project.raw_story_text == text
    assert project.import_info.source_filename == "story_idea.txt"
    assert project.import_info.parser_version == "deterministic-v1"


def test_import_service_creates_placeholders_for_missing_required_components() -> None:
    service = ImportService()
    project = service.import_story_text(
        raw_story_text="A lone thief enters a ruin.",
        source_filename="tiny.txt",
        story_form_id="howard_adventure",
        project_title="Tiny",
    )

    components = _component_nodes(project.root_nodes)
    assert any(node.required and node.is_placeholder for node in components)


def test_import_service_fixes_story_form_on_project() -> None:
    service = ImportService()
    project = service.import_story_text(
        raw_story_text="Scholar Elin writes a warning after seeing impossible stars.",
        source_filename="warning.txt",
        story_form_id="lovecraft_weird",
    )

    assert project.story_form_id == "lovecraft_weird"
    assert project.story_form_label == "Lovecraft Weird Tale"
