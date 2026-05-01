"""Right detail panel rendering."""

from __future__ import annotations

from nicegui import ui


@ui.refreshable
def render_detail_panel(state) -> None:
    """Render selected component details."""

    with ui.card().classes("w-full h-full"):
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
            ui.label(f"Required: {'Yes' if node.required else 'No'}").classes("text-sm")
            ui.label(f"Placeholder: {'Yes' if node.is_placeholder else 'No'}").classes("text-sm")
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

            story_text_value = node.story_text if node.story_text else ""
            ui.textarea("Story Text", value=story_text_value).props("readonly autogrow").classes("w-full")
