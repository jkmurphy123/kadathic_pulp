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


def test_import_service_llm_first_pass_with_mock_provider(tmp_path) -> None:
    service = ImportService(drafts_dir=tmp_path / "Drafts")
    project = service.import_story_text(
        raw_story_text="Rane finds a cursed chart and sails toward a drowned city.",
        source_filename="llm.txt",
        story_form_id="hybrid_weird_adventure",
        project_title="Rane Voyage",
        use_llm_first_pass=True,
        llm_provider_id="mock",
        llm_model="mock-model",
    )

    assert project.import_info.llm_first_pass_used is True
    assert project.import_info.parser_version == "deterministic-v1"
    assert project.import_info.llm_first_pass_provider == "mock"
    assert project.import_info.llm_first_pass_model == "mock-model"
    assert project.import_info.llm_first_pass_text.strip()
    assert project.import_info.llm_first_pass_draft_path.endswith("rane_voyage_llm_first_pass.txt")
