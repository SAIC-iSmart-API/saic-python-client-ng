from dataclasses import dataclass
from enum import Enum
from typing import Optional

from saic_ismart_client_ng.api.schema import GpsPosition
from saic_ismart_client_ng.api.serialization_utils import decode_bytes


class ScheduledChargingMode(Enum):
    DISABLED = 2
    UNTIL_CONFIGURED_SOC = 3
    UNTIL_CONFIGURED_TIME = 1


class ChargeCurrentLimitCode(Enum):
    C_IGNORE = 0
    C_6A = 1
    C_8A = 2
    C_16A = 3
    C_MAX = 4

    @staticmethod
    def to_code(limit: str):
        match limit.upper():
            case "6A":
                return ChargeCurrentLimitCode.C_6A
            case "8A":
                return ChargeCurrentLimitCode.C_8A
            case "16A":
                return ChargeCurrentLimitCode.C_16A
            case "MAX":
                return ChargeCurrentLimitCode.C_MAX
            case _:
                raise ValueError(f'Unknown charge current limit: {limit}')

    @property
    def limit(self) -> str:
        match self:
            case ChargeCurrentLimitCode.C_6A:
                return "6A"
            case ChargeCurrentLimitCode.C_8A:
                return "8A"
            case ChargeCurrentLimitCode.C_16A:
                return "16A"
            case ChargeCurrentLimitCode.C_MAX:
                return "Max"
            case _:
                raise ValueError(f'Unknown charge current limit code: {self}')


class TargetBatteryCode(Enum):
    P_40 = 1
    P_50 = 2
    P_60 = 3
    P_70 = 4
    P_80 = 5
    P_90 = 6
    P_100 = 7

    @property
    def percentage(self) -> int:
        match self:
            case TargetBatteryCode.P_40:
                return 40
            case TargetBatteryCode.P_50:
                return 50
            case TargetBatteryCode.P_60:
                return 60
            case TargetBatteryCode.P_70:
                return 70
            case TargetBatteryCode.P_80:
                return 80
            case TargetBatteryCode.P_90:
                return 90
            case TargetBatteryCode.P_100:
                return 100
            case _:
                raise ValueError(f'Unknown target battery code: {self}')

    @staticmethod
    def from_percentage(percentage: int):
        match percentage:
            case 40:
                return TargetBatteryCode.P_40
            case 50:
                return TargetBatteryCode.P_50
            case 60:
                return TargetBatteryCode.P_60
            case 70:
                return TargetBatteryCode.P_70
            case 80:
                return TargetBatteryCode.P_80
            case 90:
                return TargetBatteryCode.P_90
            case 100:
                return TargetBatteryCode.P_100
            case _:  # default
                raise ValueError(f'Unknown target battery percentage: {percentage}')


@dataclass
class ChargingStatus:
    chargingCurrent: int = None
    chargingDuration: int = None
    chargingElectricityPhase: int = None
    chargingGunState: int = None
    chargingPileID: str = None
    chargingPileSupplier: str = None
    chargingState: int = None
    chargingTimeLevelPrc: int = None
    chargingType: int = None
    chargingVoltage: int = None
    endTime: int = None
    fotaLowestVoltage: int = None
    fuelRangeElec: int = None
    lastChargeEndingPower: int = None
    mileage: int = None
    mileageOfDay: int = None
    mileageSinceLastCharge: int = None
    powerLevelPrc: int = None
    powerUsageOfDay: int = None
    powerUsageSinceLastCharge: int = None
    realtimePower: int = None
    startTime: int = None
    staticEnergyConsumption: int = None
    totalBatteryCapacity: int = None
    workingCurrent: int = None
    workingVoltage: int = None


@dataclass
class ChargeStatusResp:
    chargingStatus: ChargingStatus = None
    gpsPosition: GpsPosition = None
    statusTime: int = None


