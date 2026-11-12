"""Power tailgate: open and close (control_tailgate).

Checks the request body against what the iSmart app sends (decrypted MG S6 EV
traffic, UK): request type 9 with a single parameter, 31 = 1 to open or 2 to
close, and no end-of-parameters marker. open_tailgate is unchanged.
"""

from __future__ import annotations

import base64
from typing import Any
import unittest

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.api.vehicle import RvcReqType
from saic_ismart_client_ng.api.vehicle.locks import TailgateAction
from saic_ismart_client_ng.crypto_utils import sha256_hex_digest
from saic_ismart_client_ng.model import SaicApiConfiguration

VIN = "OFFLINE0000000000"


class TestPowerTailgate(unittest.IsolatedAsyncioTestCase):
    async def _sent(self, call: str, **kwargs: Any) -> Any:
        api = SaicApi(SaicApiConfiguration(username="user", password="pass"))  # noqa: S106
        captured: dict[str, Any] = {}

        async def capture(body: Any, vin: str) -> None:
            captured["body"] = body
            captured["vin"] = vin

        api.send_vehicle_control_command = capture  # type: ignore[method-assign,assignment]
        await getattr(api, call)(VIN, **kwargs)
        await api.close()
        return captured["body"]

    @staticmethod
    def _params(body: Any) -> list[tuple[int, bytes]]:
        return [(p.paramId, base64.b64decode(p.paramValue)) for p in body.rvcParams]

    async def test_open_and_close(self) -> None:
        for action, value in ((TailgateAction.OPEN, 1), (TailgateAction.CLOSE, 2)):
            with self.subTest(action=action):
                body = await self._sent("control_tailgate", action=action)
                assert body.rvcReqType == RvcReqType.TAILGATE.value == "9"
                assert self._params(body) == [(31, bytes([value]))]
                assert body.vin == sha256_hex_digest(VIN)

    async def test_open_tailgate_unchanged(self) -> None:
        body = await self._sent("open_tailgate")
        assert body.rvcReqType == RvcReqType.OPEN_LOCKS.value == "2"
        assert self._params(body) == [
            (4, b"\x00"),
            (5, b"\x00"),
            (6, b"\x00"),
            (7, b"\x02"),
            (255, b"\x00\x00\x00\x00"),
        ]
