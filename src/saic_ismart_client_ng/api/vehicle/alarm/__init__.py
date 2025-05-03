from __future__ import annotations

from saic_ismart_client_ng.api.vehicle import SaicVehicleApi
from saic_ismart_client_ng.api.vehicle.alarm.schema import (
    AlarmSwitch,
    AlarmSwitchReq,
    AlarmSwitchResp,
    AlarmType,
)
from saic_ismart_client_ng.crypto_utils import sha256_hex_digest

__all__ = [
    "AlarmSwitch",
    "AlarmSwitchReq",
    "AlarmSwitchResp",
    "AlarmType",
]


class SaicVehicleAlarmApi(SaicVehicleApi):
    async def get_alarm_switch(self, vin: str) -> AlarmSwitchResp:
        return await self.execute_api_call(
            "GET",
            "/vehicle/alarmSwitch",
            out_type=AlarmSwitchResp,
            params={"vin": sha256_hex_digest(vin)},
        )

    async def set_alarm_switches(
        self, alarm_switches: list[AlarmType], vin: str
    ) -> None:
        actual_switches = [
            AlarmSwitch(alarmType=alarm_type.value, alarmSwitch=1, functionSwitch=1)
            for alarm_type in alarm_switches
        ]
        body = AlarmSwitchReq(
            alarmSwitchList=actual_switches, vin=sha256_hex_digest(vin)
        )
        await self.execute_api_call_no_result("PUT", "/vehicle/alarmSwitch", body=body)
