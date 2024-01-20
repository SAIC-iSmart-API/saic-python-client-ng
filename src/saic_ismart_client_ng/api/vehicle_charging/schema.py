from dataclasses import dataclass

from saic_ismart_client_ng.api.schema import GpsPosition


@dataclass
class ChargeStatusResp:
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
    rvcReqSts: int = None


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
    rvcReqSts: int = None


@dataclass
class ChargingPtcHeatRequest:
    ptcHeatReq: int = None
    vin: str = None


@dataclass
class ChrgPtcHeatResp:
    ptcHeatReqDspCmd: int = None
    ptcHeatResp: int = None
    rvcReqSts: int = None


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
    rvcReqSts: int = None
