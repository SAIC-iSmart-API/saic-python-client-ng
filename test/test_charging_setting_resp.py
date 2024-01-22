import json
from unittest import TestCase

import dacite

from saic_ismart_client_ng.api.vehicle_charging import ChargingSettingResp


class TestChargingSettingResp(TestCase):

    def test_rvc_req_sts_decoded(self):
        sut = ChargingSettingResp(
            rvcReqSts=3,
        )
        self.assertEqual(sut.rvc_req_sts_decoded, b'\x03')

    def test_decode_from_json(self):
        as_json = '{"imcuDschrgTrgtSOCResp":0,"bmsAltngChrgCrntResp":0,"bmsPackCrnt":20015,"bmsChrgTrgtSOCResp":0,"imcuDschrgTrgtSOCDspCmd":1,"rvcReqSts":3,"bmsOnBdChrgTrgtSOCDspCmd":7,"bmsAltngChrgCrntDspCmd":4,"bmsEstdElecRng":405}'
        as_dict = json.loads(as_json)
        decoded = dacite.from_dict(ChargingSettingResp, as_dict)
        self.assertIsNotNone(decoded.imcuDschrgTrgtSOCResp)
        self.assertIsNotNone(decoded.bmsAltngChrgCrntResp)
        self.assertIsNotNone(decoded.rvcReqSts, 3)
        self.assertEqual(decoded.rvc_req_sts_decoded, b'\x03')
