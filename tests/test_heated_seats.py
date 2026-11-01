"""Per-seat heated seat control, front and rear (#34).

Checks the request body: request type 5, a single parameter for the chosen seat
(17 front left, 18 front right, 25 rear left, 26 rear right), then the
end-of-parameters marker (255). Rear seats are on/off only; the app sends 3 for
"on".
"""

from __future__ import annotations

import base64
from typing import Any
import unittest

import pytest

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.api.vehicle import RvcReqType
from saic_ismart_client_ng.api.vehicle.climate import (
    REAR_HEATED_SEAT_ON_LEVEL,
    HeatedSeat,
)
from saic_ismart_client_ng.crypto_utils import sha256_hex_digest
from saic_ismart_client_ng.model import SaicApiConfiguration

VIN = "OFFLINE0000000000"
SEAT_PARAMS = {
    HeatedSeat.FRONT_LEFT: 17,
    HeatedSeat.FRONT_RIGHT: 18,
    HeatedSeat.REAR_LEFT: 25,
    HeatedSeat.REAR_RIGHT: 26,
}


class TestHeatedSeat(unittest.IsolatedAsyncioTestCase):
    async def _sent(self, *, seat: HeatedSeat, level: int) -> Any:
        api = SaicApi(SaicApiConfiguration(username="user", password="pass"))  # noqa: S106
        captured: dict[str, Any] = {}

        async def capture(body: Any, vin: str) -> None:
            captured["body"] = body
            captured["vin"] = vin

        api.send_vehicle_control_command = capture  # type: ignore[method-assign,assignment]
        try:
            await api.control_heated_seat(VIN, seat=seat, level=level)
        finally:
            await api.close()
        return captured.get("body")

    async def test_one_seat_per_command(self) -> None:
        for seat, param_id in SEAT_PARAMS.items():
            for level in range(4):
                with self.subTest(seat=seat, level=level):
                    body = await self._sent(seat=seat, level=level)
                    assert body.rvcReqType == RvcReqType.HEATED_SEATS.value == "5"
                    params = [
                        (p.paramId, base64.b64decode(p.paramValue))
                        for p in body.rvcParams
                    ]
                    assert params == [
                        (param_id, bytes([level])),
                        (255, b"\x00\x00\x00\x00"),
                    ]
                    assert body.vin == sha256_hex_digest(VIN)

    async def test_rear_seat_on_is_the_apps_level(self) -> None:
        assert REAR_HEATED_SEAT_ON_LEVEL == 3
        body = await self._sent(
            seat=HeatedSeat.REAR_LEFT, level=REAR_HEATED_SEAT_ON_LEVEL
        )
        params = [(p.paramId, base64.b64decode(p.paramValue)) for p in body.rvcParams]
        assert params == [(25, b"\x03"), (255, b"\x00\x00\x00\x00")]

    async def test_out_of_range_levels_are_rejected(self) -> None:
        for level in (-1, 4):
            with self.subTest(level=level), pytest.raises(ValueError, match="0-3"):
                await self._sent(seat=HeatedSeat.FRONT_LEFT, level=level)
