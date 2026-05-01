from pulp_builder.services.importer import ImportService
from pulp_builder.services.project_store import ProjectStore


def test_project_store_round_trip_preserves_project_data(tmp_path) -> None:
    importer = ImportService()
    project = importer.import_story_text(
        raw_story_text=(
            "Captain Ives seeks a relic in a drowned city.\n\n"
            "His ally betrays him when the idol is revealed to be alive."
        ),
        source_filename="seed.txt",
        story_form_id="hybrid_weird_adventure",
        project_title="Drowned Vault",
    )

    # Simulate user edits before save.
    first_component = project.root_nodes[0].children[0]
    first_component.story_text = "A storm drives the crew into black waters."
    first_component.is_placeholder = False
    project.selected_node_id = first_component.node_id
    project.llm_provider = "mock"
    project.llm_model = "mock-model"
    project.dirty = True

    store = ProjectStore()
    out_path = tmp_path / "project.json"
    store.save(project, out_path)
    loaded = store.load(out_path)

    assert loaded.project_id == project.project_id
    assert loaded.title == "Drowned Vault"
    assert loaded.story_form_id == "hybrid_weird_adventure"
    assert loaded.raw_story_text.startswith("Captain Ives seeks")
    assert loaded.selected_node_id == first_component.node_id
    assert loaded.llm_provider == "mock"
    assert loaded.llm_model == "mock-model"
    assert loaded.root_nodes[0].children[0].story_text == "A storm drives the crew into black waters."
    assert loaded.dirty is False
