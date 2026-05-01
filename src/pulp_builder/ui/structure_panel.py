"""Left story structure panel rendering."""

from __future__ import annotations

from nicegui import ui


def _component_marker(component) -> str:
    if component.is_placeholder:
        return "[MISSING]"
    if component.story_text.strip():
        return "[DRAFTED]"
    if not component.required:
        return "[OPTIONAL]"
    return "[EMPTY]"


@ui.refreshable
def render_structure_panel(state, on_select_node) -> None:
    """Render expandable story structure tree."""

    with ui.card().classes("w-full h-full overflow-auto bg-white"):
        ui.label("Story Structure").classes("text-base font-medium")
        project = state.current_project
        if not project:
            ui.label("No project loaded.").classes("text-sm text-gray-600")
            return

        total_components = 0
        missing_components = 0
        drafted_components = 0
        for quarter in project.root_nodes:
            for component in quarter.children:
                total_components += 1
                if component.is_placeholder:
                    missing_components += 1
                elif component.story_text.strip():
                    drafted_components += 1

        with ui.row().classes("gap-2 items-center text-xs"):
            ui.badge(f"Components: {total_components}").props("outline")
            ui.badge(f"Drafted: {drafted_components}").props("color=positive")
            ui.badge(f"Missing: {missing_components}").props("color=warning")

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
