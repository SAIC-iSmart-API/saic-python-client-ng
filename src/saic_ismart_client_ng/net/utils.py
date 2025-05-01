from __future__ import annotations

from typing import Optional


def normalize_content_type(original_content_type: Optional[str]) -> str:
    normalized = "application/json"
    if original_content_type:
        if "multipart" in original_content_type:
            normalized = "multipart/form-data"
        elif "x-www-form-urlencoded" in original_content_type:
            normalized = "application/x-www-form-urlencoded"
    return normalized
