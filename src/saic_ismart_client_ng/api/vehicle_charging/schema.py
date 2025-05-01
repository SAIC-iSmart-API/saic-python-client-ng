from __future__ import annotations

from dataclasses import dataclass
import datetime
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
                raise ValueError(f"Unknown charge current limit: {limit}")

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
                raise ValueError(f"Unknown charge current limit code: {self}")


class BmsChargingStatusCode(Enum):
    UNPLUGGED = 0
    CHARGING_1 = 1  # Potentially AC charging
    CHARGE_DONE = 2
    CHARGING_3 = 3
    CHARGE_FAULT = 4
    CONNECTING = 5
    CONNECTED_NOT_RECOGNIZED = 6
    CONNECTED_NOT_CHARGING = 7
    CHARGING_STOPPED = 8
    SCHEDULED_CHARGING = 9
    CHARGING_10 = 10  # Potentially DC fast charging
    SUPER_OFFBOARD_CHARGING = 11
    CHARGING_12 = 12

    @staticmethod
    def to_code(code: int):
        try:
            return BmsChargingStatusCode(code)
        except ValueError:
            return None


class HeatingStopReason(Enum):
    NO_REASON = 0
    UNKNOWN_1 = 1
    LOW_BATTERY = 2
    REACHED_STOP_CONDITION = 3
    UNNECESSARY = 4
    REACHED_STOP_TIME = 5
    UNKNOWN_6 = 6
    HEATING_SYSTEM_FAILURE = 7

    @staticmethod
    def to_code(code: int):
        try:
            return HeatingStopReason(code)
        except ValueError:
            return None


class ChargingStopReason(Enum):
    NO_REASON = 0
    CHARGER_STATUS_ABNORMAL = 1
    CHARGER_PORT_OVER_TEMPERATURE = 2
    CHARGING_GUN_NOT_PROPERLY_PLUGGED_IN = 3
    CHARGER_VOLTAGE_MISMATCH = 4
    OTHER_REASON = 5

    @staticmethod
    def to_code(code: int):
        try:
            return ChargingStopReason(code)
        except ValueError:
            return ChargingStopReason.OTHER_REASON


class TargetBatteryCode(Enum):
    P_IGNORE = 0
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
                raise ValueError(f"Unknown target battery code: {self}")

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
                raise ValueError(f"Unknown target battery percentage: {percentage}")


@dataclass
class ChargingStatus:
    chargingCurrent: Optional[int] = None
    chargingDuration: Optional[int] = None
    chargingElectricityPhase: Optional[int] = None
    chargingGunState: Optional[int] = None
    chargingPileID: Optional[str] = None
    chargingPileSupplier: Optional[str] = None
    chargingState: Optional[int] = None
    chargingTimeLevelPrc: Optional[int] = None
    chargingType: Optional[int] = None
    chargingVoltage: Optional[int] = None
    endTime: Optional[int] = None
    fotaLowestVoltage: Optional[int] = None
    fuelRangeElec: Optional[int] = None
    lastChargeEndingPower: Optional[int] = None
    mileage: Optional[int] = None
    mileageOfDay: Optional[int] = None
    mileageSinceLastCharge: Optional[int] = None
    powerLevelPrc: Optional[int] = None
    powerUsageOfDay: Optional[int] = None
    powerUsageSinceLastCharge: Optional[int] = None
    realtimePower: Optional[int] = None
    startTime: Optional[int] = None
    staticEnergyConsumption: Optional[int] = None
    totalBatteryCapacity: Optional[int] = None
    workingCurrent: Optional[int] = None
    workingVoltage: Optional[int] = None


@dataclass
class ChargeStatusResp:
    chargingStatus: Optional[ChargingStatus] = None
    gpsPosition: Optional[GpsPosition] = None
    statusTime: Optional[int] = None


