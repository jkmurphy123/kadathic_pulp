"""Status message bus for UI status panel updates."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone

from pulp_builder.models.status_message import StatusMessage


class StatusBus:
    """Maintain a small rolling list of status messages."""

    def __init__(self, max_messages: int = 12) -> None:
        self._messages: deque[StatusMessage] = deque(maxlen=max_messages)

    def info(self, text: str) -> StatusMessage:
        return self._add("info", text)

    def warning(self, text: str) -> StatusMessage:
        return self._add("warning", text)

    def error(self, text: str) -> StatusMessage:
        return self._add("error", text)

    def recent(self) -> list[StatusMessage]:
        return list(self._messages)

    def _add(self, level: str, text: str) -> StatusMessage:
        now = datetime.now(timezone.utc)
        message = StatusMessage(
            message_id=f"status-{int(now.timestamp() * 1000)}-{len(self._messages)}",
            created_at=now,
            level=level,
            text=text,
        )
        self._messages.append(message)
        return message
