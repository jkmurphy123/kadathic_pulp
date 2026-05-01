"""Top control panel rendering."""

from __future__ import annotations

from nicegui import ui


@ui.refreshable
def render_top_panel(state, on_import, on_save, on_load, on_export) -> None:
    """Render top project metadata and control buttons."""

    project = state.current_project
    project_name = project.title if project else "(no project)"
    story_form = project.story_form_label if project else "(none)"
    source_file = project.import_info.source_filename if project else "(none)"
    dirty_label = "Unsaved Changes" if project and project.dirty else "Saved"

    with ui.card().classes("w-full py-2"):
        with ui.row().classes("w-full items-center justify-between gap-4"):
            with ui.row().classes("items-center gap-6"):
                ui.label(f"Project: {project_name}").classes("text-sm")
                ui.label(f"Story Form: {story_form}").classes("text-sm")
                ui.label(f"Imported File: {source_file}").classes("text-sm")
                state_classes = "text-amber-700" if dirty_label == "Unsaved Changes" else "text-green-700"
                ui.label(f"State: {dirty_label}").classes(f"text-sm font-medium {state_classes}")

            with ui.row().classes("items-center gap-2"):
                ui.button("Import Story", on_click=on_import).props("outline size=sm")
                ui.button("Save Project", on_click=on_save).props("outline size=sm")
                ui.button("Load Project", on_click=on_load).props("outline size=sm")
                ui.button("Export Story", on_click=on_export).props("outline size=sm")
