from saic_ismart_client_ng import SaicVehicleApi
from saic_ismart_client_ng.api.vehicle.schema import VehicleControlReq, VehicleControlResp, RvcParams, RvcReqType, \
    RvcParamsId
from saic_ismart_client_ng.api.vehicle.windows.schema import VehicleWindowId
from saic_ismart_client_ng.crypto_utils import sha256_hex_digest


class SaicVehicleWindowsApi(SaicVehicleApi):

    async def control_sunroof(self, vin: str, *, should_open: bool) -> VehicleControlResp:
        return await self.control_windows(vin, should_open=should_open, windows=[VehicleWindowId.SUNROOF])

    async def close_driver_window(self, vin: str) -> VehicleControlResp:
        return await self.control_windows(vin, should_open=False, windows=[VehicleWindowId.DRIVER])

    async def control_windows(self, vin: str, *, should_open: bool, windows: [VehicleWindowId]) -> VehicleControlResp:
        requested_windows = [w.value.value for w in windows]
        rcv_params = []
        for i in [
            VehicleWindowId.SUNROOF,
            VehicleWindowId.DRIVER,
            VehicleWindowId.WINDOW_2,
            VehicleWindowId.WINDOW_3,
            VehicleWindowId.WINDOW_4
        ]:
            if i.value.value in requested_windows:
                rcv_params.append(RvcParams(i.value, b'\x01'))
            else:
                rcv_params.append(RvcParams(i.value, b'\x00'))

        rcv_params.append(RvcParams(RvcParamsId.WINDOW_OPEN_CLOSE, b'\x03' if should_open else b'\x00'))

        request = VehicleControlReq(
            rvc_req_type=RvcReqType.WINDOWS,
            rvc_params=rcv_params,
            vin=sha256_hex_digest(vin),
        )

        return await self.send_vehicle_control_command(request, vin)
