"""Window ventilation: close, ventilate or fully open all door windows (#36).

Checks the request body against what the iSmart app sends (decrypted MG S6 EV
traffic): request type 3, the sunroof parameter 0 (left alone), all four door
windows 1, then the action (0 close, 1 ventilate, 2 fully open), with no
end-of-parameters marker.
"""

from __future__ import annotations

import base64
from typing import Any
import unittest

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.api.vehicle import RvcReqType
from saic_ismart_client_ng.api.vehicle.windows import DoorWindowsAction
from saic_ismart_client_ng.crypto_utils import sha256_hex_digest
from saic_ismart_client_ng.model import SaicApiConfiguration

VIN = "OFFLINE0000000000"


class TestDoorWindows(unittest.IsolatedAsyncioTestCase):
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

    async def test_each_action(self) -> None:
        for action, value in (
            (DoorWindowsAction.CLOSE, 0),
            (DoorWindowsAction.VENTILATE, 1),
            (DoorWindowsAction.OPEN, 2),
        ):
            with self.subTest(action=action):
                body = await self._sent("control_door_windows", action=action)
                assert body.rvcReqType == RvcReqType.WINDOWS.value == "3"
                assert self._params(body) == [
                    (8, b"\x00"),  # sunroof left alone
                    (9, b"\x01"),
                    (10, b"\x01"),
                    (11, b"\x01"),
                    (12, b"\x01"),
                    (13, bytes([value])),
                ]
                assert body.vin == sha256_hex_digest(VIN)

    async def test_control_windows_unchanged(self) -> None:
        # The existing helper keeps its open value (3) for other models.
        body = await self._sent("control_windows", should_open=True, windows=[])
        assert self._params(body)[-1] == (13, b"\x03")
