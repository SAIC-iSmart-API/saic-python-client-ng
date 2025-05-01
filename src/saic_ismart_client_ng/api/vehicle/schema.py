import base64
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from saic_ismart_client_ng.api.schema import GpsPosition
from saic_ismart_client_ng.api.serialization_utils import decode_bytes


@dataclass
class VehicleModelConfiguration:
    itemCode: Optional[str] = None
    itemName: Optional[str] = None
    itemValue: Optional[str] = None


@dataclass
class SubAccount:
    authorizationCardType: Optional[int] = None
    btKeyStatus: Optional[int] = None
    locationAuthorization: Optional[int] = None
    modelName: Optional[str] = None
    operationType: Optional[int] = None
    status: Optional[int] = None
    subaccountId: Optional[int] = None
    subscriberId: Optional[int] = None
    userAccount: Optional[str] = None
    userName: Optional[str] = None
    validityEndTime: Optional[int] = None
    validityStartTime: Optional[int] = None
    vin: Optional[str] = None


@dataclass
class VinInfo:
    bindTime: Optional[int] = None
    brandName: Optional[str] = None
    colorName: Optional[str] = None
    isActivate: Optional[bool] = None
    isCurrentVehicle: Optional[bool] = None
    isSubaccount: Optional[bool] = None
    modelName: Optional[str] = None
    modelYear: Optional[str] = None
    name: Optional[str] = None
    series: Optional[str] = None
    vin: Optional[str] = None
    subAccountList: List[SubAccount] = field(default_factory=list)
    vehicleModelConfiguration: List[VehicleModelConfiguration] = field(default_factory=list)


@dataclass
class VehicleListResp:
    vinList: List[VinInfo] = field(default_factory=list)


@dataclass
class BasicVehicleStatus:
    batteryVoltage: Optional[int] = None
    bonnetStatus: Optional[int] = None
    bootStatus: Optional[int] = None
    canBusActive: Optional[int] = None
    clstrDspdFuelLvlSgmt: Optional[int] = None
    currentJourneyId: Optional[int] = None
    currentJourneyDistance: Optional[int] = None
    dippedBeamStatus: Optional[int] = None
    driverDoor: Optional[int] = None
    driverWindow: Optional[int] = None
    engineStatus: Optional[int] = None
    extendedData1: Optional[int] = None
    extendedData2: Optional[int] = None
    exteriorTemperature: Optional[int] = None
    frontLeftSeatHeatLevel: Optional[int] = None
    frontLeftTyrePressure: Optional[int] = None
    frontRightSeatHeatLevel: Optional[int] = None
    frontRightTyrePressure: Optional[int] = None
    fuelLevelPrc: Optional[int] = None
    fuelRange: Optional[int] = None
    fuelRangeElec: Optional[int] = None
    handBrake: Optional[int] = None
    interiorTemperature: Optional[int] = None
    lastKeySeen: Optional[int] = None
    lockStatus: Optional[int] = None
    mainBeamStatus: Optional[int] = None
    mileage: Optional[int] = None
    passengerDoor: Optional[int] = None
    passengerWindow: Optional[int] = None
    powerMode: Optional[int] = None
    rearLeftDoor: Optional[int] = None
    rearLeftTyrePressure: Optional[int] = None
    rearLeftWindow: Optional[int] = None
    rearRightDoor: Optional[int] = None
    rearRightTyrePressure: Optional[int] = None
    rearRightWindow: Optional[int] = None
    remoteClimateStatus: Optional[int] = None
    rmtHtdRrWndSt: Optional[int] = None
    sideLightStatus: Optional[int] = None
    steeringHeatLevel: Optional[int] = None
    steeringWheelHeatFailureReason: Optional[int] = None
    sunroofStatus: Optional[int] = None
    timeOfLastCANBUSActivity: Optional[int] = None
    vehElecRngDsp: Optional[int] = None
    vehicleAlarmStatus: Optional[int] = None
    wheelTyreMonitorStatus: Optional[int] = None


@dataclass
class ExtendedVehicleStatus:
    alertDataSum: list = field(default_factory=list)


@dataclass
class VehicleStatusResp:
    basicVehicleStatus: Optional[BasicVehicleStatus] = None
    extendedVehicleStatus: Optional[ExtendedVehicleStatus] = None
    gpsPosition: Optional[GpsPosition] = None
    statusTime: Optional[int] = None

    @property
    def is_parked(self) -> bool:
        return (v := self.basicVehicleStatus) is not None and (
                v.engineStatus != 1
                or v.handBrake == 1
        )

    @property
    def is_engine_running(self) -> bool:
        return (v := self.basicVehicleStatus) is not None and v.engineStatus == 1


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

    def __init__(self, param_id: RvcParamsId, param_value: bytes):
        self.paramId = param_id.value
        self.paramValue = base64.b64encode(param_value).decode('utf-8')


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
    rvcParams: Optional[List[RvcParams]]
    rvcReqType: Optional[str | int]
    vin: str

    def __init__(self, rvc_params: Optional[List[RvcParams]], rvc_req_type: RvcReqType, vin: str):
        self.rvcParams = rvc_params
        self.rvcReqType = rvc_req_type.value
        self.vin = vin

    @property
    def rvc_req_type_decoded(self) -> Optional[bytes]:
        return decode_bytes(input_value=self.rvcReqType, field_name='rvcReqType')


@dataclass
class VehicleControlResp:
    basicVehicleStatus: Optional[BasicVehicleStatus] = None
    failureType: Optional[int] = None
    gpsPosition: Optional[GpsPosition] = None
    rvcReqSts: Optional[str | int] = None
    rvcReqType: Optional[str | int] = None

    @property
    def rvc_req_sts_decoded(self) -> Optional[bytes]:
        return decode_bytes(input_value=self.rvcReqSts, field_name='rvcReqSts')

    @property
    def rvc_req_type_decoded(self) -> Optional[bytes]:
        return decode_bytes(input_value=self.rvcReqType, field_name='rvcReqType')
