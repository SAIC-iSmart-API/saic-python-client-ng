"""Heated steering wheel control (#33).

Checks the request body: request type 8, parameter 24 = 1 (on) or 0 (off),
then the end-of-parameters marker (255).
"""

from __future__ import annotations

import base64
from typing import Any
import unittest

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.api.vehicle import RvcParamsId, RvcReqType
from saic_ismart_client_ng.crypto_utils import sha256_hex_digest
from saic_ismart_client_ng.model import SaicApiConfiguration

VIN = "OFFLINE0000000000"


class TestHeatedSteeringWheel(unittest.IsolatedAsyncioTestCase):
    async def _sent(self, *, enable: bool) -> Any:
        api = SaicApi(SaicApiConfiguration(username="user", password="pass"))  # noqa: S106
        captured: dict[str, Any] = {}

        async def capture(body: Any, vin: str) -> None:
            captured["body"] = body
            captured["vin"] = vin

        api.send_vehicle_control_command = capture  # type: ignore[method-assign,assignment]
        await api.control_heated_steering_wheel(VIN, enable=enable)
        await api.close()
        assert captured["vin"] == VIN
        return captured["body"]

    async def test_on(self) -> None:
        body = await self._sent(enable=True)
        assert body.rvcReqType == RvcReqType.HEATED_STEERING_WHEEL.value
        assert body.rvcReqType == "8"
        params = [(p.paramId, base64.b64decode(p.paramValue)) for p in body.rvcParams]
        assert params == [
            (RvcParamsId.HEATED_STEERING_WHEEL.value, b"\x01"),
            (255, b"\x00\x00\x00\x00"),
        ]
        assert params[0][0] == 24
        assert body.vin == sha256_hex_digest(VIN)

    async def test_off(self) -> None:
        body = await self._sent(enable=False)
        params = [(p.paramId, base64.b64decode(p.paramValue)) for p in body.rvcParams]
        assert params == [(24, b"\x00"), (255, b"\x00\x00\x00\x00")]
