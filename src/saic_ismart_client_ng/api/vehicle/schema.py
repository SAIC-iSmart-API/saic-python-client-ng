from dataclasses import dataclass, field
from enum import Enum
from typing import List

from saic_ismart_client_ng.api.schema import GpsPosition


@dataclass
class VehicleListResp:
    @dataclass
    class VinList:
        @dataclass
        class SubAccount:
            authorizationCardType: int = None
            btKeyStatus: int = None
            locationAuthorization: int = None
            modelName: str = None
            operationType: int = None
            status: int = None
            subaccountId: int = None
            subscriberId: int = None
            userAccount: str = None
            userName: str = None
            validityEndTime: int = None
            validityStartTime: int = None
            vin: str = None

        @dataclass
        class VehicleModelConfiguration:
            itemCode: str = None
            itemName: str = None
            itemValue: str = None

        bindTime: int = None
        brandName: str = None
        colorName: str = None
        isActivate: bool = None
        isCurrentVehicle: bool = None
        isSubaccount: bool = None
        modelName: str = None
        modelYear: str = None
        name: str = None
        series: str = None
        vin: str = None
        subAccountList: List[SubAccount] = field(default_factory=list)
        vehicleModelConfiguration: List[VehicleModelConfiguration] = field(default_factory=list)

    vinList: List[VinList] = field(default_factory=list)


class AlarmType(Enum):
    ALARM_TYPE_VEHICLE_FAULT = 0
    ALARM_TYPE_GEOFENCE = 2
    ALARM_TYPE_VEHICLE_START = 3


@dataclass
class AlarmSwitch:
    alarmType: int = None
    functionSwitch: int = None
    alarmSwitch: int = None


@dataclass
class AlarmSwitchResp:
    alarmSwitchList: List[AlarmSwitch] = field(default_factory=list)


@dataclass
class AlarmSwitchReq:
    vin: str
    alarmSwitchList: List[AlarmSwitch] = field(default_factory=list)


@dataclass
class BasicVehicleStatus:
    batteryVoltage: int = None
    bonnetStatus: int = None
    bootStatus: int = None
    canBusActive: int = None
    clstrDspdFuelLvlSgmt: int = None
    currentJourneyID: int = None
    currentjourneyDistance: int = None
    dippedBeamStatus: int = None
    driverDoor: int = None
    driverWindow: int = None
    engineStatus: int = None
    extendedData1: int = None
    extendedData2: int = None
    exteriorTemperature: int = None
    frontLeftSeatHeatLevel: int = None
    frontLeftTyrePressure: int = None
    frontRightSeatHeatLevel: int = None
    frontRightTyrePressure: int = None
    fuelLevelPrc: int = None
    fuelRange: int = None
    fuelRangeElec: int = None
    handbrake: int = None
    interiorTemperature: int = None
    lastKeySeen: int = None
    lockStatus: int = None
    mainBeamStatus: int = None
    mileage: int = None
    passengerDoor: int = None
    passengerWindow: int = None
    powerMode: int = None
    rearLeftDoor: int = None
    rearLeftTyrePressure: int = None
    rearLeftWindow: int = None
    rearRightDoor: int = None
    rearRightTyrePressure: int = None
    rearRightWindow: int = None
    remoteClimateStatus: int = None
    rmtHtdRrWndSt: int = None
    sideLightStatus: int = None
    sunroofStatus: int = None
    timeOfLastCANBUSActivity: int = None
    vehElecRngDsp: int = None
    vehicleAlarmStatus: int = None
    wheelTyreMonitorStatus: int = None


@dataclass
class VehicleStatusResp:
    @dataclass
    class ExtendedVehicleStatus:
        alertDataSum: list = field(default_factory=list)

    basicVehicleStatus: BasicVehicleStatus = None
    extendedVehicleStatus: ExtendedVehicleStatus = None
    gpsPosition: GpsPosition = None
    statusTime: int = None


@dataclass
class VehicleControlReq:
    rvcParams: List[int]
    rvcReqType: str
    vin: str


@dataclass
class VehicleControlResp:
    basicVehicleStatus: BasicVehicleStatus = None
    failureType: int = None
    gpsPosition: GpsPosition = None
    rvcReqSts: int = None
    rvcReqType: int = None
