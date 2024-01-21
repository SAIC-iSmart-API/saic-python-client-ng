import datetime
import json
from calendar import JANUARY
from unittest import TestCase

import dacite

from saic_ismart_client_ng.api.message import MessageResp


class TestDecodeMessages(TestCase):
    def test_it_should_work_with_messageId_as_number(self):
        msg = '{"code":0,"data":{"messages":[{"readStatus":0,"messageTime":"21-01-2024 17:42:14","messageType":"323","sender":"TBOX","messageId":22233425,"vin":"LSJWHXXXXXXXXXXXX","title":"Vehicle Start","content":"The vehicle(***XXX) starts on 21-01-2024 17:42:14 GMT+01:00, please confirm that you know it."},{"readStatus":0,"messageTime":"21-01-2024 17:07:21","messageType":"323","sender":"TBOX","messageId":22230622,"vin":"LSJWHXXXXXXXXXXXX","title":"Vehicle Start","content":"The vehicle(***XXX) starts on 21-01-2024 17:07:20 GMT+01:00, please confirm that you know it."},{"readStatus":1,"messageTime":"31-12-2023 19:42:07","messageType":"801","sender":"TBOX","messageId":20127429,"vin":"LSJWHXXXXXXXXXXXX","contentIdList":[{"contentId":26}],"title":"Electric power steering warning","content":"Your vehicle (***XXX) status is abnormal, please go to vehicle status for details."}],"recordsNumber":3},"message":"success"}'
        msg_as_json = json.loads(msg)
        decoded = dacite.from_dict(MessageResp, msg_as_json['data'])
        self.assertEqual(decoded.recordsNumber, 3)
        self.assertEqual(len(decoded.messages), 3)
        self.assertEqual(decoded.messages[0].messageId, 22233425)
        self.assertEqual(
            decoded.messages[0].message_time,
            datetime.datetime(year=2024, month=JANUARY, day=21, hour=17, minute=42, second=14)
        )

    def test_it_should_work_with_messageId_as_string(self):
        msg = '{"code":0,"data":{"messages":[{"readStatus":0,"messageTime":"21-01-2024 17:42:14","messageType":"323","sender":"TBOX","messageId":"22233425","vin":"LSJWHXXXXXXXXXXXX","title":"Vehicle Start","content":"The vehicle(***XXX) starts on 21-01-2024 17:42:14 GMT+01:00, please confirm that you know it."},{"readStatus":0,"messageTime":"21-01-2024 17:07:21","messageType":"323","sender":"TBOX","messageId":22230622,"vin":"LSJWHXXXXXXXXXXXX","title":"Vehicle Start","content":"The vehicle(***XXX) starts on 21-01-2024 17:07:20 GMT+01:00, please confirm that you know it."},{"readStatus":1,"messageTime":"31-12-2023 19:42:07","messageType":"801","sender":"TBOX","messageId":20127429,"vin":"LSJWHXXXXXXXXXXXX","contentIdList":[{"contentId":26}],"title":"Electric power steering warning","content":"Your vehicle (***XXX) status is abnormal, please go to vehicle status for details."}],"recordsNumber":3},"message":"success"}'
        msg_as_json = json.loads(msg)
        decoded = dacite.from_dict(MessageResp, msg_as_json['data'])
        self.assertEqual(decoded.messages[0].messageId, "22233425")
