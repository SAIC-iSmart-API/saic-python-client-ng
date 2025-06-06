from __future__ import annotations

import json
import unittest

import dacite

from saic_ismart_client_ng.api.vehicle_charging import ChargingSettingResp


class TestChargingSettingResp(unittest.TestCase):
    def test_rvc_req_sts_decoded(self) -> None:
        sut = ChargingSettingResp(
            rvcReqSts=3,
        )
        assert sut.rvc_req_sts_decoded == b"\x03"

    def test_decode_from_json(self) -> None:
        as_json = '{"imcuDschrgTrgtSOCResp":0,"bmsAltngChrgCrntResp":0,"bmsPackCrnt":20015,"bmsChrgTrgtSOCResp":0,"imcuDschrgTrgtSOCDspCmd":1,"rvcReqSts":3,"bmsOnBdChrgTrgtSOCDspCmd":7,"bmsAltngChrgCrntDspCmd":4,"bmsEstdElecRng":405}'
        as_dict = json.loads(as_json)
        decoded = dacite.from_dict(ChargingSettingResp, as_dict)
        assert decoded.imcuDschrgTrgtSOCResp is not None
        assert decoded.bmsAltngChrgCrntResp is not None
        assert decoded.rvcReqSts == 3
        assert decoded.rvc_req_sts_decoded == b"\x03"


if __name__ == "__main__":
    unittest.main()