@dataclass
class ChrgMgmtData:
    bmsAdpPubChrgSttnDspCmd: Optional[int] = None
    bmsAltngChrgCrntDspCmd: Optional[int] = None
    bmsChrgCtrlDspCmd: Optional[int] = None
    bmsChrgOtptCrntReq: Optional[int] = None
    bmsChrgOtptCrntReqV: Optional[int] = None
    bmsChrgSpRsn: Optional[int] = None
    bmsChrgSts: Optional[int] = None
    bmsDsChrgSpRsn: Optional[int] = None
    bmsEstdElecRng: Optional[int] = None
    bmsOnBdChrgTrgtSOCDspCmd: Optional[int] = None
    bmsPackCrnt: Optional[int] = None
    bmsPackCrntV: Optional[int] = None
    bmsPackSOCDsp: Optional[int] = None
    bmsPackVol: Optional[int] = None
    bmsPTCHeatReqDspCmd: Optional[int] = None
    bmsPTCHeatResp: Optional[int] = None
    bmsPTCHeatSpRsn: Optional[int] = None
    bmsReserCtrlDspCmd: Optional[int] = None
    bmsReserSpHourDspCmd: Optional[int] = None
    bmsReserSpMintueDspCmd: Optional[int] = None
    bmsReserStHourDspCmd: Optional[int] = None
    bmsReserStMintueDspCmd: Optional[int] = None
    ccuEleccLckCtrlDspCmd: Optional[int] = None
    ccuOffBdChrgrPlugOn: Optional[int] = None
    ccuOnbdChrgrPlugOn: Optional[int] = None
    chrgngAddedElecRng: Optional[int] = None
    chrgngAddedElecRngV: Optional[int] = None
    chrgngDoorOpenCnd: Optional[int] = None
    chrgngDoorPosSts: Optional[int] = None
    chrgngRmnngTime: Optional[int] = None
    chrgngRmnngTimeV: Optional[int] = None
    chrgngSpdngTime: Optional[int] = None
    chrgngSpdngTimeV: Optional[int] = None
    clstrElecRngToEPT: Optional[int] = None
    disChrgngRmnngTime: Optional[int] = None
    disChrgngRmnngTimeV: Optional[int] = None
    imcuChrgngEstdElecRng: Optional[int] = None
    imcuChrgngEstdElecRngV: Optional[int] = None
    imcuDschrgngEstdElecRng: Optional[int] = None
    imcuDschrgngEstdElecRngV: Optional[int] = None
    imcuVehElecRng: Optional[int] = None
    imcuVehElecRngV: Optional[int] = None
    onBdChrgrAltrCrntInptCrnt: Optional[int] = None
    onBdChrgrAltrCrntInptVol: Optional[int] = None

    @property
    def decoded_current(self) -> float | None:
        return (
            self.bmsPackCrnt * 0.05 - 1000.0 if self.bmsPackCrnt is not None else None
        )

    @property
    def decoded_voltage(self) -> float | None:
        return self.bmsPackVol * 0.25 if self.bmsPackVol is not None else None

    @property
    def decoded_power(self) -> float | None:
        return (
            self.decoded_current * self.decoded_voltage / 1000.0
            if self.decoded_current is not None and self.decoded_voltage is not None
            else None
        )

    @property
    def charge_target_soc(self) -> Optional[TargetBatteryCode]:
        raw_target_soc = self.bmsOnBdChrgTrgtSOCDspCmd
        try:
            return TargetBatteryCode(raw_target_soc)
        except ValueError:
            return None

    @property
    def charge_current_limit(self) -> Optional[ChargeCurrentLimitCode]:
        raw_charge_current_limit = self.bmsAltngChrgCrntDspCmd
        try:
            return ChargeCurrentLimitCode(raw_charge_current_limit)
        except ValueError:
            return None

    @property
    def is_battery_heating(self) -> bool:
        return self.bmsPTCHeatReqDspCmd == 1

    @property
    def charging_port_locked(self) -> bool:
        return self.ccuEleccLckCtrlDspCmd == 1

    @property
    def is_bms_charging(self) -> bool:
        if self.bmsChrgSts is not None and self.bmsChrgSts in (1, 3, 10, 12):
            return True
        return False

    @property
    def bms_charging_status(self) -> BmsChargingStatusCode | None:
        if self.bmsChrgSts is not None:
            return BmsChargingStatusCode.to_code(self.bmsChrgSts)
        return None

    @property
    def charging_stop_reason(self) -> ChargingStopReason | None:
        if self.bmsChrgSpRsn is not None:
            return ChargingStopReason.to_code(self.bmsChrgSpRsn)
        return None

    @property
    def heating_stop_reason(self) -> HeatingStopReason | None:
        if self.bmsPTCHeatResp is not None:
            return HeatingStopReason.to_code(self.bmsPTCHeatResp)
        return None


