"""Application entrypoint for Pulp Structure Builder."""

from __future__ import annotations

from nicegui import ui

from pulp_builder.services.app_config_store import AppConfigStore
from pulp_builder.services.importer import ImportService
from pulp_builder.ui.layout import AppState, build_layout


def _build_sample_project():
    importer = ImportService()
    sample_text = (
        "Captain Sorel takes a paid mission to recover a brass idol from a drowned temple.\n\n"
        "At the harbor, a mutilated courier delivers a map and dies whispering about the tide cult.\n\n"
        "Inside the ruins, the guide betrays Sorel and opens a flooded chamber where something ancient watches."
    )
    project = importer.import_story_text(
        raw_story_text=sample_text,
        source_filename="sample_story_idea.txt",
        story_form_id="hybrid_weird_adventure",
        project_title="Brass Idol at Low Tide",
    )

    for quarter in project.root_nodes:
        for component in quarter.children:
            if component.story_text.strip():
                component.completion_state = "drafted"
            elif component.is_placeholder:
                component.completion_state = "missing"

    return project


def main() -> None:
    """Run the NiceGUI application shell."""

    AppConfigStore().ensure_exists()
    project = _build_sample_project()
    state = AppState(current_project=project, selected_node_id=project.selected_node_id)
    state.status_bus.info("Loaded sample project for Milestone 4 shell.")
    state.status_bus.info("Select a node in the left panel to inspect details.")

    build_layout(state)
    ui.run(title="Pulp Structure Builder")


if __name__ in {"__main__", "__mp_main__"}:
    main()
