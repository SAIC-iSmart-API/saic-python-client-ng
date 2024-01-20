from crypto_utils import sha256_hex_digest
from saic_ismart_client_ng.api.base import AbstractSaicApi


class SaicVehicleChargingApi(AbstractSaicApi):

    async def get_vehicle_charging_status(self, vin: str) -> None:
        return await self.execute_api_call_with_event_id(
            "GET",
            "/vehicle/charging/status",
            params={
                "vin": sha256_hex_digest(vin),
            },
            out_type=None
        )

    async def get_vehicle_charging_management_data(self, vin: str) -> None:
        return await self.execute_api_call_with_event_id(
            "GET",
            "/vehicle/charging/mgmtData",
            params={
                "vin": sha256_hex_digest(vin),
            },
            out_type=None
        )
