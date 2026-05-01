"""Text exporter for story projects."""

from __future__ import annotations

from pathlib import Path

from pulp_builder.models.story_project import StoryProject
from pulp_builder.models.story_structure import StoryNode


class StoryExporter:
    """Export projects into readable plain-text outlines."""

    def export_to_text(self, project: StoryProject) -> str:
        """Render project as structured text."""

        lines: list[str] = [
            f"Title: {project.title}",
            f"Story Form: {project.story_form_label}",
            f"Imported From: {project.import_info.source_filename}",
            "",
        ]

        for quarter in project.root_nodes:
            lines.append(f"# {quarter.title}")
            lines.append("")
            for component in quarter.children:
                lines.extend(self._render_component(component))

        return "\n".join(lines).rstrip() + "\n"

    def export_to_file(self, project: StoryProject, target_path: str | Path) -> Path:
        """Export project to text file and return output path."""

        path = Path(target_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.export_to_text(project), encoding="utf-8")
        return path

    @staticmethod
    def _render_component(component: StoryNode) -> list[str]:
        lines = [
            f"## {component.title}",
            "",
            "Description:",
            component.description or "(none)",
            "",
            "Guidance:",
            component.guidance_prompt or "(none)",
            "",
            "Story Text:",
        ]

        if component.story_text.strip():
            lines.append(component.story_text.strip())
        elif component.is_placeholder:
            lines.append("[PLACEHOLDER: This required component has not been filled yet.]")
            if component.missing_reason.strip():
                lines.append(f"Missing reason: {component.missing_reason.strip()}")
            if component.guidance_prompt.strip():
                lines.append(f"Guidance: {component.guidance_prompt.strip()}")
        else:
            lines.append("(empty)")

        if component.suggested_questions:
            lines.append("")
            lines.append("Suggested Questions:")
            for question in component.suggested_questions:
                lines.append(f"- {question}")

        lines.extend(["", ""])
        return lines
