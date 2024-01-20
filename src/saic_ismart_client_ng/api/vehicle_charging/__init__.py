from saic_ismart_client_ng.crypto_utils import sha256_hex_digest
from saic_ismart_client_ng.api.base import AbstractSaicApi
from saic_ismart_client_ng.api.vehicle_charging.schema import ChargeInfoResp, ChargeStatusResp, ChargingControlRequest, \
    ChargingControlResp, ScheduledChargingRequest, ChargingPtcHeatRequest, ChargingSettingRequest, ChrgPtcHeatResp, \
    ScheduledChargingResp, ChargingSettingResp


class SaicVehicleChargingApi(AbstractSaicApi):

    async def get_vehicle_charging_status(self, vin: str) -> ChargeStatusResp:
        return await self.execute_api_call_with_event_id(
            "GET",
            "/vehicle/charging/status",
            params={
                "vin": sha256_hex_digest(vin),
            },
            out_type=ChargeStatusResp
        )

    async def get_vehicle_charging_management_data(self, vin: str) -> ChargeInfoResp:
        return await self.execute_api_call_with_event_id(
            "GET",
            "/vehicle/charging/mgmtData",
            params={
                "vin": sha256_hex_digest(vin),
            },
            out_type=ChargeInfoResp
        )

    async def send_vehicle_charging_control(self, vin: str, body: ChargingControlRequest) -> ChargingControlResp:
        body.vin = sha256_hex_digest(vin)
        return await self.execute_api_call_with_event_id(
            "POST",
            "/vehicle/charging/control",
            body=body,
            out_type=ChargingControlResp
        )

    async def send_vehicle_charging_reservation(self, vin: str, body: ScheduledChargingRequest) -> ScheduledChargingResp:
        body.vin = sha256_hex_digest(vin)
        return await self.execute_api_call_with_event_id(
            "POST",
            "/vehicle/charging/reservation",
            body=body,
            out_type=ScheduledChargingResp
        )

    async def send_vehicle_charging_ptc_heat(self, vin: str, body: ChargingPtcHeatRequest) -> ChrgPtcHeatResp:
        body.vin = sha256_hex_digest(vin)
        return await self.execute_api_call_with_event_id(
            "POST",
            "/vehicle/charging/ptcHeat",
            body=body,
            out_type=ChrgPtcHeatResp
        )

    async def send_vehicle_charging_settings(self, vin: str, body: ChargingSettingRequest) -> ChargingSettingResp:
        body.vin = sha256_hex_digest(vin)
        return await self.execute_api_call_with_event_id(
            "POST",
            "/vehicle/charging/setting",
            body=body,
            out_type=ChargingSettingResp
        )