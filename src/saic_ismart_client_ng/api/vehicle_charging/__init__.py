from datetime import datetime, timedelta

from saic_ismart_client_ng.api.base import AbstractSaicApi
from saic_ismart_client_ng.api.vehicle_charging.schema import ChargeStatusResp, ChargingControlRequest, \
    ChargingControlResp, ScheduledChargingRequest, ChargingPtcHeatRequest, ChargingSettingRequest, ChrgPtcHeatResp, \
    ScheduledChargingResp, ChargingSettingResp, TargetBatteryCode, ChargeCurrentLimitCode, ScheduledChargingMode, \
    ScheduledBatteryHeatingRequest, ScheduledBatteryHeatingResp, ChrgMgmtDataResp
from saic_ismart_client_ng.crypto_utils import sha256_hex_digest


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

    async def get_vehicle_charging_management_data(self, vin: str) -> ChrgMgmtDataResp:
        return await self.execute_api_call_with_event_id(
            "GET",
            "/vehicle/charging/mgmtData",
            params={
                "vin": sha256_hex_digest(vin),
            },
            out_type=ChrgMgmtDataResp
        )

    async def send_vehicle_charging_control(self, vin: str, body: ChargingControlRequest) -> ChargingControlResp:
        body.vin = sha256_hex_digest(vin)
        return await self.execute_api_call_with_event_id(
            "POST",
            "/vehicle/charging/control",
            body=body,
            out_type=ChargingControlResp
        )

    async def control_charging_port_lock(self, vin: str, *, unlock: bool) -> ChargingControlResp:
        body = ChargingControlRequest(
            chrgCtrlReq=0,
            tboxV2XReq=0,
            tboxEleccLckCtrlReq=2 if unlock else 1,
        )
        return await self.send_vehicle_charging_control(vin, body)

    async def control_charging(self, vin: str, *, stop_charging: bool) -> ChargingControlResp:
        body = ChargingControlRequest(
            chrgCtrlReq=2 if stop_charging else 1,
            tboxV2XReq=0,
            tboxEleccLckCtrlReq=0,
        )
        return await self.send_vehicle_charging_control(vin, body)

    async def send_vehicle_charging_reservation(
            self,
            vin: str,
            body: ScheduledChargingRequest
    ) -> ScheduledChargingResp:
        body.vin = sha256_hex_digest(vin)
        return await self.execute_api_call_with_event_id(
            "POST",
            "/vehicle/charging/reservation",
            body=body,
            out_type=ScheduledChargingResp
        )

    async def set_schedule_charging(
            self,
            vin: str,
            *,
            start_time: datetime.time,
            end_time: datetime.time,
            mode: ScheduledChargingMode
    ) -> ScheduledChargingResp:
        start_hour = start_time.hour
        start_minute = start_time.minute
        end_hour = end_time.hour
        end_minute = end_time.minute
        mode_value = mode.value
        body = ScheduledChargingRequest(
            rsvanStHour=start_hour,
            rsvanStMintue=start_minute,
            rsvanSpHour=end_hour,
            rsvanSpMintue=end_minute,
            tboxAdpPubChrgSttnReq=1,
            tboxReserCtrlReq=mode_value,
        )
        return await self.send_vehicle_charging_reservation(vin, body)

    async def get_vehicle_battery_heating_schedule(self, vin: str) -> ScheduledBatteryHeatingResp:
        return await self.execute_api_call(
            "GET",
            "/charging/batteryHeating",
            params={
                "vin": sha256_hex_digest(vin),
            },
            out_type=ScheduledBatteryHeatingResp
        )

    async def send_vehicle_battery_heating_schedule(
            self,
            vin: str,
            body: ScheduledBatteryHeatingRequest
    ) -> None:
        body.vin = sha256_hex_digest(vin)
        return await self.execute_api_call(
            "POST",
            "/charging/batteryHeating",
            body=body,
        )

    async def disable_schedule_battery_heating(
            self,
            vin: str,
    ) -> None:
        body = ScheduledBatteryHeatingRequest(
            vin=sha256_hex_digest(vin),
            startTime=0,
            status=0,
        )
        return await self.send_vehicle_battery_heating_schedule(vin, body)

    async def enable_schedule_battery_heating(
            self,
            vin: str,
            *,
            start_time: datetime.time,
    ) -> None:
        start_date = datetime.now().replace(
            hour=start_time.hour,
            minute=start_time.minute,
            second=0,
            microsecond=0
        )
        if start_date < datetime.now():
            start_date = start_date + timedelta(days=1)
        body = ScheduledBatteryHeatingRequest(
            vin=sha256_hex_digest(vin),
            startTime=int(start_date.timestamp()) * 1000,
            status=1,
        )
        return await self.send_vehicle_battery_heating_schedule(vin, body)

    async def send_vehicle_charging_ptc_heat(self, vin: str, body: ChargingPtcHeatRequest) -> ChrgPtcHeatResp:
        body.vin = sha256_hex_digest(vin)
        return await self.execute_api_call_with_event_id(
            "POST",
            "/vehicle/charging/ptcHeat",
            body=body,
            out_type=ChrgPtcHeatResp
        )

    async def control_battery_heating(self, vin: str, *, enable: bool) -> ChrgPtcHeatResp:
        body = ChargingPtcHeatRequest(
            ptcHeatReq=1 if enable else 2,
            vin=sha256_hex_digest(vin)
        )
        return await self.send_vehicle_charging_ptc_heat(vin, body)

    async def send_vehicle_charging_settings(self, vin: str, body: ChargingSettingRequest) -> ChargingSettingResp:
        body.vin = sha256_hex_digest(vin)
        return await self.execute_api_call_with_event_id(
            "POST",
            "/vehicle/charging/setting",
            body=body,
            out_type=ChargingSettingResp
        )

    async def set_target_battery_soc(
            self,
            vin: str,
            target_soc: TargetBatteryCode,
            charge_current_limit: ChargeCurrentLimitCode = ChargeCurrentLimitCode.C_IGNORE,
    ) -> ChargingSettingResp:
        body = ChargingSettingRequest(
            onBdChrgTrgtSOCReq=target_soc.value,
            altngChrgCrntReq=charge_current_limit.value,
            tboxV2XSpSOCReq=0,
            vin=sha256_hex_digest(vin)
        )
        return await self.send_vehicle_charging_settings(vin, body)
