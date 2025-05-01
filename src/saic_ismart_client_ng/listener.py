from __future__ import annotations


class SaicApiListener:
    async def on_request(
        self, path: str, body: str | None = None, headers: dict[str, str] | None = None
    ) -> None:
        pass

    async def on_response(
        self, path: str, body: str | None = None, headers: dict[str, str] | None = None
    ) -> None:
        pass
