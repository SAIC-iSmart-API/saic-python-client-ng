from __future__ import annotations

from saic_ismart_client_ng.api.vehicle import SaicVehicleApi
from saic_ismart_client_ng.api.vehicle.schema import (
    RvcParams,
    RvcParamsId,
    RvcReqType,
    VehicleControlReq,
    VehicleControlResp,
)
from saic_ismart_client_ng.api.vehicle.windows.schema import (
    DoorWindowsAction,
    VehicleWindowId,
)
from saic_ismart_client_ng.crypto_utils import sha256_hex_digest

__all__ = ["DoorWindowsAction", "VehicleWindowId"]


class SaicVehicleWindowsApi(SaicVehicleApi):
    async def control_sunroof(
        self, vin: str, *, should_open: bool
    ) -> VehicleControlResp:
        return await self.control_windows(
            vin, should_open=should_open, windows=[VehicleWindowId.SUNROOF]
        )

    async def close_driver_window(self, vin: str) -> VehicleControlResp:
        return await self.control_windows(
            vin, should_open=False, windows=[VehicleWindowId.DRIVER]
        )

    async def control_windows(
        self, vin: str, *, should_open: bool, windows: list[VehicleWindowId]
    ) -> VehicleControlResp:
        requested_windows = [w.value.value for w in windows]
        rcv_params = []
        for i in [
            VehicleWindowId.SUNROOF,
            VehicleWindowId.DRIVER,
            VehicleWindowId.WINDOW_2,
            VehicleWindowId.WINDOW_3,
            VehicleWindowId.WINDOW_4,
        ]:
            if i.value.value in requested_windows:
                rcv_params.append(RvcParams(i.value, b"\x01"))
            else:
                rcv_params.append(RvcParams(i.value, b"\x00"))

        rcv_params.append(
            RvcParams(
                RvcParamsId.WINDOW_OPEN_CLOSE, b"\x03" if should_open else b"\x00"
            )
        )

        request = VehicleControlReq(
            rvc_req_type=RvcReqType.WINDOWS,
            rvc_params=rcv_params,
            vin=sha256_hex_digest(vin),
        )

        return await self.send_vehicle_control_command(request, vin)

    async def control_door_windows(
        self, vin: str, *, action: DoorWindowsAction
    ) -> VehicleControlResp:
        """Close, ventilate or fully open all four door windows together.

        Matches what the iSmart app sends (decrypted MG S6 EV traffic): the
        sunroof parameter set to 0 (left alone), all four door windows set to
        1, and the action (0 close, 1 ventilate, 2 fully open). There is no
        end-of-parameters marker. The MG S6 EV doesn't accept single-window
        control this way.

        ``control_windows(should_open=True)`` sends 3 as its open value, which
        the MG S6 EV does not use; it is left unchanged for other models.
        """
        rvc_params = [
            RvcParams(RvcParamsId.WINDOW_SUNROOF, b"\x00"),
            RvcParams(RvcParamsId.WINDOW_DRIVER, b"\x01"),
            RvcParams(RvcParamsId.WINDOW_2, b"\x01"),
            RvcParams(RvcParamsId.WINDOW_3, b"\x01"),
            RvcParams(RvcParamsId.WINDOW_4, b"\x01"),
            RvcParams(RvcParamsId.WINDOW_OPEN_CLOSE, action.value.to_bytes(1, "big")),
        ]
        request = VehicleControlReq(
            rvc_req_type=RvcReqType.WINDOWS,
            rvc_params=rvc_params,
            vin=sha256_hex_digest(vin),
        )
        return await self.send_vehicle_control_command(request, vin)
