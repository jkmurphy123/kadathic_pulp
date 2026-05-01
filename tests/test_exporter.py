from pulp_builder.services.exporter import StoryExporter
from pulp_builder.services.importer import ImportService


def _all_components(project):
    return [component for quarter in project.root_nodes for component in quarter.children]


def test_exporter_generates_readable_text_with_placeholders() -> None:
    project = ImportService().import_story_text(
        raw_story_text="A warrior flees a ruined tower with a stolen idol.",
        source_filename="idea.txt",
        story_form_id="howard_adventure",
        project_title="Tower Run",
    )

    rendered = StoryExporter().export_to_text(project)

    assert "Title: Tower Run" in rendered
    assert "Story Form: Howard Adventure" in rendered
    assert "# Opening Menace" in rendered
    assert "## Hook with Menace" in rendered
    assert "[PLACEHOLDER: This required component has not been filled yet.]" in rendered


def test_exporter_includes_user_story_text_when_present() -> None:
    project = ImportService().import_story_text(
        raw_story_text="Scholar Miren discovers a cursed codex.",
        source_filename="notes.txt",
        story_form_id="lovecraft_weird",
        project_title="Codex Ash",
    )

    component = _all_components(project)[0]
    component.story_text = "Miren records the first impossible symbol before dawn."
    component.is_placeholder = False

    rendered = StoryExporter().export_to_text(project)

    assert "Miren records the first impossible symbol before dawn." in rendered


def test_exporter_writes_text_file(tmp_path) -> None:
    project = ImportService().import_story_text(
        raw_story_text="A map points to an island that should not exist.",
        source_filename="map.txt",
        story_form_id="hybrid_weird_adventure",
        project_title="False Island",
    )

    exporter = StoryExporter()
    out_file = tmp_path / "outline.txt"
    exporter.export_to_file(project, out_file)

    written = out_file.read_text(encoding="utf-8")
    assert "Title: False Island" in written
    assert "# Payoff and Final Sting" in written