@dataclass
class RvsChargeStatus:
    chargingDuration: Optional[int] = None
    chargingElectricityPhase: Optional[int] = None
    chargingGunState: Optional[int] = None
    chargingPileID: Optional[str] = None
    chargingPileSupplier: Optional[str] = None
    chargingType: Optional[int] = None
    endTime: Optional[int] = None
    extendedData1: Optional[int] = None
    extendedData2: Optional[int] = None
    extendedData3: Optional[str] = None
    extendedData4: Optional[str] = None
    fotaLowestVoltage: Optional[int] = None
    fuelRangeElec: Optional[int] = None
    lastChargeEndingPower: Optional[int] = None
    mileage: Optional[int] = None
    mileageOfDay: Optional[int] = None
    mileageSinceLastCharge: Optional[int] = None
    powerUsageOfDay: Optional[int] = None
    powerUsageSinceLastCharge: Optional[int] = None
    realtimePower: Optional[int] = None
    startTime: Optional[int] = None
    staticEnergyConsumption: Optional[int] = None
    totalBatteryCapacity: Optional[int] = None
    workingCurrent: Optional[int] = None
    workingVoltage: Optional[int] = None


@dataclass
class ChrgMgmtDataResp:
    chrgMgmtData: Optional[ChrgMgmtData] = None
    rvsChargeStatus: Optional[RvsChargeStatus] = None


@dataclass
class ChargingSettingRequest:
    altngChrgCrntReq: Optional[int] = None
    onBdChrgTrgtSOCReq: Optional[int] = None
    tboxV2XSpSOCReq: Optional[int] = None
    vin: Optional[str] = None


@dataclass
class ChargingSettingResp:
    bmsAltngChrgCrntDspCmd: Optional[int] = None
    bmsAltngChrgCrntResp: Optional[int] = None
    bmsChrgTrgtSOCResp: Optional[int] = None
    bmsEstdElecRng: Optional[int] = None
    bmsOnBdChrgTrgtSOCDspCmd: Optional[int] = None
    bmsPackCrnt: Optional[int] = None
    imcuDschrgTrgtSOCDspCmd: Optional[int] = None
    imcuDschrgTrgtSOCResp: Optional[int] = None
    rvcReqSts: Optional[str | int] = None

    @property
    def rvc_req_sts_decoded(self) -> Optional[bytes]:
        return decode_bytes(input_value=self.rvcReqSts, field_name="rvcReqSts")

    @property
    def charge_target_soc(self) -> Optional[TargetBatteryCode]:
        raw_target_soc = self.bmsOnBdChrgTrgtSOCDspCmd
        try:
            return TargetBatteryCode(raw_target_soc)
        except ValueError:
            return None

    @property
    def charge_current_limit(self) -> Optional[ChargeCurrentLimitCode]:
        raw_charge_current_limit = self.bmsAltngChrgCrntDspCmd
        try:
            return ChargeCurrentLimitCode(raw_charge_current_limit)
        except ValueError:
            return None

    @property
    def v2x_target_soc(self) -> Optional[TargetBatteryCode]:
        raw_target_soc = self.imcuDschrgTrgtSOCDspCmd
        try:
            return TargetBatteryCode(raw_target_soc)
        except ValueError:
            return None


