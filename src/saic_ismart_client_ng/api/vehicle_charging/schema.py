from __future__ import annotations

from dataclasses import dataclass
import datetime
from enum import Enum
from typing import TYPE_CHECKING

from saic_ismart_client_ng.api.serialization_utils import decode_bytes

if TYPE_CHECKING:
    from saic_ismart_client_ng.api.schema import GpsPosition


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
    def to_code(limit: str) -> ChargeCurrentLimitCode:
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
                msg = f"Unknown charge current limit: {limit}"
                raise ValueError(msg)

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
                msg = f"Unknown charge current limit code: {self}"
                raise ValueError(msg)


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
    def to_code(code: int) -> BmsChargingStatusCode | None:
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
    def to_code(code: int) -> HeatingStopReason | None:
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
    def to_code(code: int) -> ChargingStopReason:
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
    # pylint: disable=too-many-return-statements
    def percentage(self) -> int:  # noqa: PLR0911
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
                msg = f"Unknown target battery code: {self}"
                raise ValueError(msg)

    @staticmethod
    # pylint: disable=too-many-return-statements
    def from_percentage(percentage: int) -> TargetBatteryCode:  # noqa: PLR0911
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
                msg = f"Unknown target battery percentage: {percentage}"
                raise ValueError(msg)


@dataclass
class ChargingStatus:
    chargingCurrent: int | None = None
    chargingDuration: int | None = None
    chargingElectricityPhase: int | None = None
    chargingGunState: int | None = None
    chargingPileID: str | None = None
    chargingPileSupplier: str | None = None
    chargingState: int | None = None
    chargingTimeLevelPrc: int | None = None
    chargingType: int | None = None
    chargingVoltage: int | None = None
    endTime: int | None = None
    fotaLowestVoltage: int | None = None
    fuelRangeElec: int | None = None
    lastChargeEndingPower: int | None = None
    mileage: int | None = None
    mileageOfDay: int | None = None
    mileageSinceLastCharge: int | None = None
    powerLevelPrc: int | None = None
    powerUsageOfDay: int | None = None
    powerUsageSinceLastCharge: int | None = None
    realtimePower: int | None = None
    startTime: int | None = None
    staticEnergyConsumption: int | None = None
    totalBatteryCapacity: int | None = None
    workingCurrent: int | None = None
    workingVoltage: int | None = None


@dataclass
class ChargeStatusResp:
    # pylint: disable=import-outside-toplevel
    from saic_ismart_client_ng.api.schema import GpsPosition

    chargingStatus: ChargingStatus | None = None
    gpsPosition: GpsPosition | None = None
    statusTime: int | None = None


@dataclass
class ChrgMgmtData:
    bmsAdpPubChrgSttnDspCmd: int | None = None
    bmsAltngChrgCrntDspCmd: int | None = None
    bmsChrgCtrlDspCmd: int | None = None
    bmsChrgOtptCrntReq: int | None = None
    bmsChrgOtptCrntReqV: int | None = None
    bmsChrgSpRsn: int | None = None
    bmsChrgSts: int | None = None
    bmsDsChrgSpRsn: int | None = None
    bmsEstdElecRng: int | None = None
    bmsOnBdChrgTrgtSOCDspCmd: int | None = None
    bmsPackCrnt: int | None = None
    bmsPackCrntV: int | None = None
    bmsPackSOCDsp: int | None = None
    bmsPackVol: int | None = None
    bmsPTCHeatReqDspCmd: int | None = None
    bmsPTCHeatResp: int | None = None
    bmsPTCHeatSpRsn: int | None = None
    bmsReserCtrlDspCmd: int | None = None
    bmsReserSpHourDspCmd: int | None = None
    bmsReserSpMintueDspCmd: int | None = None
    bmsReserStHourDspCmd: int | None = None
    bmsReserStMintueDspCmd: int | None = None
    ccuEleccLckCtrlDspCmd: int | None = None
    ccuOffBdChrgrPlugOn: int | None = None
    ccuOnbdChrgrPlugOn: int | None = None
    chrgngAddedElecRng: int | None = None
    chrgngAddedElecRngV: int | None = None
    chrgngDoorOpenCnd: int | None = None
    chrgngDoorPosSts: int | None = None
    chrgngRmnngTime: int | None = None
    chrgngRmnngTimeV: int | None = None
    chrgngSpdngTime: int | None = None
    chrgngSpdngTimeV: int | None = None
    clstrElecRngToEPT: int | None = None
    disChrgngRmnngTime: int | None = None
    disChrgngRmnngTimeV: int | None = None
    imcuChrgngEstdElecRng: int | None = None
    imcuChrgngEstdElecRngV: int | None = None
    imcuDschrgngEstdElecRng: int | None = None
    imcuDschrgngEstdElecRngV: int | None = None
    imcuVehElecRng: int | None = None
    imcuVehElecRngV: int | None = None
    onBdChrgrAltrCrntInptCrnt: int | None = None
    onBdChrgrAltrCrntInptVol: int | None = None

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
    def charge_target_soc(self) -> TargetBatteryCode | None:
        raw_target_soc = self.bmsOnBdChrgTrgtSOCDspCmd
        try:
            return TargetBatteryCode(raw_target_soc)
        except ValueError:
            return None

    @property
    def charge_current_limit(self) -> ChargeCurrentLimitCode | None:
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
        return bool(self.bmsChrgSts is not None and self.bmsChrgSts in (1, 3, 10, 12))

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
    chargingDuration: int | None = None
    chargingElectricityPhase: int | None = None
    chargingGunState: int | None = None
    chargingPileID: str | None = None
    chargingPileSupplier: str | None = None
    chargingType: int | None = None
    endTime: int | None = None
    extendedData1: int | None = None
    extendedData2: int | None = None
    extendedData3: str | None = None
    extendedData4: str | None = None
    fotaLowestVoltage: int | None = None
    fuelRangeElec: int | None = None
    lastChargeEndingPower: int | None = None
    mileage: int | None = None
    mileageOfDay: int | None = None
    mileageSinceLastCharge: int | None = None
    powerUsageOfDay: int | None = None
    powerUsageSinceLastCharge: int | None = None
    realtimePower: int | None = None
    startTime: int | None = None
    staticEnergyConsumption: int | None = None
    totalBatteryCapacity: int | None = None
    workingCurrent: int | None = None
    workingVoltage: int | None = None


