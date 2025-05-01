from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserTimezoneResp:
    timezone: str | None = None