@dataclass
class ChrgMgmtData:
    bmsAdpPubChrgSttnDspCmd: int = None
    bmsAltngChrgCrntDspCmd: int = None
    bmsChrgCtrlDspCmd: int = None
    bmsChrgOtptCrntReq: int = None
    bmsChrgSpRsn: int = None
    bmsChrgSts: int = None
    bmsEstdElecRng: int = None
    bmsOnBdChrgTrgtSOCDspCmd: int = None
    bmsPTCHeatReqDspCmd: int = None
    bmsPTCHeatResp: int = None
    bmsPTCHeatSpRsn: int = None
    bmsPackCrnt: int = None
    bmsPackSOCDsp: int = None
    bmsPackVol: int = None
    bmsReserCtrlDspCmd: int = None
    bmsReserSpHourDspCmd: int = None
    bmsReserSpMintueDspCmd: int = None
    bmsReserStHourDspCmd: int = None
    bmsReserStMintueDspCmd: int = None
    ccuEleccLckCtrlDspCmd: int = None
    chrgngRmnngTime: int = None
    chrgngRmnngTimeV: int = None
    clstrElecRngToEPT: int = None

    @property
    def decoded_current(self) -> float:
        return self.bmsPackCrnt * 0.05 - 1000.0

    @property
    def decoded_voltage(self) -> float:
        return self.bmsPackVol * 0.25

    @property
    def decoded_power(self) -> float:
        return self.decoded_current * self.decoded_voltage / 1000.0

    @property
    def charge_target_soc(self) -> Optional[TargetBatteryCode]:
        raw_target_soc = self.bmsOnBdChrgTrgtSOCDspCmd
        try:
            return TargetBatteryCode(raw_target_soc)
        except ValueError:
            return None


@dataclass
class RvsChargeStatus:
    chargingDuration: int = None
    chargingElectricityPhase: int = None
    chargingGunState: int = None
    chargingPileSupplier: str = None
    chargingType: int = None
    endTime: int = None
    fotaLowestVoltage: int = None
    fuelRangeElec: int = None
    lastChargeEndingPower: int = None
    mileage: int = None
    mileageOfDay: int = None
    mileageSinceLastCharge: int = None
    powerUsageOfDay: int = None
    powerUsageSinceLastCharge: int = None
    realtimePower: int = None
    startTime: int = None
    staticEnergyConsumption: int = None
    totalBatteryCapacity: int = None
    workingCurrent: int = None
    workingVoltage: int = None


@dataclass
class ChargeInfoResp:
    chrgMgmtData: ChrgMgmtData = None,
    rvsChargeStatus: RvsChargeStatus = None,


@dataclass
class ChargingSettingRequest:
    altngChrgCrntReq: int = None
    onBdChrgTrgtSOCReq: int = None
    tboxV2XSpSOCReq: int = None
    vin: str = None


@dataclass
class ChargingSettingResp:
    bmsAltngChrgCrntDspCmd: int = None
    bmsAltngChrgCrntResp: int = None
    bmsChrgTrgtSOCResp: int = None
    bmsEstdElecRng: int = None
    bmsOnBdChrgTrgtSOCDspCmd: int = None
    bmsPackCrnt: int = None
    imcuDschrgTrgtSOCDspCmd: int = None
    imcuDschrgTrgtSOCResp: int = None
    rvcReqSts: Optional[str | int] = None

    @property
    def rvc_req_sts_decoded(self) -> Optional[bytes]:
        return decode_bytes(input_value=self.rvcReqSts, field_name='rvcReqSts')


@dataclass
class ScheduledChargingRequest:
    rsvanSpHour: int = None
    rsvanSpMintue: int = None
    rsvanStHour: int = None
    rsvanStMintue: int = None
    tboxAdpPubChrgSttnReq: int = None
    tboxReserCtrlReq: int = None
    vin: str = None


