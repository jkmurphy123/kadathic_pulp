"""Main layout and app state wiring for the NiceGUI shell."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

from nicegui import events, run, ui

from pulp_builder.models.story_project import StoryProject
from pulp_builder.models.story_structure import StoryNode
from pulp_builder.services.app_config_store import AppConfig, AppConfigStore
from pulp_builder.services.exporter import StoryExporter
from pulp_builder.services.importer import ImportService
from pulp_builder.services.llm_connection import LLMConnectionService
from pulp_builder.services.llm_rewriter import LLMRewriteService, RewriteRequest
from pulp_builder.services.llm_tag_applier import LLMTagApplierService, TagApplyRequest
from pulp_builder.services.project_store import ProjectStore
from pulp_builder.services.status_bus import StatusBus
from pulp_builder.structures.registry import StoryStructureRegistry
from pulp_builder.ui.detail_panel import render_detail_panel
from pulp_builder.ui.import_dialog import show_import_dialog
from pulp_builder.ui.status_panel import render_status_panel
from pulp_builder.ui.structure_panel import render_structure_panel
from pulp_builder.ui.top_panel import render_top_panel


async def _extract_upload_payload(event: events.UploadEventArguments) -> tuple[str, bytes]:
    """Return uploaded filename and bytes across NiceGUI upload event variants."""

    if hasattr(event, "file") and event.file is not None:
        file_obj = event.file
        return file_obj.name, await file_obj.read()

    if hasattr(event, "name") and hasattr(event, "content"):
        content = event.content
        if hasattr(content, "seek"):
            content.seek(0)
        return event.name, content.read()

    return "", b""


@dataclass(slots=True)
class AppState:
    """Shared UI state container."""

    current_project: StoryProject | None = None
    selected_node_id: str | None = None
    status_bus: StatusBus = field(default_factory=StatusBus)

    def find_node(self, node_id: str | None) -> StoryNode | None:
        if not self.current_project or not node_id:
            return None
        for quarter in self.current_project.root_nodes:
            if quarter.node_id == node_id:
                return quarter
            for component in quarter.children:
                if component.node_id == node_id:
                    return component
        return None

    def selected_node(self) -> StoryNode | None:
        return self.find_node(self.selected_node_id)


class LayoutController:
    """Thin controller for panel refresh and basic callbacks."""

    def __init__(self, state: AppState) -> None:
        self.state = state
        self._app_config_store = AppConfigStore()
        self._app_config = self._app_config_store.load()
        self._exporter = StoryExporter()
        self._import_service = ImportService()
        self._llm_connection = LLMConnectionService()
        self._llm_rewriter = LLMRewriteService(self._llm_connection)
        self._llm_tag_applier = LLMTagApplierService(self._llm_connection)
        self._project_store = ProjectStore()
        self._registry = StoryStructureRegistry()
        self._templates_dir = Path(__file__).resolve().parents[3] / "templates"
        self._load_dialog = None
        self._load_warning_label = None
        self._load_status_label = None
        self._load_replace_confirm = None
        self._load_uploaded_name = ""
        self._load_uploaded_project: StoryProject | None = None
        self._load_has_unsaved = False
        self._ensure_llm_defaults()

    def on_select_node(self, raw_node_id: Any) -> None:
        node_id = self._normalize_node_id(raw_node_id)
        if not node_id:
            self.state.status_bus.warning("Could not resolve selected node.")
            render_status_panel.refresh(self.state)
            return

        self.state.selected_node_id = node_id
        if self.state.current_project:
            self.state.current_project.selected_node_id = node_id
        self.state.status_bus.info(f"Selected node: {node_id}")
        render_detail_panel.refresh(
            self.state,
            self.on_story_text_input,
            self.on_story_text_commit,
            self.on_llm_rewrite_selected,
            self.on_apply_tags_selected,
        )
        render_status_panel.refresh(self.state)

    def on_story_text_input(self, story_text: str) -> None:
        project = self.state.current_project
        node = self.state.selected_node()
        if not project or not node:
            return

        node.story_text = story_text
        if story_text.strip():
            node.is_placeholder = False
            node.missing_reason = ""
            node.completion_state = "drafted"
        else:
            node.completion_state = "missing"
            if node.required:
                node.is_placeholder = True
                node.was_placeholder = True
                if not node.missing_reason:
                    node.missing_reason = "No user text has been provided for this required component."
            else:
                node.is_placeholder = False

        was_dirty = project.dirty
        project.dirty = True
        project.updated_at = datetime.now(timezone.utc)

        # Keep typing responsive: avoid full panel refresh on each keystroke.
        if not was_dirty:
            render_top_panel.refresh(
                self.state,
                self._provider_options(),
                self._model_options(),
                self.on_llm_provider_change,
                self.on_llm_model_change,
                self.on_test_llm_connection,
                self.on_import,
                self.on_new_project,
                self.on_import_tagged_draft,
                self.on_save,
                self.on_load,
                self.on_export,
            )

    def on_story_text_commit(self) -> None:
        """Refresh dependent panels after editing focus leaves the textarea."""

        render_top_panel.refresh(
            self.state,
            self._provider_options(),
            self._model_options(),
            self.on_llm_provider_change,
            self.on_llm_model_change,
            self.on_test_llm_connection,
            self.on_import,
            self.on_new_project,
            self.on_import_tagged_draft,
            self.on_save,
            self.on_load,
            self.on_export,
        )
        render_structure_panel.refresh(self.state, self.on_select_node)
        render_status_panel.refresh(self.state)

    async def on_llm_rewrite_selected(self) -> None:
        project = self.state.current_project
        node = self.state.selected_node()
        if not project or not node:
            self.state.status_bus.warning("Select a story component to rewrite.")
            render_status_panel.refresh(self.state)
            return
        if not node.story_text.strip():
            self.state.status_bus.warning("Story text is empty; nothing to rewrite.")
            render_status_panel.refresh(self.state)
            return

        provider_id = self._current_llm_provider_id()
        model = self._current_llm_model()
        self.state.status_bus.info(f"LLM rewrite started ({provider_id}/{model})...")
        render_status_panel.refresh(self.state)

        request = RewriteRequest(
            story_form_id=project.story_form_id,
            story_form_label=project.story_form_label,
            component_title=node.title,
            component_description=node.description,
            guidance_prompt=node.guidance_prompt,
            source_text=node.story_text,
        )
        try:
            rewritten = await run.io_bound(
                self._llm_rewriter.rewrite,
                provider_id=provider_id,
                model=model,
                request=request,
            )
        except Exception as exc:
            self.state.status_bus.error(f"LLM rewrite failed: {exc}")
            render_status_panel.refresh(self.state)
            return

        if not rewritten.strip():
            self.state.status_bus.warning("LLM rewrite returned empty text.")
            render_status_panel.refresh(self.state)
            return

        self.on_story_text_input(rewritten)
        self.on_story_text_commit()
        render_detail_panel.refresh(
            self.state,
            self.on_story_text_input,
            self.on_story_text_commit,
            self.on_llm_rewrite_selected,
            self.on_apply_tags_selected,
        )
        self.state.status_bus.info(f"LLM rewrite applied to '{node.title}'.")
        render_status_panel.refresh(self.state)

    async def on_apply_tags_selected(self) -> None:
        project = self.state.current_project
        node = self.state.selected_node()
        if not project or not node:
            self.state.status_bus.warning("Select a story component before applying tags.")
            render_status_panel.refresh(self.state)
            return
        if not node.story_text.strip():
            self.state.status_bus.warning("Story text is empty; nothing to apply tags to.")
            render_status_panel.refresh(self.state)
            return

        provider_id = self._current_llm_provider_id()
        model = self._current_llm_model()
        self.state.status_bus.info(f"Applying inline tags with LLM ({provider_id}/{model})...")
        render_status_panel.refresh(self.state)

        request = TagApplyRequest(
            story_form_id=project.story_form_id,
            story_form_label=project.story_form_label,
            component_title=node.title,
            component_description=node.description,
            guidance_prompt=node.guidance_prompt,
            source_text=node.story_text,
        )
        try:
            updated_text, replacements = await run.io_bound(
                self._llm_tag_applier.apply_tags,
                provider_id=provider_id,
                model=model,
                request=request,
            )
        except Exception as exc:
            self.state.status_bus.error(f"Apply Tags failed: {exc}")
            render_status_panel.refresh(self.state)
            return

        if replacements == 0:
            self.state.status_bus.warning("No [tag] instructions found in story text.")
            render_status_panel.refresh(self.state)
            return

        self.on_story_text_input(updated_text)
        self.on_story_text_commit()
        render_detail_panel.refresh(
            self.state,
            self.on_story_text_input,
            self.on_story_text_commit,
            self.on_llm_rewrite_selected,
            self.on_apply_tags_selected,
        )
        self.state.status_bus.info(f"Applied {replacements} tag replacement(s).")
        render_status_panel.refresh(self.state)

    def on_import(self) -> None:
        options = {story_form["id"]: story_form["label"] for story_form in self._registry.list_forms()}
        has_unsaved = bool(self.state.current_project and self.state.current_project.dirty)

        provider_id = self._current_llm_provider_id()
        model = self._current_llm_model()
        provider_label = self._provider_options().get(provider_id, provider_id)

        show_import_dialog(
            story_form_options=options,
            has_unsaved_changes=has_unsaved,
            llm_provider_label=provider_label,
            llm_model=model,
            on_import=self._import_story_text,
        )

    def on_new_project(self) -> None:
        has_unsaved = bool(self.state.current_project and self.state.current_project.dirty)
        story_form_options = {story_form["id"]: story_form["label"] for story_form in self._registry.list_forms()}
        default_form = (
            self.state.current_project.story_form_id
            if self.state.current_project and self.state.current_project.story_form_id in story_form_options
            else next(iter(story_form_options.keys()))
        )

        with ui.dialog() as dialog, ui.card().classes("w-[36rem] max-w-full"):
            ui.label("New Project").classes("text-lg font-medium")
            ui.label(
                "Create a project from a built-in tagged template for the selected story style."
            ).classes("text-sm text-gray-700")

            if has_unsaved:
                ui.label("Warning: creating a new project will replace unsaved work.").classes(
                    "text-sm text-amber-700"
                )

            project_name_input = ui.input("Project Name", value="Untitled Project").classes("w-full")
            selected_form = ui.select(
                options=story_form_options,
                value=default_form,
                label="Story Form",
            ).classes("w-full")

            replace_confirm = ui.checkbox("I understand current unsaved work will be replaced.", value=False)
            if not has_unsaved:
                replace_confirm.visible = False

            async def handle_create_click() -> None:
                project_title = (project_name_input.value or "").strip()
                story_form_id = selected_form.value
                if not project_title:
                    ui.notify("Provide a project name.", type="warning")
                    return
                if not story_form_id:
                    ui.notify("Select a story form.", type="warning")
                    return
                if has_unsaved and not replace_confirm.value:
                    ui.notify("Confirm replacement of unsaved work.", type="warning")
                    return

                template_path = self._templates_dir / f"{story_form_id}.txt"
                if not template_path.exists():
                    self.state.status_bus.error(f"Template not found: {template_path}")
                    render_status_panel.refresh(self.state)
                    return

                self.state.status_bus.info(f"New project creation started from template '{template_path.name}'...")
                render_status_panel.refresh(self.state)
                try:
                    template_text = template_path.read_text(encoding="utf-8")
                    project = await run.io_bound(
                        self._import_service.import_story_text,
                        raw_story_text=template_text,
                        source_filename=template_path.name,
                        story_form_id=story_form_id,
                        project_title=project_title,
                        use_llm_first_pass=False,
                        llm_provider_id=self._current_llm_provider_id(),
                        llm_model=self._current_llm_model(),
                    )
                except Exception as exc:
                    self.state.status_bus.error(f"Could not create new project: {exc}")
                    render_status_panel.refresh(self.state)
                    return

                self.state.current_project = project
                self.state.selected_node_id = project.selected_node_id
                self._ensure_llm_defaults()
                self._save_app_llm_preferences(project)
                self.state.status_bus.info(
                    f"Created new project '{project.title}' from template {template_path.name}."
                )
                dialog.close()
                self.refresh_all()

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=dialog.close).props("outline")
                ui.button("Create Project", on_click=handle_create_click)

        dialog.open()

    async def _import_story_text(
        self,
        story_form_id: str,
        source_filename: str,
        raw_story_text: str,
        project_title: str,
        use_llm_first_pass: bool,
    ) -> None:
        self.state.status_bus.info("Import started. Parsing story input...")
        render_status_panel.refresh(self.state)

        try:
            project = await run.io_bound(
                self._import_service.import_story_text,
                raw_story_text=raw_story_text,
                source_filename=source_filename,
                story_form_id=story_form_id,
                project_title=project_title,
                use_llm_first_pass=use_llm_first_pass,
                llm_provider_id=self._current_llm_provider_id(),
                llm_model=self._current_llm_model(),
            )
        except Exception as exc:
            self.state.status_bus.error(f"Could not import story: {exc}")
            render_status_panel.refresh(self.state)
            return

        self.state.current_project = project
        self.state.selected_node_id = project.selected_node_id
        self._ensure_llm_defaults()
        self._save_app_llm_preferences(project)

        placeholders = sum(
            1
            for quarter in project.root_nodes
            for component in quarter.children
            if component.required and component.is_placeholder
        )
        self.state.status_bus.info(f"Imported {source_filename} using {project.story_form_label}.")
        if project.import_info.llm_first_pass_used:
            self.state.status_bus.info(
                f"LLM first-pass draft generated ({project.import_info.llm_first_pass_provider}/"
                f"{project.import_info.llm_first_pass_model})."
            )
            if project.import_info.llm_first_pass_draft_path:
                self.state.status_bus.info(
                    f"LLM first-pass draft saved: {project.import_info.llm_first_pass_draft_path}"
                )
            if project.import_info.llm_first_pass_warning:
                self.state.status_bus.warning(project.import_info.llm_first_pass_warning)
        if placeholders:
            self.state.status_bus.warning(
                f"Inserted {placeholders} required placeholders for missing story components."
            )

        self.refresh_all()

    def on_save(self) -> None:
        project = self.state.current_project
        if not project:
            self.state.status_bus.warning("No active project to save.")
            render_status_panel.refresh(self.state)
            return

        default_name = self._default_project_filename(project)

        with ui.dialog() as dialog, ui.card().classes("w-[36rem] max-w-full"):
            ui.label("Save Project").classes("text-lg font-medium")
            path_input = ui.input("Target JSON Path", value=f"projects/{default_name}.json").classes("w-full")

            def handle_save_click() -> None:
                target_path = (path_input.value or "").strip()
                if not target_path:
                    ui.notify("Provide a target path.", type="warning")
                    return
                try:
                    saved_path = self._project_store.save(project, target_path)
                except Exception as exc:
                    self.state.status_bus.error(f"Failed to save project: {exc}")
                    render_status_panel.refresh(self.state)
                    return

                self.state.status_bus.info(f"Saved project to {saved_path}.")
                self._save_app_llm_preferences(project)
                dialog.close()
                self.refresh_all()

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=dialog.close).props("outline")
                ui.button("Save", on_click=handle_save_click)

        dialog.open()

    def on_import_tagged_draft(self) -> None:
        has_unsaved = bool(self.state.current_project and self.state.current_project.dirty)
        story_form_options = {story_form["id"]: story_form["label"] for story_form in self._registry.list_forms()}
        default_form = (
            self.state.current_project.story_form_id
            if self.state.current_project and self.state.current_project.story_form_id in story_form_options
            else next(iter(story_form_options.keys()))
        )
        uploaded_name = ""
        uploaded_text = ""
        uploaded_size = 0

        with ui.dialog() as dialog, ui.card().classes("w-[40rem] max-w-full"):
            ui.label("Import Tagged Draft").classes("text-lg font-medium")
            ui.label(
                "Expected tags: '## Quarter', '- Component: ...', and optional '- Story Text: ...'."
            ).classes("text-sm text-gray-700")

            if has_unsaved:
                ui.label("Warning: importing will replace the current unsaved project.").classes("text-sm text-amber-700")

            selected_form = ui.select(
                options=story_form_options,
                value=default_form,
                label="Story Form",
            ).classes("w-full")

            upload_status = ui.label("No .txt file selected.").classes("text-sm text-gray-700")

            async def handle_upload(event: events.UploadEventArguments) -> None:
                nonlocal uploaded_name, uploaded_text, uploaded_size
                uploaded_name, raw_bytes = await _extract_upload_payload(event)

                if not uploaded_name.lower().endswith(".txt"):
                    uploaded_name = ""
                    uploaded_text = ""
                    uploaded_size = 0
                    upload_status.set_text("Please upload a .txt file.")
                    return

                uploaded_size = len(raw_bytes)
                if uploaded_size == 0:
                    uploaded_text = ""
                    upload_status.set_text(f"Loaded: {uploaded_name} (0 bytes)")
                    return

                try:
                    uploaded_text = raw_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    try:
                        uploaded_text = raw_bytes.decode("latin-1")
                    except UnicodeDecodeError:
                        uploaded_text = raw_bytes.decode("utf-8", errors="replace")
                upload_status.set_text(f"Loaded: {uploaded_name} ({uploaded_size} bytes)")

            ui.upload(
                on_upload=handle_upload,
                auto_upload=True,
                label="Browse Tagged Draft (.txt)",
            ).props("accept=.txt")

            replace_confirm = ui.checkbox("I understand current unsaved work will be replaced.", value=False)
            if not has_unsaved:
                replace_confirm.visible = False

            async def handle_import_click() -> None:
                story_form_id = selected_form.value
                if not story_form_id:
                    ui.notify("Select a story form.", type="warning")
                    return
                if not uploaded_name or uploaded_size == 0 or not uploaded_text.strip():
                    ui.notify("Upload a non-empty .txt file.", type="warning")
                    return
                if has_unsaved and not replace_confirm.value:
                    ui.notify("Confirm replacement of unsaved work.", type="warning")
                    return

                self.state.status_bus.info("Tagged draft import started...")
                render_status_panel.refresh(self.state)

                try:
                    project = await run.io_bound(
                        self._import_service.import_story_text,
                        raw_story_text=uploaded_text,
                        source_filename=uploaded_name,
                        story_form_id=story_form_id,
                        project_title=(
                            self.state.current_project.title if self.state.current_project else None
                        ),
                        use_llm_first_pass=False,
                        llm_provider_id=self._current_llm_provider_id(),
                        llm_model=self._current_llm_model(),
                    )
                except Exception as exc:
                    self.state.status_bus.error(f"Could not import tagged draft: {exc}")
                    render_status_panel.refresh(self.state)
                    return

                self.state.current_project = project
                self.state.selected_node_id = project.selected_node_id
                self._ensure_llm_defaults()
                self._save_app_llm_preferences(project)
                self.state.status_bus.info(f"Imported tagged draft {uploaded_name}.")
                dialog.close()
                self.refresh_all()

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=dialog.close).props("outline")
                ui.button("Import Tagged Draft", on_click=handle_import_click)

        dialog.open()

    def on_load(self) -> None:
        self._ensure_load_dialog()
        self._load_uploaded_name = ""
        self._load_uploaded_project = None
        self._load_has_unsaved = bool(self.state.current_project and self.state.current_project.dirty)

        self._load_status_label.set_text("No project file selected.")
        self._load_warning_label.visible = self._load_has_unsaved
        self._load_replace_confirm.visible = self._load_has_unsaved
        self._load_replace_confirm.value = False
        self._load_dialog.open()

    def on_export(self) -> None:
        project = self.state.current_project
        if not project:
            self.state.status_bus.warning("No active project to export.")
            render_status_panel.refresh(self.state)
            return

        default_name = self._default_project_filename(project)

        with ui.dialog() as dialog, ui.card().classes("w-[36rem] max-w-full"):
            ui.label("Export Story").classes("text-lg font-medium")
            path_input = ui.input("Target Text Path", value=f"exports/{default_name}.txt").classes("w-full")

            def handle_export_click() -> None:
                target_path = (path_input.value or "").strip()
                if not target_path:
                    ui.notify("Provide a target path.", type="warning")
                    return
                try:
                    output_path = self._exporter.export_to_file(project, target_path)
                except Exception as exc:
                    self.state.status_bus.error(f"Failed to export story: {exc}")
                    render_status_panel.refresh(self.state)
                    return

                self.state.status_bus.info(f"Exported story to {output_path}.")
                dialog.close()
                render_status_panel.refresh(self.state)

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=dialog.close).props("outline")
                ui.button("Export", on_click=handle_export_click)

        dialog.open()

    def refresh_all(self) -> None:
        render_top_panel.refresh(
            self.state,
            self._provider_options(),
            self._model_options(),
            self.on_llm_provider_change,
            self.on_llm_model_change,
            self.on_test_llm_connection,
            self.on_import,
            self.on_new_project,
            self.on_import_tagged_draft,
            self.on_save,
            self.on_load,
            self.on_export,
        )
        render_structure_panel.refresh(self.state, self.on_select_node)
        render_detail_panel.refresh(
            self.state,
            self.on_story_text_input,
            self.on_story_text_commit,
            self.on_llm_rewrite_selected,
            self.on_apply_tags_selected,
        )
        render_status_panel.refresh(self.state)

    @staticmethod
    def _default_project_filename(project: StoryProject) -> str:
        name = re.sub(r"[^A-Za-z0-9]+", "_", project.title.strip()).strip("_").lower()
        return name or project.project_id

    @staticmethod
    def _normalize_node_id(raw_value: Any) -> str | None:
        if isinstance(raw_value, str):
            return raw_value
        if isinstance(raw_value, dict):
            candidate = raw_value.get("id")
            return candidate if isinstance(candidate, str) else None
        if isinstance(raw_value, (list, tuple, set)):
            for item in raw_value:
                normalized = LayoutController._normalize_node_id(item)
                if normalized:
                    return normalized
        return None

    def on_llm_provider_change(self, provider_id: str) -> None:
        project = self.state.current_project
        if not project or not provider_id:
            return

        project.llm_provider = provider_id
        suggested_models = self._llm_connection.model_options_for_provider(provider_id)
        if not project.llm_model or (suggested_models and project.llm_model not in suggested_models):
            project.llm_model = self._llm_connection.default_model_for_provider(provider_id)
        project.dirty = True
        project.updated_at = datetime.now(timezone.utc)
        self.state.status_bus.info(f"LLM provider set to {provider_id}.")

        render_top_panel.refresh(
            self.state,
            self._provider_options(),
            self._model_options(),
            self.on_llm_provider_change,
            self.on_llm_model_change,
            self.on_test_llm_connection,
            self.on_import,
            self.on_new_project,
            self.on_import_tagged_draft,
            self.on_save,
            self.on_load,
            self.on_export,
        )
        render_status_panel.refresh(self.state)

    def on_llm_model_change(self, model: str) -> None:
        project = self.state.current_project
        if not project or not model:
            return

        project.llm_model = model
        project.dirty = True
        project.updated_at = datetime.now(timezone.utc)
        self.state.status_bus.info(f"LLM model set to {model}.")

        render_top_panel.refresh(
            self.state,
            self._provider_options(),
            self._model_options(),
            self.on_llm_provider_change,
            self.on_llm_model_change,
            self.on_test_llm_connection,
            self.on_import,
            self.on_new_project,
            self.on_import_tagged_draft,
            self.on_save,
            self.on_load,
            self.on_export,
        )
        render_status_panel.refresh(self.state)

    def on_test_llm_connection(self) -> None:
        project = self.state.current_project
        if not project:
            self.state.status_bus.warning("No active project to test LLM connection.")
            render_status_panel.refresh(self.state)
            return

        provider_id = project.llm_provider or self._llm_connection.default_provider_id()
        model = project.llm_model or self._llm_connection.default_model_for_provider(provider_id)
        result = self._llm_connection.test_connection(provider_id=provider_id, model=model)

        if result.success:
            preview = f" Response: {result.response_preview}" if result.response_preview else ""
            self.state.status_bus.info(
                f"LLM test succeeded ({result.provider_id}/{result.model}).{preview}"
            )
        else:
            self.state.status_bus.error(
                f"LLM test failed ({result.provider_id}/{result.model}): {result.message}"
            )
        render_status_panel.refresh(self.state)

    def _ensure_llm_defaults(self) -> None:
        project = self.state.current_project
        if not project:
            return

        if not project.llm_provider:
            project.llm_provider = self._app_config.llm_provider or self._llm_connection.default_provider_id()
        if not project.llm_model:
            if self._app_config.llm_model and project.llm_provider == (self._app_config.llm_provider or ""):
                project.llm_model = self._app_config.llm_model
            else:
                project.llm_model = self._llm_connection.default_model_for_provider(project.llm_provider)


    def _current_llm_provider_id(self) -> str:
        project = self.state.current_project
        if project and project.llm_provider:
            return project.llm_provider
        return self._app_config.llm_provider or self._llm_connection.default_provider_id()

    def _current_llm_model(self) -> str:
        project = self.state.current_project
        provider_id = self._current_llm_provider_id()
        if project and project.llm_model:
            return project.llm_model
        if self._app_config.llm_model and provider_id == (self._app_config.llm_provider or ""):
            return self._app_config.llm_model
        return self._llm_connection.default_model_for_provider(provider_id)

    def _provider_options(self) -> dict[str, str]:
        return self._llm_connection.list_provider_options()

    def _model_options(self) -> list[str]:
        project = self.state.current_project
        provider_id = project.llm_provider if project and project.llm_provider else self._llm_connection.default_provider_id()
        return self._llm_connection.model_options_for_provider(provider_id)

    def _save_app_llm_preferences(self, project: StoryProject) -> None:
        if not project.llm_provider or not project.llm_model:
            return
        self._app_config = AppConfig(llm_provider=project.llm_provider, llm_model=project.llm_model)
        self._app_config_store.save(self._app_config)

    def _ensure_load_dialog(self) -> None:
        if self._load_dialog is not None:
            return

        with ui.dialog() as dialog, ui.card().classes("w-[40rem] max-w-full"):
            ui.label("Load Project").classes("text-lg font-medium")
            self._load_warning_label = ui.label("Warning: loading will replace current unsaved project.").classes(
                "text-sm text-amber-700"
            )
            self._load_warning_label.visible = False
            self._load_status_label = ui.label("No project file selected.").classes("text-sm text-gray-700")

            ui.upload(on_upload=self._handle_load_upload, auto_upload=True, label="Browse Project JSON").props(
                "accept=.json"
            )
            self._load_replace_confirm = ui.checkbox("I understand current unsaved work will be replaced.", value=False)
            self._load_replace_confirm.visible = False

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=dialog.close).props("outline")
                ui.button("Load", on_click=self._handle_load_confirm)

        self._load_dialog = dialog

    async def _handle_load_upload(self, event: events.UploadEventArguments) -> None:
        try:
            if hasattr(event, "file") and event.file is not None:
                self._load_uploaded_name = event.file.name
                payload = (await event.file.read()).decode("utf-8")
            elif hasattr(event, "name") and hasattr(event, "content"):
                self._load_uploaded_name = event.name
                if hasattr(event.content, "seek"):
                    event.content.seek(0)
                payload = event.content.read().decode("utf-8")
            else:
                raise ValueError("unsupported upload event payload")
            self._load_uploaded_project = self._project_store.load_json(payload)
            self._load_status_label.set_text(f"Loaded JSON: {self._load_uploaded_name}")
        except Exception as exc:
            self._load_uploaded_project = None
            self._load_status_label.set_text(f"Invalid project file: {exc}")

    def _handle_load_confirm(self) -> None:
        if self._load_has_unsaved and not self._load_replace_confirm.value:
            ui.notify("Confirm replacement of unsaved work.", type="warning")
            return
        if self._load_uploaded_project is None:
            ui.notify("Upload a valid project JSON file.", type="warning")
            return

        self.state.current_project = self._load_uploaded_project
        self.state.selected_node_id = self._load_uploaded_project.selected_node_id
        self._ensure_llm_defaults()
        self.state.status_bus.info(f"Loaded project from {self._load_uploaded_name}.")
        self._load_dialog.close()
        self.refresh_all()


def build_layout(state: AppState) -> None:
    """Render the four-panel app shell."""

    controller = LayoutController(state)
    ui.add_css(
        """
        body {
            background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
        }
        .q-card {
            border-radius: 10px;
        }
        """
    )

    with ui.column().classes("w-full h-screen p-2 gap-2"):
        render_top_panel(
            state,
            controller._provider_options(),
            controller._model_options(),
            controller.on_llm_provider_change,
            controller.on_llm_model_change,
            controller.on_test_llm_connection,
            controller.on_import,
            controller.on_new_project,
            controller.on_import_tagged_draft,
            controller.on_save,
            controller.on_load,
            controller.on_export,
        )

        with ui.row().classes("w-full flex-1 min-h-0 gap-2 no-wrap"):
            with ui.column().classes("h-full min-h-0").style("flex: 0 0 30%; min-width: 260px;"):
                render_structure_panel(state, controller.on_select_node)
            with ui.column().classes("h-full min-h-0").style("flex: 1 1 auto; min-width: 0;"):
                render_detail_panel(
                    state,
                    controller.on_story_text_input,
                    controller.on_story_text_commit,
                    controller.on_llm_rewrite_selected,
                    controller.on_apply_tags_selected,
                )

        render_status_panel(state)
