import json
import unittest

import dacite

from saic_ismart_client_ng.api.vehicle_charging import ChrgMgmtDataResp


class TestChargeInfoResp(unittest.TestCase):
    def test_decode_from_json(self):
        as_json = '''{
          "chrgMgmtData": {
            "bmsChrgSts": 1,
            "bmsPackVol": 1649,
            "bmsPackCrnt": 19915,
            "bmsChrgSpRsn": 0,
            "bmsPackCrntV": 0,
            "bmsPackSOCDsp": 786,
            "bmsDsChrgSpRsn": 0,
            "bmsEstdElecRng": 358,
            "bmsPTCHeatResp": 0,
            "imcuVehElecRng": 330,
            "chrgngRmnngTime": 29,
            "chrgngSpdngTime": 0,
            "imcuVehElecRngV": 0,
            "chrgngDoorPosSts": 1,
            "chrgngRmnngTimeV": 0,
            "chrgngSpdngTimeV": 0,
            "bmsChrgCtrlDspCmd": 1,
            "chrgngDoorOpenCnd": 0,
            "clstrElecRngToEPT": 330,
            "bmsChrgOtptCrntReq": 107,
            "bmsReserCtrlDspCmd": 1,
            "ccuOnbdChrgrPlugOn": 4,
            "chrgngAddedElecRng": 0,
            "disChrgngRmnngTime": 1023,
            "bmsChrgOtptCrntReqV": 0,
            "bmsPTCHeatReqDspCmd": 2,
            "ccuOffBdChrgrPlugOn": 1,
            "chrgngAddedElecRngV": 0,
            "disChrgngRmnngTimeV": 1,
            "bmsReserSpHourDspCmd": 6,
            "bmsReserStHourDspCmd": 22,
            "ccuEleccLckCtrlDspCmd": 1,
            "imcuChrgngEstdElecRng": 337,
            "bmsAltngChrgCrntDspCmd": 4,
            "bmsReserSpMintueDspCmd": 0,
            "bmsReserStMintueDspCmd": 0,
            "imcuChrgngEstdElecRngV": 0,
            "bmsAdpPubChrgSttnDspCmd": 0,
            "imcuDschrgngEstdElecRng": 337,
            "bmsOnBdChrgTrgtSOCDspCmd": 5,
            "imcuDschrgngEstdElecRngV": 0,
            "onBdChrgrAltrCrntInptVol": 108,
            "onBdChrgrAltrCrntInptCrnt": 47
          },
          "rvsChargeStatus": {
            "endTime": 0,
            "mileage": 161410,
            "startTime": 1710792070,
            "chargingType": 6,
            "mileageOfDay": 0,
            "fuelRangeElec": 3300,
            "realtimePower": 570,
            "workingCurrent": 19915,
            "workingVoltage": 1649,
            "powerUsageOfDay": 0,
            "chargingDuration": 37633,
            "chargingGunState": 1,
            "totalBatteryCapacity": 725,
            "mileageSinceLastCharge": 0,
            "powerUsageSinceLastCharge": 0
          }
        }'''
        as_dict = json.loads(as_json)
        decoded = dacite.from_dict(ChrgMgmtDataResp, as_dict)
        self.assertIsNotNone(decoded)


if __name__ == '__main__':
    unittest.main()
