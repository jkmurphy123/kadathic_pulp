"""Import dialog for story form + .txt input."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import inspect

from nicegui import events, ui


async def _extract_upload_payload(event: events.UploadEventArguments) -> tuple[str, bytes]:
    """Return uploaded filename and bytes across NiceGUI upload event variants."""

    if hasattr(event, "file") and event.file is not None:
        file_obj = event.file
        return file_obj.name, await file_obj.read()

    # Backward compatibility for older event variants.
    if hasattr(event, "name") and hasattr(event, "content"):
        content = event.content
        if hasattr(content, "seek"):
            content.seek(0)
        return event.name, content.read()

    return "", b""


def show_import_dialog(
    story_form_options: dict[str, str],
    has_unsaved_changes: bool,
    llm_provider_label: str,
    llm_model: str,
    on_import: Callable[[str, str, str, bool], Awaitable[None] | None],
) -> None:
    """Open the import dialog and invoke callback on successful validation."""

    if not story_form_options:
        ui.notify("No story forms available.", type="negative")
        return

    uploaded_name = ""
    uploaded_text = ""
    uploaded_size = 0

    with ui.dialog() as dialog, ui.card().classes("w-[40rem] max-w-full"):
        ui.label("Import Story").classes("text-lg font-medium")

        if has_unsaved_changes:
            ui.label("Warning: importing will replace the current unsaved project.").classes("text-sm text-amber-700")

        selected_form = ui.select(
            options=story_form_options,
            value=next(iter(story_form_options.keys())),
            label="Story Form",
        ).classes("w-full")

        use_llm_first_pass = ui.checkbox(
            f"Use LLM first pass ({llm_provider_label} / {llm_model})",
            value=False,
        )

        upload_status = ui.label("No .txt file selected.").classes("text-sm text-gray-700")

        async def handle_upload(event: events.UploadEventArguments) -> None:
            nonlocal uploaded_name, uploaded_text, uploaded_size
            uploaded_name, raw_bytes = await _extract_upload_payload(event)

            if not uploaded_name.lower().endswith(".txt"):
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
            label="Browse .txt",
        ).props("accept=.txt")

        replace_confirm = ui.checkbox("I understand current unsaved work will be replaced.", value=False)
        if not has_unsaved_changes:
            replace_confirm.visible = False

        async def handle_import_click() -> None:
            story_form_id = selected_form.value
            if not story_form_id:
                ui.notify("Select a story form.", type="warning")
                return

            if not uploaded_name or uploaded_size == 0 or not uploaded_text.strip():
                ui.notify("Upload a non-empty .txt file.", type="warning")
                return

            if has_unsaved_changes and not replace_confirm.value:
                ui.notify("Confirm replacement of unsaved work.", type="warning")
                return

            result = on_import(story_form_id, uploaded_name, uploaded_text, bool(use_llm_first_pass.value))
            if inspect.isawaitable(result):
                await result
            dialog.close()

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("outline")
            ui.button("Import", on_click=handle_import_click)

    dialog.open()