@dataclass
class ChrgMgmtDataResp:
    chrgMgmtData: ChrgMgmtData | None = None
    rvsChargeStatus: RvsChargeStatus | None = None


@dataclass
class ChargingSettingRequest:
    altngChrgCrntReq: int | None = None
    onBdChrgTrgtSOCReq: int | None = None
    tboxV2XSpSOCReq: int | None = None
    vin: str | None = None


@dataclass
class ChargingSettingResp:
    bmsAltngChrgCrntDspCmd: int | None = None
    bmsAltngChrgCrntResp: int | None = None
    bmsChrgTrgtSOCResp: int | None = None
    bmsEstdElecRng: int | None = None
    bmsOnBdChrgTrgtSOCDspCmd: int | None = None
    bmsPackCrnt: int | None = None
    imcuDschrgTrgtSOCDspCmd: int | None = None
    imcuDschrgTrgtSOCResp: int | None = None
    rvcReqSts: str | int | None = None

    @property
    def rvc_req_sts_decoded(self) -> bytes | None:
        return decode_bytes(input_value=self.rvcReqSts, field_name="rvcReqSts")

    @property
    def charge_target_soc(self) -> TargetBatteryCode | None:
        raw_target_soc = self.bmsOnBdChrgTrgtSOCDspCmd
        try:
            return TargetBatteryCode(raw_target_soc)
        except ValueError:
            return None

    @property
    def charge_current_limit(self) -> ChargeCurrentLimitCode | None:
        raw_charge_current_limit = self.bmsAltngChrgCrntDspCmd
        try:
            return ChargeCurrentLimitCode(raw_charge_current_limit)
        except ValueError:
            return None

    @property
    def v2x_target_soc(self) -> TargetBatteryCode | None:
        raw_target_soc = self.imcuDschrgTrgtSOCDspCmd
        try:
            return TargetBatteryCode(raw_target_soc)
        except ValueError:
            return None


@dataclass
class ScheduledChargingRequest:
    rsvanSpHour: int | None = None
    rsvanSpMintue: int | None = None
    rsvanStHour: int | None = None
    rsvanStMintue: int | None = None
    tboxAdpPubChrgSttnReq: int | None = None
    tboxReserCtrlReq: int | None = None
    vin: str | None = None


@dataclass
class ScheduledChargingResp:
    bmsAdpPubChrgSttnDspCmd: int | None = None
    bmsReserChrgCtrlResp: int | None = None
    bmsReserCtrlDspCmd: int | None = None
    bmsReserSpHourDspCmd: int | None = None
    bmsReserSpMintueDspCmd: int | None = None
    bmsReserStHourDspCmd: int | None = None
    bmsReserStMintueDspCmd: int | None = None
    rvcReqSts: str | int | None = None

    @property
    def rvc_req_sts_decoded(self) -> bytes | None:
        return decode_bytes(input_value=self.rvcReqSts, field_name="rvcReqSts")


@dataclass
class ChargingPtcHeatRequest:
    ptcHeatReq: int | None = None
    vin: str | None = None


