"""Rear (second row) heated seat levels in the vehicle status (#34).

The /vehicle/status response from an MG S6 EV carries
secondRowLeftSeatHeatLevel and secondRowRightSeatHeatLevel, which were
dropped because BasicVehicleStatus had no fields for them.
"""

from __future__ import annotations

import json
import unittest

import dacite

from saic_ismart_client_ng.api.vehicle import VehicleStatusResp

# Trimmed MG S6 EV (series MIS3E) response with one rear seat heating.
MGS6_STATUS = """{
  "basicVehicleStatus": {
    "frontLeftSeatHeatLevel": 0,
    "frontRightSeatHeatLevel": 2,
    "secondRowLeftSeatHeatLevel": 3,
    "secondRowRightSeatHeatLevel": 0,
    "steeringHeatLevel": 0,
    "lockStatus": 1
  },
  "extendedVehicleStatus": {"alertDataSum": [0, 0, 0]},
  "statusTime": 1790714718
}"""


class TestRearSeatHeatLevels(unittest.TestCase):
    def test_rear_seat_heat_levels(self) -> None:
        basic = dacite.from_dict(VehicleStatusResp, json.loads(MGS6_STATUS))
        assert basic.basicVehicleStatus is not None
        assert basic.basicVehicleStatus.secondRowLeftSeatHeatLevel == 3
        assert basic.basicVehicleStatus.secondRowRightSeatHeatLevel == 0
        assert basic.basicVehicleStatus.frontRightSeatHeatLevel == 2

    def test_absent_on_cars_without_them(self) -> None:
        payload = json.loads(MGS6_STATUS)
        del payload["basicVehicleStatus"]["secondRowLeftSeatHeatLevel"]
        del payload["basicVehicleStatus"]["secondRowRightSeatHeatLevel"]
        status = dacite.from_dict(VehicleStatusResp, payload)
        assert status.basicVehicleStatus is not None
        assert status.basicVehicleStatus.secondRowLeftSeatHeatLevel is None
        assert status.basicVehicleStatus.secondRowRightSeatHeatLevel is None
