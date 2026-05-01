"""Status message model."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class StatusMessage(BaseModel):
    """Message shown in the UI status panel."""

    message_id: str
    created_at: datetime
    level: Literal["info", "warning", "error"]
    text: str
