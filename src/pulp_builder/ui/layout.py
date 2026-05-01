"""Main layout and app state wiring for the NiceGUI shell."""

from __future__ import annotations

from dataclasses import dataclass, field

from nicegui import ui

from pulp_builder.models.story_project import StoryProject
from pulp_builder.models.story_structure import StoryNode
from pulp_builder.services.importer import ImportService
from pulp_builder.services.status_bus import StatusBus
from pulp_builder.structures.registry import StoryStructureRegistry
from pulp_builder.ui.detail_panel import render_detail_panel
from pulp_builder.ui.import_dialog import show_import_dialog
from pulp_builder.ui.status_panel import render_status_panel
from pulp_builder.ui.structure_panel import render_structure_panel
from pulp_builder.ui.top_panel import render_top_panel


@dataclass(slots=True)
class AppState:
    """Shared UI state container."""

    current_project: StoryProject | None = None
    selected_node_id: str | None = None
    status_bus: StatusBus = field(default_factory=StatusBus)

    def find_node(self, node_id: str | None) -> StoryNode | None:
        if not self.current_project or not node_id:
            return None
        for quarter in self.current_project.root_nodes:
            if quarter.node_id == node_id:
                return quarter
            for component in quarter.children:
                if component.node_id == node_id:
                    return component
        return None

    def selected_node(self) -> StoryNode | None:
        return self.find_node(self.selected_node_id)


class LayoutController:
    """Thin controller for panel refresh and basic callbacks."""

    def __init__(self, state: AppState) -> None:
        self.state = state
        self._import_service = ImportService()
        self._registry = StoryStructureRegistry()

    def on_select_node(self, node_id: str) -> None:
        self.state.selected_node_id = node_id
        if self.state.current_project:
            self.state.current_project.selected_node_id = node_id
        self.state.status_bus.info(f"Selected node: {node_id}")
        self.refresh_all()

    def on_import(self) -> None:
        options = {story_form["id"]: story_form["label"] for story_form in self._registry.list_forms()}
        has_unsaved = bool(self.state.current_project and self.state.current_project.dirty)

        show_import_dialog(
            story_form_options=options,
            has_unsaved_changes=has_unsaved,
            on_import=self._import_story_text,
        )

    def _import_story_text(self, story_form_id: str, source_filename: str, raw_story_text: str) -> None:
        try:
            project = self._import_service.import_story_text(
                raw_story_text=raw_story_text,
                source_filename=source_filename,
                story_form_id=story_form_id,
            )
        except Exception as exc:
            self.state.status_bus.error(f"Could not import story: {exc}")
            render_status_panel.refresh(self.state)
            return

        self.state.current_project = project
        self.state.selected_node_id = project.selected_node_id

        placeholders = sum(
            1
            for quarter in project.root_nodes
            for component in quarter.children
            if component.required and component.is_placeholder
        )
        self.state.status_bus.info(
            f"Imported {source_filename} using {project.story_form_label}."
        )
        if placeholders:
            self.state.status_bus.warning(
                f"Inserted {placeholders} required placeholders for missing story components."
            )

        self.refresh_all()

    def on_save(self) -> None:
        self.state.status_bus.info("Save from UI is planned for Milestone 6.")
        render_status_panel.refresh(self.state)

    def on_load(self) -> None:
        self.state.status_bus.info("Load from UI is planned for Milestone 6.")
        render_status_panel.refresh(self.state)

    def on_export(self) -> None:
        self.state.status_bus.info("Export from UI is planned for Milestone 7.")
        render_status_panel.refresh(self.state)

    def refresh_all(self) -> None:
        render_top_panel.refresh(
            self.state,
            self.on_import,
            self.on_save,
            self.on_load,
            self.on_export,
        )
        render_structure_panel.refresh(self.state, self.on_select_node)
        render_detail_panel.refresh(self.state)
        render_status_panel.refresh(self.state)


def build_layout(state: AppState) -> None:
    """Render the four-panel app shell."""

    controller = LayoutController(state)

    with ui.column().classes("w-full h-screen p-2 gap-2"):
        render_top_panel(
            state,
            controller.on_import,
            controller.on_save,
            controller.on_load,
            controller.on_export,
        )

        with ui.row().classes("w-full flex-1 min-h-0 gap-2"):
            with ui.column().classes("w-1/3 h-full min-h-0"):
                render_structure_panel(state, controller.on_select_node)
            with ui.column().classes("w-2/3 h-full min-h-0"):
                render_detail_panel(state)

        render_status_panel(state)
