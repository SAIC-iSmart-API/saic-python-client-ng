from typing import Optional

from saic_ismart_client_ng import SaicVehicleApi
from saic_ismart_client_ng.api.vehicle.locks.schema import VehicleLockId
from saic_ismart_client_ng.api.vehicle.schema import VehicleControlReq, VehicleControlResp, RvcParams, \
    RvcReqType, RvcParamsId
from saic_ismart_client_ng.crypto_utils import sha256_hex_digest


class SaicVehicleLocksApi(SaicVehicleApi):

    async def lock_vehicle(self, vin: str) -> VehicleControlResp:
        return await self.control_vehicle_locks(vin, should_lock=True)

    async def unlock_vehicle(self, vin: str) -> VehicleControlResp:
        return await self.control_vehicle_locks(vin, should_lock=False, lock_id=VehicleLockId.DOORS)

    async def open_tailgate(self, vin: str) -> VehicleControlResp:
        return await self.control_vehicle_locks(vin, should_lock=False, lock_id=VehicleLockId.TAILGATE)

    async def control_vehicle_locks(
            self,
            vin: str,
            *,
            should_lock: bool,
            lock_id: Optional[VehicleLockId] = None,
    ) -> VehicleControlResp:
        if should_lock:
            request_type = RvcReqType.CLOSE_LOCKS
            params = None
        else:
            request_type = RvcReqType.OPEN_LOCKS
            params = [
                RvcParams(RvcParamsId.UNK_4, b'\x00'),
                RvcParams(RvcParamsId.UNK_5, b'\x00'),
                RvcParams(RvcParamsId.UNK_6, b'\x00'),
                RvcParams(RvcParamsId.LOCK_ID, lock_id.value.to_bytes(1, byteorder='big')),
                RvcParams(RvcParamsId.PARAMS_MAX, b'\x00\x00\x00\x00'),
            ]
        command = VehicleControlReq(
            rvc_req_type=request_type,
            rvc_params=params,
            vin=sha256_hex_digest(vin),
        )
        return await self.send_vehicle_control_command(command, vin)
