"""Front heated seats are named by physical side, not driver/passenger.

Parameters 17 and 18 are the front-left and front-right seats on both left-
and right-hand drive cars: on a right-hand drive MG S6 EV the iSmart app's
front-left (passenger) seat sends 17. HEATED_SEAT_FRONT_LEFT/RIGHT are the
new names; HEATED_SEAT_DRIVER/PASSENGER are kept as aliases, and the bytes
sent are unchanged.
"""

from __future__ import annotations

import base64
from typing import Any
import unittest

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.api.vehicle import RvcParamsId
from saic_ismart_client_ng.api.vehicle.climate import HeatedSeat
from saic_ismart_client_ng.model import SaicApiConfiguration


class TestHeatedSeatSides(unittest.IsolatedAsyncioTestCase):
    def test_front_seats_are_physical_sides(self) -> None:
        assert RvcParamsId.HEATED_SEAT_FRONT_LEFT.value == 17
        assert RvcParamsId.HEATED_SEAT_FRONT_RIGHT.value == 18
        assert HeatedSeat.FRONT_LEFT.value is RvcParamsId.HEATED_SEAT_FRONT_LEFT
        assert HeatedSeat.FRONT_RIGHT.value is RvcParamsId.HEATED_SEAT_FRONT_RIGHT

    def test_old_names_still_work(self) -> None:
        # Looked up by name: mypy doesn't know enum aliases share a member.
        assert RvcParamsId["HEATED_SEAT_DRIVER"] is RvcParamsId.HEATED_SEAT_FRONT_LEFT
        assert (
            RvcParamsId["HEATED_SEAT_PASSENGER"] is RvcParamsId.HEATED_SEAT_FRONT_RIGHT
        )

    async def test_both_front_seats_command_unchanged(self) -> None:
        api = SaicApi(SaicApiConfiguration(username="user", password="pass"))  # noqa: S106
        captured: dict[str, Any] = {}

        async def capture(body: Any, vin: str) -> None:
            captured["body"] = body
            captured["vin"] = vin

        api.send_vehicle_control_command = capture  # type: ignore[method-assign,assignment]
        await api.control_heated_seats(
            "OFFLINE0000000000", left_side_level=1, right_side_level=3
        )
        await api.close()
        params = [
            (p.paramId, base64.b64decode(p.paramValue))
            for p in captured["body"].rvcParams
        ]
        assert params == [(17, b"\x01"), (18, b"\x03"), (255, b"\x00\x00\x00\x00")]
