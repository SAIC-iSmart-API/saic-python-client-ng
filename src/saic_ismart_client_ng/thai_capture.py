from __future__ import annotations

import argparse
import base64
import json
import plistlib
import sys
from collections.abc import Sequence
from pathlib import Path
from urllib.parse import urlsplit

def dump_capture_to_text(path: Path) -> Path:
    """Write a readable text report containing every item in a Proxygen capture."""
    with path.open("rb") as capture_file:
        capture = plistlib.load(capture_file)

    if not isinstance(capture, dict) or not isinstance(capture.get("history"), dict):
        raise ValueError("Invalid Proxygen capture: missing request history.")
    history = capture["history"]
    entries = history.get("entries")
    if not isinstance(entries, list):
        raise ValueError("Invalid Proxygen capture: missing request entries.")

    lines = ["Capture metadata:"]
    metadata = {key: value for key, value in capture.items() if key != "history"}
    lines.extend(_format_value(metadata, 2))
    history_metadata = {key: value for key, value in history.items() if key != "entries"}
    if history_metadata:
        lines.extend(["", "History metadata:"])
        lines.extend(_format_value(history_metadata, 2))

    for index, entry in enumerate(entries, start=1):
        lines.extend(["", f"Entry {index}:"])
        lines.extend(_format_value(entry, 2))

    output_path = path.with_suffix(".txt")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def main(argv: Sequence[str] | None = None) -> None:
    """Dump a Proxygen plist capture to a companion text file."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("capture", type=Path, help="path to the Proxygen plist")
    args = parser.parse_args(argv)
    output_path = dump_capture_to_text(args.capture)
    sys.stdout.write(f"Wrote text dump to {output_path}\n")


def _format_value(value: object, indent: int = 0, key: str | None = None) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        if not value:
            return [f"{prefix}{{}}"]
        lines: list[str] = []
        for item_key, item_value in value.items():
            item_lines = _format_value(
                item_value, indent + 2, str(item_key).lower()
            )
            if not isinstance(item_value, (dict, list)) and len(item_lines) == 1:
                lines.append(f"{prefix}{item_key}: {item_lines[0].strip()}")
                continue
            lines.append(f"{prefix}{item_key}:")
            lines.extend(item_lines)
        return lines
    if isinstance(value, list):
        if not value:
            return [f"{prefix}[]"]
        lines = []
        for item in value:
            formatted = _format_value(item, indent + 2, key)
            lines.append(f"{prefix}- {formatted[0].lstrip()}")
            lines.extend(formatted[1:])
        return lines
    if isinstance(value, bytes):
        try:
            value = value.decode("utf-8")
        except UnicodeDecodeError:
            value = f"[binary data, base64] {base64.b64encode(value).decode('ascii')}"
        else:
            if key == "body":
                try:
                    value = json.dumps(
                        json.loads(value), ensure_ascii=False, indent=2
                    )
                except json.JSONDecodeError:
                    pass
    elif isinstance(value, str) and key == "body":
        try:
            value = json.dumps(json.loads(value), ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            pass

    rendered = str(value)
    if "\n" in rendered:
        return [f"{prefix}{line}" for line in rendered.splitlines()]
    return [f"{prefix}{rendered}"]


def login_authorization_from_capture(path: Path) -> str:
    """Read the unique Thai login authorization from a Proxygen plist capture."""
    with path.open("rb") as capture_file:
        capture = plistlib.load(capture_file)

    if not isinstance(capture, dict) or not isinstance(capture.get("history"), dict):
        raise ValueError("Invalid Proxygen capture: missing request history.")
    entries = capture["history"].get("entries")
    if not isinstance(entries, list):
        raise ValueError("Invalid Proxygen capture: missing request entries.")

    authorizations: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(
            entry.get("transaction"), dict
        ):
            continue
        transaction = entry["transaction"]
        request = transaction.get("request")
        target = transaction.get("target")
        if not isinstance(request, dict) or not isinstance(target, dict):
            continue
        uri = request.get("uri")
        if not isinstance(uri, str):
            continue
        url = urlsplit(uri)
        if (
            target.get("host") != "gateway-mg-th.soimt.com"
            or url.hostname not in (None, "gateway-mg-th.soimt.com")
            or url.path != "/api.app/v1/oauth/token"
            or request.get("method") != "POST"
        ):
            continue
        headers = request.get("headers")
        if not isinstance(headers, list):
            continue
        for header in headers:
            if (
                isinstance(header, dict)
                and isinstance(header.get("name"), str)
                and header["name"].lower() == "authorization"
                and isinstance(header.get("value"), str)
            ):
                authorizations.add(header["value"])

    if not authorizations:
        raise ValueError("No Thai login authorization found in the capture.")
    if len(authorizations) != 1:
        raise ValueError("Multiple Thai login authorizations found in the capture.")
    return authorizations.pop()


if __name__ == "__main__":
    main()
