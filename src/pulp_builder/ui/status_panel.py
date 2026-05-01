"""Bottom status panel rendering."""

from __future__ import annotations

from nicegui import ui


LEVEL_CLASSES = {
    "info": "text-blue-700",
    "warning": "text-amber-700",
    "error": "text-red-700",
}


@ui.refreshable
def render_status_panel(state) -> None:
    """Render rolling status messages."""

    with ui.card().classes("w-full py-2"):
        ui.label("Status").classes("text-sm font-medium")
        messages = state.status_bus.recent()
        if not messages:
            ui.label("INFO: Ready.").classes("text-sm text-blue-700")
            return

        for message in messages[-6:]:
            classes = LEVEL_CLASSES.get(message.level, "text-gray-700")
            ui.label(f"{message.level.upper()}: {message.text}").classes(f"text-sm {classes}")
