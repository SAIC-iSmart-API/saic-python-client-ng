from abc import ABC
from typing import Optional


class SaicApiListener(ABC):
    async def on_request(self, path: str, body: Optional[str] = None, headers: Optional[dict] = None):
        pass

    async def on_response(self, path: str, body: Optional[str] = None, headers: Optional[dict] = None):
        pass
