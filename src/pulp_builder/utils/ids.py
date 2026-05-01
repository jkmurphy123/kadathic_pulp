"""ID utility helpers."""

from __future__ import annotations

from datetime import datetime


def make_project_id(now: datetime) -> str:
    """Create a readable project ID based on UTC timestamp."""

    return now.strftime("project-%Y%m%d-%H%M%S")
