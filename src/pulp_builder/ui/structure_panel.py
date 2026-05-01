"""Left story structure panel rendering."""

from __future__ import annotations

from nicegui import ui


def _component_marker(component) -> str:
    if component.is_placeholder:
        return "[!]"
    if component.story_text.strip():
        return "[✓]"
    if not component.required:
        return "[?]"
    return "[ ]"


@ui.refreshable
def render_structure_panel(state, on_select_node) -> None:
    """Render expandable story structure tree."""

    with ui.card().classes("w-full h-full"):
        ui.label("Story Structure").classes("text-base font-medium")
        project = state.current_project
        if not project:
            ui.label("No project loaded.").classes("text-sm text-gray-600")
            return

        tree_nodes = []
        for quarter in project.root_nodes:
            tree_nodes.append(
                {
                    "id": quarter.node_id,
                    "label": quarter.title,
                    "children": [
                        {
                            "id": component.node_id,
                            "label": f"{_component_marker(component)} {component.title}",
                        }
                        for component in quarter.children
                    ],
                }
            )

        def _handle_select(event) -> None:
            selected = event.value
            if selected:
                on_select_node(selected)

        ui.tree(tree_nodes, node_key="id", label_key="label", on_select=_handle_select).props(
            "default-expand-all selected-color=primary"
        )