@dataclass
class ChrgPtcHeatResp:
    ptcHeatReqDspCmd: int | None = None
    ptcHeatResp: int | None = None
    rvcReqSts: str | int | None = None

    @property
    def rvc_req_sts_decoded(self) -> bytes | None:
        return decode_bytes(input_value=self.rvcReqSts, field_name="rvcReqSts")

    @property
    def heating_stop_reason(self) -> HeatingStopReason | None:
        if self.ptcHeatResp is not None:
            return HeatingStopReason.to_code(self.ptcHeatResp)
        return None


@dataclass
class ChargingControlRequest:
    chrgCtrlReq: int | None = None
    tboxEleccLckCtrlReq: int | None = None
    tboxV2XReq: int | None = None
    vin: str | None = None


@dataclass
class ChargingControlResp:
    bmsAdpPubChrgSttnDspCmd: int | None = None
    bmsAltngChrgCrntDspCmd: int | None = None
    bmsAltngChrgCrntResp: int | None = None
    bmsChrgCtrlDspCmd: int | None = None
    bmsChrgOtptCrntReq: int | None = None
    bmsChrgOtptCrntReqV: int | None = None
    bmsChrgSpRsn: int | None = None
    bmsChrgSts: int | None = None
    bmsChrgTrgtSOCResp: int | None = None
    bmsDsChrgCtrlDspCmd: int | None = None
    bmsDsChrgCtrlResp: int | None = None
    bmsDsChrgSpRsn: int | None = None
    bmsEstdElecRng: int | None = None
    bmsOnBdChrgTrgtSOCDspCmd: int | None = None
    bmsPTCHeatReqDspCmd: int | None = None
    bmsPTCHeatResp: int | None = None
    bmsPTCHeatSpRsn: int | None = None
    bmsPackCrnt: int | None = None
    bmsPackCrntV: int | None = None
    bmsPackSOCDsp: int | None = None
    bmsPackVol: int | None = None
    bmsReserChrgCtrlResp: int | None = None
    bmsReserCtrlDspCmd: int | None = None
    bmsReserSpHourDspCmd: int | None = None
    bmsReserSpMintueDspCmd: int | None = None
    bmsReserStHourDspCmd: int | None = None
    bmsReserStMintueDspCmd: int | None = None
    ccuEleccLckCtrlDspCmd: int | None = None
    ccuEleccLckCtrlResp: int | None = None
    ccuOffBdChrgrPlugOn: int | None = None
    ccuOnbdChrgrPlugOn: int | None = None
    chrgCtrlDspCmd: int | None = None
    chrgCtrlResp: int | None = None
    chrgngAddedElecRng: int | None = None
    chrgngAddedElecRngV: int | None = None
    chrgngDoorOpenCnd: int | None = None
    chrgngDoorPosSts: int | None = None
    chrgngRmnngTime: int | None = None
    chrgngRmnngTimeV: int | None = None
    chrgngSpdngTime: int | None = None
    chrgngSpdngTimeV: int | None = None
    clstrElecRngToEPT: int | None = None
    disChrgngRmnngTime: int | None = None
    disChrgngRmnngTimeV: int | None = None
    imcuChrgngEstdElecRng: int | None = None
    imcuChrgngEstdElecRngV: int | None = None
    imcuDschrgTrgtSOCDspCmd: int | None = None
    imcuDschrgTrgtSOCResp: int | None = None
    imcuDschrgngEstdElecRng: int | None = None
    imcuDschrgngEstdElecRngV: int | None = None
    imcuVehElecRng: int | None = None
    imcuVehElecRngV: int | None = None
    onBdChrgrAltrCrntInptCrnt: int | None = None
    onBdChrgrAltrCrntInptVol: int | None = None
    rvcReqSts: str | int | None = None

    @property
    def rvc_req_sts_decoded(self) -> bytes | None:
        return decode_bytes(input_value=self.rvcReqSts, field_name="rvcReqSts")

    @property
    def charge_target_soc(self) -> TargetBatteryCode | None:
        raw_target_soc = self.bmsOnBdChrgTrgtSOCDspCmd
        try:
            return TargetBatteryCode(raw_target_soc)
        except ValueError:
            return None

    @property
    def charge_current_limit(self) -> ChargeCurrentLimitCode | None:
        raw_charge_current_limit = self.bmsAltngChrgCrntDspCmd
        try:
            return ChargeCurrentLimitCode(raw_charge_current_limit)
        except ValueError:
            return None

    @property
    def v2x_target_soc(self) -> TargetBatteryCode | None:
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
        return bool(self.bmsChrgSts is not None and self.bmsChrgSts in (1, 3, 10, 12))

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
    startTime: int | None = None
    status: int | None = None
    vin: str | None = None


@dataclass
class ScheduledBatteryHeatingResp:
    startTime: int | None = None
    status: int | None = None

    @property
    def is_enabled(self) -> bool:
        return self.status == 1

    @property
    def decoded_start_time(self) -> datetime.time | None:
        if self.startTime is None:
            return None
        return datetime.datetime.fromtimestamp(self.startTime / 1000).time()
