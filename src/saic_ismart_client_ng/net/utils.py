from __future__ import annotations


def normalize_content_type(original_content_type: str | None) -> str:
    normalized = "application/json"
    if original_content_type:
        if "multipart" in original_content_type:
            normalized = "multipart/form-data"
        elif "x-www-form-urlencoded" in original_content_type:
            normalized = "application/x-www-form-urlencoded"
    return normalized
