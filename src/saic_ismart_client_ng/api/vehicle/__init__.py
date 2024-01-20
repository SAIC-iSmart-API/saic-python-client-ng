import tenacity

from crypto_utils import sha256_hex_digest
from saic_ismart_client_ng.api.base import AbstractSaicApi
from saic_ismart_client_ng.api.vehicle.schema import VehicleListResp, AlarmSwitchResp, AlarmSwitchReq, \
    VehicleStatusResp, \
    VehicleControlReq, VehicleControlResp
from saic_ismart_client_ng.exceptions import SaicApiException


class SaicVehicleApi(AbstractSaicApi):
    @tenacity.retry(
        stop=tenacity.stop_after_attempt(1),
        retry=tenacity.retry_if_not_exception_type(SaicApiException),
    )
    async def vehicle_list(self) -> VehicleListResp:
        return await self.execute_api_call("GET", "/vehicle/list", out_type=VehicleListResp)

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(1),
        retry=tenacity.retry_if_not_exception_type(SaicApiException),
    )
    async def get_alarm_switch(self, vin) -> AlarmSwitchResp:
        return await self.execute_api_call("GET", "/vehicle/alarmSwitch", out_type=AlarmSwitchResp,
                                           params={"vin": sha256_hex_digest(vin)})

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(1),
        retry=tenacity.retry_if_not_exception_type(SaicApiException),
    )
    async def set_alarm_switches(self, body: AlarmSwitchReq, vin: str) -> None:
        body.vin = sha256_hex_digest(vin)
        return await self.execute_api_call("PUT", "/vehicle/alarmSwitch", body=body)

    async def get_vehicle_status(self, vin: str) -> VehicleStatusResp:
        return await self.execute_api_call_with_event_id(
            "GET",
            "/vehicle/status",
            params={
                "vin": sha256_hex_digest(vin),
                "vehStatusReqType": "2",
            },
            out_type=VehicleStatusResp,
        )

    async def send_vehicle_control_command(self, body: VehicleControlReq, vin: str) -> VehicleControlResp:
        body.vin = sha256_hex_digest(vin)
        return await self.execute_api_call_with_event_id(
            "POST",
            "/vehicle/control",
            body=body,
            out_type=VehicleControlResp,
        )
