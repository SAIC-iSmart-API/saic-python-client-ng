from __future__ import annotations

from saic_ismart_client_ng.api.vehicle import (
    RvcParams,
    RvcParamsId,
    RvcReqType,
    SaicVehicleApi,
    VehicleControlReq,
    VehicleControlResp,
)
from saic_ismart_client_ng.crypto_utils import sha256_hex_digest


class SaicVehicleClimateApi(SaicVehicleApi):
    async def start_ac(
        self, vin: str, *, temperature_idx: int = 8
    ) -> VehicleControlResp:
        return await self.control_climate(
            vin, fan_speed=2, ac_on=None, temperature_idx=temperature_idx
        )

    async def stop_ac(self, vin: str) -> VehicleControlResp:
        return await self.control_climate(
            vin, fan_speed=0, ac_on=False, temperature_idx=0
        )

    async def start_ac_blowing(self, vin: str) -> VehicleControlResp:
        return await self.control_climate(
            vin, fan_speed=1, ac_on=False, temperature_idx=0
        )

    async def start_front_defrost(self, vin: str) -> VehicleControlResp:
        return await self.control_climate(
            vin, fan_speed=5, ac_on=True, temperature_idx=8
        )

    async def control_climate(
        self,
        vin: str,
        *,
        fan_speed: int = 5,
        ac_on: bool | None = True,
        temperature_idx: int = 8,
    ) -> VehicleControlResp:
        if fan_speed == 0:
            ac_on = False
            temperature_idx = 8

        rvc_params = [RvcParams(RvcParamsId.FAN_SPEED, fan_speed.to_bytes(1, "big"))]

        if fan_speed > 0 or temperature_idx == 0:
            param_fan_speed = RvcParams(
                RvcParamsId.TEMPERATURE, temperature_idx.to_bytes(1, "big")
            )
            rvc_params.append(param_fan_speed)

        if ac_on is not None:
            param_ac_on_off = RvcParams(
                RvcParamsId.AC_ON_OFF, b"\x01" if ac_on else b"\x00"
            )
            rvc_params.append(param_ac_on_off)

        rvc_params.append(RvcParams(RvcParamsId.PARAMS_MAX, b"\x00\x00\x00\x00"))

        body = VehicleControlReq(
            rvc_req_type=RvcReqType.CLIMATE,
            rvc_params=rvc_params,
            vin=sha256_hex_digest(vin),
        )

        return await self.send_vehicle_control_command(body, vin)

    async def control_heated_seats(
        self, vin: str, *, left_side_level: int = 0, right_side_level: int = 0
    ) -> VehicleControlResp:
        rcv_params = [
            RvcParams(
                RvcParamsId.HEATED_SEAT_DRIVER, left_side_level.to_bytes(1, "big")
            ),
            RvcParams(
                RvcParamsId.HEATED_SEAT_PASSENGER, right_side_level.to_bytes(1, "big")
            ),
            RvcParams(RvcParamsId.PARAMS_MAX, b"\x00\x00\x00\x00"),
        ]
        body = VehicleControlReq(
            rvc_req_type=RvcReqType.HEATED_SEATS,
            rvc_params=rcv_params,
            vin=sha256_hex_digest(vin),
        )
        return await self.send_vehicle_control_command(body, vin)

    async def control_rear_window_heat(
        self, vin: str, *, enable: bool
    ) -> VehicleControlResp:
        rvc_params = [
            RvcParams(
                RvcParamsId.REMOTE_HEAT_REAR_WINDOW, b"\x01" if enable else b"\x00"
            ),
            RvcParams(RvcParamsId.PARAMS_MAX, b"\x00\x00\x00\x00"),
        ]
        body = VehicleControlReq(
            rvc_req_type=RvcReqType.REMOTE_HEAT_REAR_WINDOW,
            rvc_params=rvc_params,
            vin=sha256_hex_digest(vin),
        )

        return await self.send_vehicle_control_command(body, vin)