@dataclass
class ScheduledChargingResp:
    bmsAdpPubChrgSttnDspCmd: int = None
    bmsReserChrgCtrlResp: int = None
    bmsReserCtrlDspCmd: int = None
    bmsReserSpHourDspCmd: int = None
    bmsReserSpMintueDspCmd: int = None
    bmsReserStHourDspCmd: int = None
    bmsReserStMintueDspCmd: int = None
    rvcReqSts: Optional[str | int] = None

    @property
    def rvc_req_sts_decoded(self) -> Optional[bytes]:
        return decode_bytes(input_value=self.rvcReqSts, field_name='rvcReqSts')


@dataclass
class ChargingPtcHeatRequest:
    ptcHeatReq: int = None
    vin: str = None


@dataclass
class ChrgPtcHeatResp:
    ptcHeatReqDspCmd: int = None
    ptcHeatResp: int = None
    rvcReqSts: Optional[str | int] = None

    @property
    def rvc_req_sts_decoded(self) -> Optional[bytes]:
        return decode_bytes(input_value=self.rvcReqSts, field_name='rvcReqSts')


@dataclass
class ChargingControlRequest:
    chrgCtrlReq: int = None
    tboxEleccLckCtrlReq: int = None
    tboxV2XReq: int = None
    vin: str = None


@dataclass
class ChargingControlResp:
    bmsAdpPubChrgSttnDspCmd: int = None
    bmsAltngChrgCrntDspCmd: int = None
    bmsAltngChrgCrntResp: int = None
    bmsChrgCtrlDspCmd: int = None
    bmsChrgOtptCrntReq: int = None
    bmsChrgOtptCrntReqV: int = None
    bmsChrgSpRsn: int = None
    bmsChrgSts: int = None
    bmsChrgTrgtSOCResp: int = None
    bmsDsChrgCtrlDspCmd: int = None
    bmsDsChrgCtrlResp: int = None
    bmsDsChrgSpRsn: int = None
    bmsEstdElecRng: int = None
    bmsOnBdChrgTrgtSOCDspCmd: int = None
    bmsPTCHeatReqDspCmd: int = None
    bmsPTCHeatResp: int = None
    bmsPTCHeatSpRsn: int = None
    bmsPackCrnt: int = None
    bmsPackCrntV: int = None
    bmsPackSOCDsp: int = None
    bmsPackVol: int = None
    bmsReserChrgCtrlResp: int = None
    bmsReserCtrlDspCmd: int = None
    bmsReserSpHourDspCmd: int = None
    bmsReserSpMintueDspCmd: int = None
    bmsReserStHourDspCmd: int = None
    bmsReserStMintueDspCmd: int = None
    ccuEleccLckCtrlDspCmd: int = None
    ccuEleccLckCtrlResp: int = None
    ccuOffBdChrgrPlugOn: int = None
    ccuOnbdChrgrPlugOn: int = None
    chrgCtrlDspCmd: int = None
    chrgCtrlResp: int = None
    chrgngAddedElecRng: int = None
    chrgngAddedElecRngV: int = None
    chrgngDoorOpenCnd: int = None
    chrgngDoorPosSts: int = None
    chrgngRmnngTime: int = None
    chrgngRmnngTimeV: int = None
    chrgngSpdngTime: int = None
    chrgngSpdngTimeV: int = None
    clstrElecRngToEPT: int = None
    disChrgngRmnngTime: int = None
    disChrgngRmnngTimeV: int = None
    imcuChrgngEstdElecRng: int = None
    imcuChrgngEstdElecRngV: int = None
    imcuDschrgTrgtSOCDspCmd: int = None
    imcuDschrgTrgtSOCResp: int = None
    imcuDschrgngEstdElecRng: int = None
    imcuDschrgngEstdElecRngV: int = None
    imcuVehElecRng: int = None
    imcuVehElecRngV: int = None
    onBdChrgrAltrCrntInptCrnt: int = None
    onBdChrgrAltrCrntInptVol: int = None
    rvcReqSts: Optional[str | int] = None

    @property
    def rvc_req_sts_decoded(self) -> Optional[bytes]:
        return decode_bytes(input_value=self.rvcReqSts, field_name='rvcReqSts')
