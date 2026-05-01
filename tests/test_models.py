from datetime import datetime, timezone

from pulp_builder.models.story_project import ImportInfo, StoryProject
from pulp_builder.models.story_structure import ExtractedEvidence, StoryNode


def test_story_project_model_instantiation() -> None:
    now = datetime.now(timezone.utc)
    project = StoryProject(
        project_id="project-001",
        title="Test Project",
        story_form_id="howard_adventure",
        story_form_label="Howard Adventure",
        created_at=now,
        updated_at=now,
        import_info=ImportInfo(
            source_filename="idea.txt",
            imported_at=now,
            parser_version="deterministic-v1",
        ),
        raw_story_text="A rough note.",
        root_nodes=[
            StoryNode(
                node_id="q1",
                title="Opening Menace",
                node_type="quarter",
                order_index=0,
            )
        ],
    )

    assert project.project_id == "project-001"
    assert project.import_info.source_filename == "idea.txt"


def test_story_node_contains_evidence_and_children() -> None:
    node = StoryNode(
        node_id="q1-hook-with-menace",
        parent_id="q1",
        title="Hook with Menace",
        node_type="component",
        order_index=0,
        extracted_evidence=[
            ExtractedEvidence(
                source="paragraph",
                text="A bloodied sailor staggers into the dockside inn.",
                confidence=0.75,
            )
        ],
        children=[],
    )

    assert node.extracted_evidence[0].source == "paragraph"
    assert node.completion_state == "missing"
