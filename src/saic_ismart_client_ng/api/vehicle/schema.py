from __future__ import annotations

import base64
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from saic_ismart_client_ng.api.serialization_utils import decode_bytes

if TYPE_CHECKING:
    from saic_ismart_client_ng.api.schema import GpsPosition


@dataclass
class VehicleModelConfiguration:
    itemCode: str | None = None
    itemName: str | None = None
    itemValue: str | None = None


@dataclass
class SubAccount:
    authorizationCardType: int | None = None
    btKeyStatus: int | None = None
    locationAuthorization: int | None = None
    modelName: str | None = None
    operationType: int | None = None
    status: int | None = None
    subaccountId: int | None = None
    subscriberId: int | None = None
    userAccount: str | None = None
    userName: str | None = None
    validityEndTime: int | None = None
    validityStartTime: int | None = None
    vin: str | None = None


@dataclass
class VinInfo:
    bindTime: int | None = None
    brandName: str | None = None
    colorName: str | None = None
    isActivate: bool | None = None
    isCurrentVehicle: bool | None = None
    isSubaccount: bool | None = None
    modelName: str | None = None
    modelYear: str | None = None
    name: str | None = None
    series: str | None = None
    vin: str | None = None
    subAccountList: list[SubAccount] = field(default_factory=list)
    vehicleModelConfiguration: list[VehicleModelConfiguration] = field(
        default_factory=list
    )


@dataclass
class VehicleListResp:
    vinList: list[VinInfo] = field(default_factory=list)


@dataclass
class BasicVehicleStatus:
    batteryVoltage: int | None = None
    bonnetStatus: int | None = None
    bootStatus: int | None = None
    canBusActive: int | None = None
    clstrDspdFuelLvlSgmt: int | None = None
    currentJourneyId: int | None = None
    currentJourneyDistance: int | None = None
    dippedBeamStatus: int | None = None
    driverDoor: int | None = None
    driverWindow: int | None = None
    engineStatus: int | None = None
    extendedData1: int | None = None
    extendedData2: int | None = None
    exteriorTemperature: int | None = None
    frontLeftSeatHeatLevel: int | None = None
    frontLeftTyrePressure: int | None = None
    frontRightSeatHeatLevel: int | None = None
    frontRightTyrePressure: int | None = None
    fuelLevelPrc: int | None = None
    fuelRange: int | None = None
    fuelRangeElec: int | None = None
    handBrake: int | None = None
    interiorTemperature: int | None = None
    lastKeySeen: int | None = None
    lockStatus: int | None = None
    mainBeamStatus: int | None = None
    mileage: int | None = None
    passengerDoor: int | None = None
    passengerWindow: int | None = None
    powerMode: int | None = None
    rearLeftDoor: int | None = None
    rearLeftTyrePressure: int | None = None
    rearLeftWindow: int | None = None
    rearRightDoor: int | None = None
    rearRightTyrePressure: int | None = None
    rearRightWindow: int | None = None
    remoteClimateStatus: int | None = None
    rmtHtdRrWndSt: int | None = None
    sideLightStatus: int | None = None
    steeringHeatLevel: int | None = None
    steeringWheelHeatFailureReason: int | None = None
    sunroofStatus: int | None = None
    timeOfLastCANBUSActivity: int | None = None
    vehElecRngDsp: int | None = None
    vehicleAlarmStatus: int | None = None
    wheelTyreMonitorStatus: int | None = None

    @property
    def is_parked(self) -> bool:
        return self.engineStatus != 1 or self.handBrake == 1

    @property
    def is_engine_running(self) -> bool:
        return self.engineStatus == 1


@dataclass
class ExtendedVehicleStatus:
    alertDataSum: list[Any] = field(default_factory=list)


@dataclass
class VehicleStatusResp:
    # pylint: disable=import-outside-toplevel
    from saic_ismart_client_ng.api.schema import GpsPosition

    basicVehicleStatus: BasicVehicleStatus | None = None
    extendedVehicleStatus: ExtendedVehicleStatus | None = None
    gpsPosition: GpsPosition | None = None
    statusTime: int | None = None


class RvcParamsId(Enum):
    FIND_MY_CAR_ENABLE = 1
    FIND_MY_CAR_HORN = 2
    FIND_MY_CAR_LIGHTS = 3
    UNK_4 = 4
    UNK_5 = 5
    UNK_6 = 6
    LOCK_ID = 7
    WINDOW_SUNROOF = 8
    WINDOW_DRIVER = 9
    WINDOW_2 = 10
    WINDOW_3 = 11
    WINDOW_4 = 12
    WINDOW_OPEN_CLOSE = 13
    HEATED_SEAT_DRIVER = 17
    HEATED_SEAT_PASSENGER = 18
    FAN_SPEED = 19
    TEMPERATURE = 20
    AC_ON_OFF = 22
    REMOTE_HEAT_REAR_WINDOW = 23
    PARAMS_MAX = 0xFF


@dataclass
class RvcParams:
    paramId: int
    paramValue: str

    def __init__(self, param_id: RvcParamsId, param_value: bytes) -> None:
        self.paramId = param_id.value
        self.paramValue = base64.b64encode(param_value).decode("utf-8")


class RvcReqType(Enum):
    FIND_MY_CAR = "0"
    CLOSE_LOCKS = "1"
    OPEN_LOCKS = "2"
    WINDOWS = "3"
    KEY_MANAGEMENT = "4"
    HEATED_SEATS = "5"
    CLIMATE = "6"
    AIR_CLEAN = "7"
    ENGINE_CONTROL = "17"
    REMOTE_REFRESH = "18"
    REMOTE_IMMOBILIZER = "19"
    REMOTE_HEAT_REAR_WINDOW = "32"
    MAX_VALUE = "597"


@dataclass
class VehicleControlReq:
    rvcParams: list[RvcParams] | None
    rvcReqType: str | int | None
    vin: str

    def __init__(
        self, rvc_params: list[RvcParams] | None, rvc_req_type: RvcReqType, vin: str
    ) -> None:
        self.rvcParams = rvc_params
        self.rvcReqType = rvc_req_type.value
        self.vin = vin

    @property
    def rvc_req_type_decoded(self) -> bytes | None:
        return decode_bytes(input_value=self.rvcReqType, field_name="rvcReqType")


@dataclass
class VehicleControlResp:
    # pylint: disable=import-outside-toplevel
    from saic_ismart_client_ng.api.schema import GpsPosition

    basicVehicleStatus: BasicVehicleStatus | None = None
    failureType: int | None = None
    gpsPosition: GpsPosition | None = None
    rvcReqSts: str | int | None = None
    rvcReqType: str | int | None = None

    @property
    def rvc_req_sts_decoded(self) -> bytes | None:
        return decode_bytes(input_value=self.rvcReqSts, field_name="rvcReqSts")

    @property
    def rvc_req_type_decoded(self) -> bytes | None:
        return decode_bytes(input_value=self.rvcReqType, field_name="rvcReqType")