@dataclass
class ScheduledChargingRequest:
    rsvanSpHour: Optional[int] = None
    rsvanSpMintue: Optional[int] = None
    rsvanStHour: Optional[int] = None
    rsvanStMintue: Optional[int] = None
    tboxAdpPubChrgSttnReq: Optional[int] = None
    tboxReserCtrlReq: Optional[int] = None
    vin: Optional[str] = None


@dataclass
class ScheduledChargingResp:
    bmsAdpPubChrgSttnDspCmd: Optional[int] = None
    bmsReserChrgCtrlResp: Optional[int] = None
    bmsReserCtrlDspCmd: Optional[int] = None
    bmsReserSpHourDspCmd: Optional[int] = None
    bmsReserSpMintueDspCmd: Optional[int] = None
    bmsReserStHourDspCmd: Optional[int] = None
    bmsReserStMintueDspCmd: Optional[int] = None
    rvcReqSts: Optional[str | int] = None

    @property
    def rvc_req_sts_decoded(self) -> Optional[bytes]:
        return decode_bytes(input_value=self.rvcReqSts, field_name="rvcReqSts")


@dataclass
class ChargingPtcHeatRequest:
    ptcHeatReq: Optional[int] = None
    vin: Optional[str] = None


@dataclass
class ChrgPtcHeatResp:
    ptcHeatReqDspCmd: Optional[int] = None
    ptcHeatResp: Optional[int] = None
    rvcReqSts: Optional[str | int] = None

    @property
    def rvc_req_sts_decoded(self) -> Optional[bytes]:
        return decode_bytes(input_value=self.rvcReqSts, field_name="rvcReqSts")

    @property
    def heating_stop_reason(self) -> HeatingStopReason | None:
        if self.ptcHeatResp is not None:
            return HeatingStopReason.to_code(self.ptcHeatResp)
        return None


@dataclass
class ChargingControlRequest:
    chrgCtrlReq: Optional[int] = None
    tboxEleccLckCtrlReq: Optional[int] = None
    tboxV2XReq: Optional[int] = None
    vin: Optional[str] = None


