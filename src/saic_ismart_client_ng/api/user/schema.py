from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class UserTimezoneResp:
    timezone: Optional[str] = None
