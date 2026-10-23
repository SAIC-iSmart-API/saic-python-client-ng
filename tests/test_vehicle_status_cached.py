from __future__ import annotations

import unittest
from unittest.mock import AsyncMock

import dacite

from saic_ismart_client_ng.api.vehicle import SaicVehicleApi, VehicleStatusCacheResp
from saic_ismart_client_ng.crypto_utils import sha256_hex_digest

# Captured from /vehicle/status/cache, GPS values removed
CACHE_RESPONSE_DATA = {
    "basicVehicleStatus": {
        "fuelLevelPrc": 0,
        "clstrDspdFuelLvlSgmt": 0,
        "frontLeftTyrePressure": 61,
        "remoteClimateStatus": 0,
        "driverWindow": 0,
        "rearRightTyrePressure": 62,
        "rmtHtdRrWndSt": 0,
        "frontRightTyrePressure": 60,
        "bonnetStatus": 0,
        "lockStatus": 1,
        "bootStatus": 0,
        "fuelRangeElec": 2740,
        "engineStatus": 0,
        "rearRightWindow": 0,
        "fuelRange": 2740,
        "rearLeftTyrePressure": 60,
        "extendedData2": 0,
        "passengerWindow": 0,
        "extendedData1": 63,
        "rearLeftWindow": 0,
        "mileage": 482020,
    },
    "gpsPosition": {"wayPoint": {"position": {}}},
    "statusTime": 1792774872,
    "onlineStatus": 1,
}


class TestVehicleStatusCached(unittest.IsolatedAsyncioTestCase):
    def test_decode_from_json(self) -> None:
        decoded = dacite.from_dict(VehicleStatusCacheResp, CACHE_RESPONSE_DATA)
        assert decoded.statusTime == 1792774872
        assert decoded.onlineStatus == 1
        assert decoded.gpsPosition is not None
        assert decoded.basicVehicleStatus is not None
        assert decoded.basicVehicleStatus.extendedData1 == 63
        assert decoded.basicVehicleStatus.fuelRangeElec == 2740
        assert decoded.basicVehicleStatus.mileage == 482020

    async def test_calls_cache_endpoint(self) -> None:
        expected = VehicleStatusCacheResp(statusTime=1792774872)
        sut = SaicVehicleApi.__new__(SaicVehicleApi)
        sut.execute_api_call = AsyncMock(return_value=expected)  # type: ignore[method-assign]

        result = await sut.get_vehicle_status_cached("VIN123")

        assert result is expected
        sut.execute_api_call.assert_awaited_once_with(
            "GET",
            "/vehicle/status/cache",
            params={"vin": sha256_hex_digest("VIN123"), "vehStatusReqType": "2"},
            out_type=VehicleStatusCacheResp,
        )


if __name__ == "__main__":
    unittest.main()
