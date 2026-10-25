"""Door windows are named after the status model, the old names are aliases.

The parameters sent to the car don't change.
"""

from __future__ import annotations

import base64
from typing import Any
import unittest

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.api.vehicle import RvcParamsId
from saic_ismart_client_ng.api.vehicle.windows import VehicleWindowId
from saic_ismart_client_ng.model import SaicApiConfiguration


class TestDoorWindowNames(unittest.IsolatedAsyncioTestCase):
    def test_new_names_keep_the_param_ids(self) -> None:
        assert RvcParamsId.WINDOW_DRIVER.value == 9
        assert RvcParamsId.WINDOW_PASSENGER.value == 10
        assert RvcParamsId.WINDOW_REAR_LEFT.value == 11
        assert RvcParamsId.WINDOW_REAR_RIGHT.value == 12

    def test_old_names_still_work(self) -> None:
        # Looked up by name: mypy doesn't know enum aliases share a member.
        assert RvcParamsId["WINDOW_2"] is RvcParamsId.WINDOW_PASSENGER
        assert RvcParamsId["WINDOW_3"] is RvcParamsId.WINDOW_REAR_LEFT
        assert RvcParamsId["WINDOW_4"] is RvcParamsId.WINDOW_REAR_RIGHT
        assert VehicleWindowId["WINDOW_2"] is VehicleWindowId.PASSENGER
        assert VehicleWindowId["WINDOW_3"] is VehicleWindowId.REAR_LEFT
        assert VehicleWindowId["WINDOW_4"] is VehicleWindowId.REAR_RIGHT

    async def test_control_windows_command_unchanged(self) -> None:
        api = SaicApi(SaicApiConfiguration(username="user", password="pass"))  # noqa: S106
        captured: dict[str, Any] = {}

        async def capture(body: Any, _vin: str) -> None:
            captured["body"] = body

        api.send_vehicle_control_command = capture  # type: ignore[method-assign,assignment]
        await api.control_windows(
            "OFFLINE0000000000",
            should_open=False,
            windows=[VehicleWindowId.PASSENGER],
        )
        await api.close()
        params = [
            (p.paramId, base64.b64decode(p.paramValue))
            for p in captured["body"].rvcParams
        ]
        assert params == [
            (8, b"\x00"),
            (9, b"\x00"),
            (10, b"\x01"),
            (11, b"\x00"),
            (12, b"\x00"),
            (13, b"\x00"),
        ]
