import tenacity

from crypto_utils import sha256_hex_digest
from saic_ismart_client_ng.api.base import AbstractSaicApi, saic_api_after_retry, saic_api_retry_policy


class SaicVehicleChargingApi(AbstractSaicApi):

    async def get_vehicle_charging_status(self, vin: str) -> None:
        @tenacity.retry(
            stop=tenacity.stop_after_attempt(5),
            wait=tenacity.wait_fixed(3),
            retry=saic_api_retry_policy,
            after=saic_api_after_retry,
        )
        async def get_vehicle_charging_status_inner(event_id: str) -> None:
            return await self.execute_api_call(
                "GET",
                "/vehicle/charging/status",
                headers={
                    "event-id": event_id,
                },
                params={
                    "vin": sha256_hex_digest(vin),
                },
                out_type=None,
            )

        return await get_vehicle_charging_status_inner(event_id="0")

    """
    DEBUG [2024-01-18 21:52:10] root - Response code: 0 {"code":0,"data":{"rvsChargeStatus":{"mileageSinceLastCharge":0,"totalBatteryCapacity":725,"workingVoltage":1630,"chargingDuration":27,"chargingType":6,"fuelRangeElec":3190,"realtimePower":542,"workingCurrent":19919,"chargingGunState":1,"mileageOfDay":0,"startTime":1705611101,"endTime":1705605882,"powerUsageOfDay":0,"powerUsageSinceLastCharge":0,"mileage":133650},"chrgMgmtData":{"bmsChrgOtptCrntReqV":0,"ccuOnbdChrgrPlugOn":4,"bmsPTCHeatResp":0,"bmsChrgSts":1,"chrgngAddedElecRngV":0,"bmsPackSOCDsp":748,"ccuOffBdChrgrPlugOn":1,"bmsPackCrnt":19919,"imcuChrgngEstdElecRng":445,"chrgngSpdngTimeV":0,"bmsReserStMintueDspCmd":0,"bmsDsChrgSpRsn":0,"imcuChrgngEstdElecRngV":0,"bmsPackVol":1630,"bmsPackCrntV":0,"imcuVehElecRngV":0,"bmsReserSpHourDspCmd":6,"bmsAdpPubChrgSttnDspCmd":0,"bmsReserSpMintueDspCmd":0,"bmsAltngChrgCrntDspCmd":4,"disChrgngRmnngTimeV":1,"imcuDschrgngEstdElecRngV":0,"bmsChrgSpRsn":0,"disChrgngRmnngTime":1023,"chrgngAddedElecRng":0,"clstrElecRngToEPT":319,"bmsPTCHeatReqDspCmd":2,"ccuEleccLckCtrlDspCmd":1,"bmsChrgCtrlDspCmd":1,"bmsOnBdChrgTrgtSOCDspCmd":7,"onBdChrgrAltrCrntInptCrnt":46,"bmsEstdElecRng":445,"chrgngDoorOpenCnd":0,"bmsReserCtrlDspCmd":1,"bmsChrgOtptCrntReq":108,"chrgngDoorPosSts":1,"bmsReserStHourDspCmd":22,"imcuVehElecRng":319,"chrgngSpdngTime":0,"chrgngRmnngTimeV":0,"imcuDschrgngEstdElecRng":343,"chrgngRmnngTime":584,"onBdChrgrAltrCrntInptVol":109}},"message":"success"}
    """

    async def get_vehicle_charging_management_data(self, vin: str) -> None:
        @tenacity.retry(
            stop=tenacity.stop_after_attempt(5),
            wait=tenacity.wait_fixed(3),
            retry=saic_api_retry_policy,
            after=saic_api_after_retry,
        )
        async def get_vehicle_charging_management_data_inner(event_id: str) -> None:
            return await self.execute_api_call(
                "GET",
                "/vehicle/charging/mgmtData",
                headers={
                    "event-id": event_id,
                },
                params={
                    "vin": sha256_hex_digest(vin),
                },
                out_type=None,
            )

        return await get_vehicle_charging_management_data_inner(event_id="0")
