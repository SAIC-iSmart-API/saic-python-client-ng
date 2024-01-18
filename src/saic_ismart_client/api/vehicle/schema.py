from dataclasses import dataclass, field
from enum import Enum
from typing import List


@dataclass
class VehicleListResp:
    @dataclass
    class VinListDTO:
        @dataclass
        class SubAccountListDTO:
            authorizationCardType: int = field(init=False),
            btKeyStatus: int = field(init=False),
            locationAuthorization: int = field(init=False),
            modelName: str = field(init=False),
            operationType: int = field(init=False),
            status: int = field(init=False),
            subaccountId: int = field(init=False),
            subscriberId: int = field(init=False),
            userAccount: str = field(init=False),
            userName: str = field(init=False),
            validityEndTime: int = field(init=False),
            validityStartTime: int = field(init=False),
            vin: str = field(init=False),

        @dataclass
        class VehicleModelConfigurationDTO:
            itemCode: str = field(init=False),
            itemName: str = field(init=False),
            itemValue: str = field(init=False),

        bindTime: int = field(init=False),
        brandName: str = field(init=False),
        colorName: str = field(init=False),
        isActivate: bool = field(init=False),
        isCurrentVehicle: bool = field(init=False),
        isSubaccount: bool = field(init=False),
        modelName: str = field(init=False),
        modelYear: str = field(init=False),
        name: str = field(init=False),
        series: str = field(init=False),
        vin: str = field(init=False),
        subAccountList: List[SubAccountListDTO] = field(default_factory=list)
        vehicleModelConfiguration: List[VehicleModelConfigurationDTO] = field(default_factory=list)

    vinList: List[VinListDTO] = field(default_factory=list)


class AlarmType(Enum):
    ALARM_TYPE_VEHICLE_FAULT = 0
    ALARM_TYPE_GEOFENCE = 2
    ALARM_TYPE_VEHICLE_START = 3


@dataclass
class AlarmSwitchDTO:
    alarmType: int = field(init=False),
    functionSwitch: int = field(init=False),
    alarmSwitch: int = field(init=False),


@dataclass
class AlarmSwitchResp:
    alarmSwitchList: List[AlarmSwitchDTO] = field(default_factory=list)


@dataclass
class AlarmSwitchReq:
    vin: str
    alarmSwitchList: List[AlarmSwitchDTO] = field(default_factory=list)


@dataclass
class BasicVehicleStatusBean:
    batteryVoltage: int = field(init=False),
    bonnetStatus: int = field(init=False),
    bootStatus: int = field(init=False),
    canBusActive: int = field(init=False),
    clstrDspdFuelLvlSgmt: int = field(init=False),
    currentJourneyID: int = field(init=False),
    currentjourneyDistance: int = field(init=False),
    dippedBeamStatus: int = field(init=False),
    driverDoor: int = field(init=False),
    driverWindow: int = field(init=False),
    engineStatus: int = field(init=False),
    extendedData1: int = field(init=False),
    extendedData2: int = field(init=False),
    exteriorTemperature: int = field(init=False),
    frontLeftSeatHeatLevel: int = field(init=False),
    frontLeftTyrePressure: int = field(init=False),
    frontRightSeatHeatLevel: int = field(init=False),
    frontRightTyrePressure: int = field(init=False),
    fuelLevelPrc: int = field(init=False),
    fuelRange: int = field(init=False),
    fuelRangeElec: int = field(init=False),
    handbrake: int = field(init=False),
    interiorTemperature: int = field(init=False),
    lastKeySeen: int = field(init=False),
    lockStatus: int = field(init=False),
    mainBeamStatus: int = field(init=False),
    mileage: int = field(init=False),
    passengerDoor: int = field(init=False),
    passengerWindow: int = field(init=False),
    powerMode: int = field(init=False),
    rearLeftDoor: int = field(init=False),
    rearLeftTyrePressure: int = field(init=False),
    rearLeftWindow: int = field(init=False),
    rearRightDoor: int = field(init=False),
    rearRightTyrePressure: int = field(init=False),
    rearRightWindow: int = field(init=False),
    remoteClimateStatus: int = field(init=False),
    rmtHtdRrWndSt: int = field(init=False),
    sideLightStatus: int = field(init=False),
    sunroofStatus: int = field(init=False),
    timeOfLastCANBUSActivity: int = field(init=False),
    vehElecRngDsp: int = field(init=False),
    vehicleAlarmStatus: int = field(init=False),
    wheelTyreMonitorStatus: int = field(init=False),


@dataclass
class VehicleStatusResp:
    @dataclass
    class ExtendedVehicleStatusDTO:
        alertDataSum: list = field(default_factory=list)

    @dataclass
    class GpsPositionDTO:
        @dataclass
        class WayPointDTO:
            @dataclass
            class PositionDTO:
                altitude: int = field(init=False),
                latitude: int = field(init=False),
                longitude: int = field(init=False),

            hdop: int = field(init=False),
            heading: int = field(init=False),
            position: PositionDTO = field(init=False),
            satellites: int = field(init=False),
            speed: int = field(init=False),

        gpsStatus: int = field(init=False),
        timeStamp: int = field(init=False),
        wayPoint: WayPointDTO = field(init=False),

    basicVehicleStatus: BasicVehicleStatusBean = field(init=False),
    extendedVehicleStatus: ExtendedVehicleStatusDTO = field(init=False),
    gpsPosition: GpsPositionDTO = field(init=False),
    statusTime: int = field(init=False),
