"""Top control panel rendering."""

from __future__ import annotations

from collections.abc import Callable

from nicegui import events
from nicegui import ui


@ui.refreshable
def render_top_panel(
    state,
    provider_options: dict[str, str],
    model_options: list[str],
    on_provider_change: Callable[[str], None],
    on_model_change: Callable[[str], None],
    on_test_llm_connection: Callable[[], None],
    on_import,
    on_new_project,
    on_import_tagged_draft,
    on_save,
    on_load,
    on_export,
) -> None:
    """Render top project metadata and control buttons."""

    project = state.current_project
    project_name = project.title if project else "(no project)"
    story_form = project.story_form_label if project else "(none)"
    source_file = project.import_info.source_filename if project else "(none)"
    dirty_label = "Unsaved Changes" if project and project.dirty else "Saved"
    current_provider = (project.llm_provider if project else None) or ""
    current_model = (project.llm_model if project else None) or ""

    with ui.card().classes("w-full py-2 bg-slate-50"):
        with ui.row().classes("w-full items-center justify-between gap-4 no-wrap"):
            with ui.row().classes("items-center gap-4 no-wrap"):
                ui.input(
                    "Project",
                    value=project_name,
                ).props("dense outlined readonly").classes("min-w-[16rem]")
                ui.label(f"Story Form: {story_form}").classes("text-sm")
                ui.label(f"Imported File: {source_file}").classes("text-sm")
                state_classes = "text-amber-700" if dirty_label == "Unsaved Changes" else "text-green-700"
                ui.label(f"State: {dirty_label}").classes(f"text-sm font-medium {state_classes}")
                def _handle_provider_change(event: events.ValueChangeEventArguments) -> None:
                    on_provider_change(event.value or "")

                def _handle_model_change(event: events.ValueChangeEventArguments) -> None:
                    on_model_change(event.value or "")

                model_select_options = {item: item for item in model_options}
                ui.select(
                    options=provider_options,
                    value=current_provider if current_provider in provider_options else None,
                    label="LLM Provider",
                    on_change=_handle_provider_change,
                ).props("dense outlined").classes("min-w-[12rem]")
                ui.select(
                    options=model_select_options,
                    value=current_model if current_model in model_select_options else None,
                    label="LLM Model",
                    on_change=_handle_model_change,
                ).props("dense outlined").classes("min-w-[12rem]")
                ui.button("Test LLM Connection", on_click=on_test_llm_connection).props("outline size=sm")

            with ui.row().classes("items-center gap-2"):
                ui.button("Import Story", on_click=on_import).props("outline size=sm")
                ui.button("New Project", on_click=on_new_project).props("outline size=sm")
                ui.button("Import Tagged Draft", on_click=on_import_tagged_draft).props("outline size=sm")
                ui.button("Save Project", on_click=on_save).props("outline size=sm")
                ui.button("Load Project", on_click=on_load).props("outline size=sm")
                ui.button("Export Story", on_click=on_export).props("outline size=sm")