@dataclass
class ChargingControlResp:
    bmsAdpPubChrgSttnDspCmd: Optional[int] = None
    bmsAltngChrgCrntDspCmd: Optional[int] = None
    bmsAltngChrgCrntResp: Optional[int] = None
    bmsChrgCtrlDspCmd: Optional[int] = None
    bmsChrgOtptCrntReq: Optional[int] = None
    bmsChrgOtptCrntReqV: Optional[int] = None
    bmsChrgSpRsn: Optional[int] = None
    bmsChrgSts: Optional[int] = None
    bmsChrgTrgtSOCResp: Optional[int] = None
    bmsDsChrgCtrlDspCmd: Optional[int] = None
    bmsDsChrgCtrlResp: Optional[int] = None
    bmsDsChrgSpRsn: Optional[int] = None
    bmsEstdElecRng: Optional[int] = None
    bmsOnBdChrgTrgtSOCDspCmd: Optional[int] = None
    bmsPTCHeatReqDspCmd: Optional[int] = None
    bmsPTCHeatResp: Optional[int] = None
    bmsPTCHeatSpRsn: Optional[int] = None
    bmsPackCrnt: Optional[int] = None
    bmsPackCrntV: Optional[int] = None
    bmsPackSOCDsp: Optional[int] = None
    bmsPackVol: Optional[int] = None
    bmsReserChrgCtrlResp: Optional[int] = None
    bmsReserCtrlDspCmd: Optional[int] = None
    bmsReserSpHourDspCmd: Optional[int] = None
    bmsReserSpMintueDspCmd: Optional[int] = None
    bmsReserStHourDspCmd: Optional[int] = None
    bmsReserStMintueDspCmd: Optional[int] = None
    ccuEleccLckCtrlDspCmd: Optional[int] = None
    ccuEleccLckCtrlResp: Optional[int] = None
    ccuOffBdChrgrPlugOn: Optional[int] = None
    ccuOnbdChrgrPlugOn: Optional[int] = None
    chrgCtrlDspCmd: Optional[int] = None
    chrgCtrlResp: Optional[int] = None
    chrgngAddedElecRng: Optional[int] = None
    chrgngAddedElecRngV: Optional[int] = None
    chrgngDoorOpenCnd: Optional[int] = None
    chrgngDoorPosSts: Optional[int] = None
    chrgngRmnngTime: Optional[int] = None
    chrgngRmnngTimeV: Optional[int] = None
    chrgngSpdngTime: Optional[int] = None
    chrgngSpdngTimeV: Optional[int] = None
    clstrElecRngToEPT: Optional[int] = None
    disChrgngRmnngTime: Optional[int] = None
    disChrgngRmnngTimeV: Optional[int] = None
    imcuChrgngEstdElecRng: Optional[int] = None
    imcuChrgngEstdElecRngV: Optional[int] = None
    imcuDschrgTrgtSOCDspCmd: Optional[int] = None
    imcuDschrgTrgtSOCResp: Optional[int] = None
    imcuDschrgngEstdElecRng: Optional[int] = None
    imcuDschrgngEstdElecRngV: Optional[int] = None
    imcuVehElecRng: Optional[int] = None
    imcuVehElecRngV: Optional[int] = None
    onBdChrgrAltrCrntInptCrnt: Optional[int] = None
    onBdChrgrAltrCrntInptVol: Optional[int] = None
    rvcReqSts: Optional[str | int] = None

    @property
    def rvc_req_sts_decoded(self) -> Optional[bytes]:
        return decode_bytes(input_value=self.rvcReqSts, field_name="rvcReqSts")

    @property
    def charge_target_soc(self) -> Optional[TargetBatteryCode]:
        raw_target_soc = self.bmsOnBdChrgTrgtSOCDspCmd
        try:
            return TargetBatteryCode(raw_target_soc)
        except ValueError:
            return None

    @property
    def charge_current_limit(self) -> Optional[ChargeCurrentLimitCode]:
        raw_charge_current_limit = self.bmsAltngChrgCrntDspCmd
        try:
            return ChargeCurrentLimitCode(raw_charge_current_limit)
        except ValueError:
            return None

    @property
    def v2x_target_soc(self) -> Optional[TargetBatteryCode]:
        raw_target_soc = self.imcuDschrgTrgtSOCDspCmd
        try:
            return TargetBatteryCode(raw_target_soc)
        except ValueError:
            return None

    @property
    def is_battery_heating(self) -> bool:
        return self.bmsPTCHeatReqDspCmd == 1

    @property
    def charging_port_locked(self) -> bool:
        return self.ccuEleccLckCtrlDspCmd == 1

    @property
    def is_bms_charging(self) -> bool:
        if self.bmsChrgSts is not None and self.bmsChrgSts in (1, 3, 10, 12):
            return True
        return False

    @property
    def bms_charging_status(self) -> BmsChargingStatusCode | None:
        if self.bmsChrgSts is not None:
            return BmsChargingStatusCode.to_code(self.bmsChrgSts)
        return None

    @property
    def charging_stop_reason(self) -> ChargingStopReason | None:
        if self.bmsChrgSpRsn is not None:
            return ChargingStopReason.to_code(self.bmsChrgSpRsn)
        return None

    @property
    def heating_stop_reason(self) -> HeatingStopReason | None:
        if self.bmsPTCHeatResp is not None:
            return HeatingStopReason.to_code(self.bmsPTCHeatResp)
        return None


@dataclass
class ScheduledBatteryHeatingRequest:
    startTime: Optional[int] = None
    status: Optional[int] = None
    vin: Optional[str] = None


@dataclass
class ScheduledBatteryHeatingResp:
    startTime: Optional[int] = None
    status: Optional[int] = None

    @property
    def is_enabled(self) -> bool:
        return self.status == 1

    @property
    def decoded_start_time(self) -> Optional[datetime.time]:
        if self.startTime is None:
            return None
        return datetime.datetime.fromtimestamp(self.startTime / 1000).time()
