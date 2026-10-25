"""Per-seat ventilated seat control and status (#35).

Checks the request body: request type 22, a single parameter for the chosen
seat (27 front left, 28 front right, 29 rear left, 30 rear right), then the
end-of-parameters marker (255). Seats with a single level take 3 for "on".

This follows the iSmart app's logic. It has not been checked on a car.
"""

from __future__ import annotations

import base64
import json
from typing import Any
import unittest

import dacite
import pytest

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.api.vehicle import RvcReqType, VehicleStatusResp
from saic_ismart_client_ng.api.vehicle.climate import (
    ONE_LEVEL_VENTILATED_SEAT_ON_LEVEL,
    VentilatedSeat,
)
from saic_ismart_client_ng.crypto_utils import sha256_hex_digest
from saic_ismart_client_ng.model import SaicApiConfiguration

VIN = "OFFLINE0000000000"
SEAT_PARAMS = {
    VentilatedSeat.FRONT_LEFT: 27,
    VentilatedSeat.FRONT_RIGHT: 28,
    VentilatedSeat.REAR_LEFT: 29,
    VentilatedSeat.REAR_RIGHT: 30,
}


class TestVentilatedSeat(unittest.IsolatedAsyncioTestCase):
    async def _sent(self, *, seat: VentilatedSeat, level: int) -> Any:
        api = SaicApi(SaicApiConfiguration(username="user", password="pass"))  # noqa: S106
        captured: dict[str, Any] = {}

        async def capture(body: Any, _vin: str) -> None:
            captured["body"] = body

        api.send_vehicle_control_command = capture  # type: ignore[method-assign,assignment]
        try:
            await api.control_ventilated_seat(VIN, seat=seat, level=level)
        finally:
            await api.close()
        return captured.get("body")

    async def test_one_seat_per_command(self) -> None:
        for seat, param_id in SEAT_PARAMS.items():
            for level in range(4):
                with self.subTest(seat=seat, level=level):
                    body = await self._sent(seat=seat, level=level)
                    assert body.rvcReqType == RvcReqType.VENTILATED_SEATS.value == "22"
                    params = [
                        (p.paramId, base64.b64decode(p.paramValue))
                        for p in body.rvcParams
                    ]
                    assert params == [
                        (param_id, bytes([level])),
                        (255, b"\x00\x00\x00\x00"),
                    ]
                    assert body.vin == sha256_hex_digest(VIN)

    async def test_one_level_seat_on_level(self) -> None:
        assert ONE_LEVEL_VENTILATED_SEAT_ON_LEVEL == 3
        body = await self._sent(
            seat=VentilatedSeat.FRONT_LEFT, level=ONE_LEVEL_VENTILATED_SEAT_ON_LEVEL
        )
        params = [(p.paramId, base64.b64decode(p.paramValue)) for p in body.rvcParams]
        assert params == [(27, b"\x03"), (255, b"\x00\x00\x00\x00")]

    async def test_out_of_range_levels_are_rejected(self) -> None:
        for level in (-1, 4):
            with self.subTest(level=level), pytest.raises(ValueError, match="0-3"):
                await self._sent(seat=VentilatedSeat.FRONT_LEFT, level=level)


class TestVentilatedSeatStatus(unittest.TestCase):
    PAYLOAD = """{
      "basicVehicleStatus": {
        "frontLeftSeatVentLevel": 0,
        "frontRightSeatVentLevel": 2,
        "secondRowLeftSeatVentLevel": 3,
        "secondRowRightSeatVentLevel": 0,
        "lockStatus": 1
      },
      "extendedVehicleStatus": {"alertDataSum": [0, 0, 0]},
      "statusTime": 1790714718
    }"""

    def test_levels_are_parsed(self) -> None:
        status = dacite.from_dict(VehicleStatusResp, json.loads(self.PAYLOAD))
        basic = status.basicVehicleStatus
        assert basic is not None
        assert basic.frontLeftSeatVentLevel == 0
        assert basic.frontRightSeatVentLevel == 2
        assert basic.secondRowLeftSeatVentLevel == 3
        assert basic.secondRowRightSeatVentLevel == 0

    def test_absent_on_cars_without_them(self) -> None:
        payload = json.loads(self.PAYLOAD)
        for key in list(payload["basicVehicleStatus"]):
            if "Vent" in key:
                del payload["basicVehicleStatus"][key]
        status = dacite.from_dict(VehicleStatusResp, payload)
        basic = status.basicVehicleStatus
        assert basic is not None
        assert basic.frontLeftSeatVentLevel is None
        assert basic.secondRowRightSeatVentLevel is None
