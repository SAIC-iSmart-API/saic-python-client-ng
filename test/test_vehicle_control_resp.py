import json
from unittest import TestCase

import dacite

from saic_ismart_client_ng.api.vehicle import VehicleControlResp


class TestVehicleControlResp(TestCase):
    def test_rvc_req_sts_decoded(self):
        sut = VehicleControlResp(
            rvcReqSts='AQ==',
        )
        self.assertEqual(sut.rvc_req_sts_decoded, b'\x01')

    def test_rvc_req_type_decoded(self):
        sut = VehicleControlResp(
            rvcReqType='Bg==',
        )
        self.assertEqual(sut.rvc_req_type_decoded, b'\x06')

    def test_decode_from_json(self):
        as_json = '{"basicVehicleStatus":{"frontRightSeatHeatLevel":0,"steeringWheelHeatFailureReason":0,"rearRightDoor":0,"frontLeftTyrePressure":62,"sideLightStatus":0,"driverWindow":0,"rearRightTyrePressure":63,"rmtHtdRrWndSt":0,"canBusActive":1,"frontRightTyrePressure":62,"driverDoor":0,"lockStatus":1,"frontLeftSeatHeatLevel":0,"powerMode":0,"engineStatus":0,"exteriorTemperature":7,"fuelRange":3240,"extendedData2":0,"currentJourneyId":1237,"extendedData1":79,"mileage":133690,"interiorTemperature":17,"fuelLevelPrc":0,"steeringHeatLevel":0,"batteryVoltage":142,"passengerDoor":0,"clstrDspdFuelLvlSgmt":0,"mainBeamStatus":0,"remoteClimateStatus":2,"vehElecRngDsp":0,"sunroofStatus":0,"currentJourneyDistance":40,"timeOfLastCANBUSActivity":1705953523,"bonnetStatus":0,"bootStatus":0,"fuelRangeElec":3240,"rearRightWindow":0,"lastKeySeen":0,"vehicleAlarmStatus":2,"wheelTyreMonitorStatus":0,"rearLeftTyrePressure":62,"rearLeftDoor":0,"passengerWindow":0,"rearLeftWindow":0,"dippedBeamStatus":0},"gpsPosition":{"timeStamp":1705953524,"gpsStatus":2,"wayPoint":{"satellites":10,"heading":0,"position":{"altitude":115,"latitude":45485072,"longitude":9160267},"hdop":7,"speed":0}},"rvcReqType":"Bg==","failureType":0,"rvcReqSts":"AQ=="}'
        as_dict = json.loads(as_json)
        decoded = dacite.from_dict(VehicleControlResp, as_dict)
        self.assertIsNotNone(decoded.basicVehicleStatus)
        self.assertIsNotNone(decoded.gpsPosition)
        self.assertEqual(decoded.rvcReqType, 'Bg==')
        self.assertEqual(decoded.rvc_req_type_decoded, b'\x06')
        self.assertIsNotNone(decoded.rvcReqSts, 'AQ==')
        self.assertEqual(decoded.rvc_req_sts_decoded, b'\x01')
