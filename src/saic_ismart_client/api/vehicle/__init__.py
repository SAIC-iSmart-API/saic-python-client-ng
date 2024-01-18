import tenacity

from crypto_utils import sha256_hex_digest
from saic_ismart_client.api.base import AbstractSaicApi, saic_api_after_retry, saic_api_retry_policy
from saic_ismart_client.api.vehicle.schema import VehicleListResp, AlarmSwitchResp, AlarmSwitchReq, VehicleStatusResp
from saic_ismart_client.exceptions import SaicApiException


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
        @tenacity.retry(
            stop=tenacity.stop_after_attempt(5),
            wait=tenacity.wait_fixed(3),
            retry=saic_api_retry_policy,
            after=saic_api_after_retry,
        )
        async def get_vehicle_status_inner(event_id: str) -> VehicleStatusResp:
            return await self.execute_api_call(
                "GET",
                "/vehicle/status",
                headers={
                    "event-id": event_id,
                },
                params={
                    "vin": sha256_hex_digest(vin),
                    "vehStatusReqType": "2",
                },
                out_type=VehicleStatusResp,
            )

        return await get_vehicle_status_inner(event_id="0")
