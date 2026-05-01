"""Right detail panel rendering."""

from __future__ import annotations

from collections.abc import Callable

from nicegui import events, ui


@ui.refreshable
def render_detail_panel(state, on_story_text_change: Callable[[str], None]) -> None:
    """Render selected component details."""

    with ui.card().classes("w-full h-full overflow-auto bg-white"):
        ui.label("Component Details").classes("text-base font-medium")

        project = state.current_project
        node = state.selected_node()
        if not project or not node:
            ui.label("Select a structure node to inspect details.").classes("text-sm text-gray-600")
            return

        parent = state.find_node(node.parent_id) if node.parent_id else None

        with ui.column().classes("gap-2 w-full"):
            ui.label(f"Title: {node.title}").classes("text-sm")
            ui.label(f"Quarter: {parent.title if parent else '(none)'}").classes("text-sm")
            ui.label(f"Description: {node.description or '(none)'}").classes("text-sm")
            with ui.row().classes("gap-2 items-center"):
                ui.badge("Required" if node.required else "Optional").props(
                    "color=primary" if node.required else "outline"
                )
                ui.badge("Placeholder" if node.is_placeholder else "Has Text").props(
                    "color=warning" if node.is_placeholder else "color=positive"
                )
                ui.badge(f"State: {node.completion_state}").props("outline")
            if node.missing_reason.strip():
                ui.label(f"Missing Reason: {node.missing_reason}").classes("text-sm text-amber-700")
            ui.label(f"Guidance: {node.guidance_prompt or '(none)'}").classes("text-sm")

            if node.suggested_questions:
                ui.label("Suggested Questions:").classes("text-sm font-medium")
                for question in node.suggested_questions:
                    ui.label(f"- {question}").classes("text-sm")

            if node.extracted_evidence:
                ui.label("Extracted Evidence:").classes("text-sm font-medium")
                for evidence in node.extracted_evidence:
                    ui.label(f"- {evidence.source}: {evidence.text}").classes("text-sm")

            def _handle_change(event: events.ValueChangeEventArguments) -> None:
                on_story_text_change(event.value or "")

            story_text_value = node.story_text if node.story_text else ""
            ui.textarea("Story Text", value=story_text_value, on_change=_handle_change).props("autogrow").classes(
                "w-full"
            )
