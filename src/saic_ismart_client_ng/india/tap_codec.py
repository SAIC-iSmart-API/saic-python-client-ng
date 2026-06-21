from __future__ import annotations

from functools import lru_cache
import time
from typing import Any

import asn1tools

INDIA_TAP_ASN1 = "MGIndiaTapModule\n\nDEFINITIONS AUTOMATIC TAGS ::= BEGIN\n\nMPDispatcherBody ::= SEQUENCE\n{\n  uid IA5String(SIZE(50)) OPTIONAL,\n  token IA5String(SIZE(40)) OPTIONAL,\n  applicationID IA5String(SIZE(3)),\n  vin IA5String(SIZE(17)) OPTIONAL,\n  messageID INTEGER(0..255),\n  eventCreationTime INTEGER(0..2147483647),\n  eventID INTEGER(0..2147483647) OPTIONAL,\n  ulMessageCounter INTEGER(0..65535) OPTIONAL,\n  dlMessageCounter INTEGER(0..65535) OPTIONAL,\n  ackMessageCounter INTEGER(0..65535) OPTIONAL,\n  ackRequired BOOLEAN OPTIONAL,\n  applicationDataLength INTEGER(0..65535) OPTIONAL,\n  applicationDataEncoding DataEncodingType OPTIONAL,\n  applicationDataProtocolVersion INTEGER(0..65535) OPTIONAL,\n  testFlag INTEGER(1..3) OPTIONAL,\n  result INTEGER(0..65535) OPTIONAL,\n  errorMessage OCTET STRING(SIZE(1..1024)) OPTIONAL\n}\n\nDataEncodingType ::= ENUMERATED { perUnaligned(0), der(1), ber(2) }\n\nOTARVMVehicleStatusReq ::= SEQUENCE { vehStatusReqType INTEGER(0..255) }\n\nOTARVMVehicleStatusResp513 ::= SEQUENCE\n{\n  statusTime INTEGER(0..2147483647),\n  gpsPosition RvsPosition,\n  basicVehicleStatus RvsBasicStatus513,\n  extendedVehicleStatus RvsExtStatus OPTIONAL\n}\n\nRvsPosition ::= SEQUENCE\n{\n  wayPoint RvsWayPoint,\n  timestamp4Short Timestamp4Short,\n  gpsStatus GPSStatus\n}\n\nRvsWayPoint ::= SEQUENCE\n{\n  position RvsWGS84Point,\n  heading INTEGER(0..359),\n  speed INTEGER(-1000..4500),\n  hdop INTEGER(0..1000),\n  satellites INTEGER(0..16)\n}\n\nRvsWGS84Point ::= SEQUENCE\n{\n  latitude INTEGER(-90000000..90000000),\n  longitude INTEGER(-180000000..180000000),\n  altitude INTEGER(-100..8900)\n}\n\nTimestamp4Short ::= SEQUENCE { seconds INTEGER(0..2147483647) }\nGPSStatus ::= ENUMERATED { noGpsSignal(0), timeFix(1), fix2D(2), fix3D(3) }\n\nRvsBasicStatus513 ::= SEQUENCE\n{\n  driverDoor BOOLEAN,\n  passengerDoor BOOLEAN,\n  rearLeftDoor BOOLEAN,\n  rearRightDoor BOOLEAN,\n  bootStatus BOOLEAN,\n  bonnetStatus BOOLEAN,\n  lockStatus BOOLEAN,\n  driverWindow BOOLEAN OPTIONAL,\n  passengerWindow BOOLEAN OPTIONAL,\n  rearLeftWindow BOOLEAN OPTIONAL,\n  rearRightWindow BOOLEAN OPTIONAL,\n  sunroofStatus BOOLEAN OPTIONAL,\n  frontRrightTyrePressure INTEGER(0..255) OPTIONAL,\n  frontLeftTyrePressure INTEGER(0..255) OPTIONAL,\n  rearRightTyrePressure INTEGER(0..255) OPTIONAL,\n  rearLeftTyrePressure INTEGER(0..255) OPTIONAL,\n  wheelTyreMonitorStatus INTEGER(0..255) OPTIONAL,\n  sideLightStatus BOOLEAN,\n  dippedBeamStatus BOOLEAN,\n  mainBeamStatus BOOLEAN,\n  vehicleAlarmStatus INTEGER(0..255) OPTIONAL,\n  engineStatus INTEGER(0..255),\n  powerMode INTEGER(0..255),\n  lastKeySeen INTEGER(0..65535),\n  currentJourneyDistance INTEGER(0..65535),\n  currentJourneyID INTEGER(0..2147483647),\n  interiorTemperature INTEGER(-128..127),\n  exteriorTemperature INTEGER(-128..127),\n  fuelLevelPrc INTEGER(0..255),\n  fuelRange INTEGER(0..65535),\n  remoteClimateStatus INTEGER(0..255),\n  frontLeftSeatHeatLevel INTEGER(0..255) OPTIONAL,\n  frontRightSeatHeatLevel INTEGER(0..255) OPTIONAL,\n  canBusActive BOOLEAN,\n  timeOfLastCANBUSActivity INTEGER(0..2147483647),\n  clstrDspdFuelLvlSgmt INTEGER(0..255),\n  mileage INTEGER(0..2147483647),\n  batteryVoltage INTEGER(0..65535),\n  extendedData1 INTEGER(0..2147483647) OPTIONAL,\n  extendedData2 INTEGER(0..2147483647) OPTIONAL,\n  handBrake BOOLEAN\n}\n\nRvsExtStatus ::= SEQUENCE { vehicleAlerts SEQUENCE SIZE(0..64) OF VehicleAlertInfo }\nVehicleAlertInfo ::= SEQUENCE { id INTEGER(0..255), value INTEGER(0..255) }\n\nEND\n"

TAP_PROTOCOL_VERSION = 33
TAP_RESERVED_SIZE = 16
STATUS_APPLICATION_ID = "511"
STATUS_APPLICATION_PROTOCOL = 513


class IndiaTapError(ValueError):
    pass


@lru_cache(maxsize=1)
def _codec() -> Any:
    return asn1tools.compile_string(INDIA_TAP_ASN1, "uper")


def encode_status_request(uid: str, token: str, vin: str, event_id: int) -> str:
    app = _codec().encode("OTARVMVehicleStatusReq", {"vehStatusReqType": 2})
    body = _codec().encode(
        "MPDispatcherBody",
        {
            "uid": uid,
            "token": token,
            "applicationID": STATUS_APPLICATION_ID,
            "vin": vin,
            "messageID": 1,
            "eventCreationTime": int(time.time()),
            "eventID": event_id,
            "ulMessageCounter": 0,
            "dlMessageCounter": 0,
            "ackMessageCounter": 0,
            "ackRequired": False,
            "applicationDataLength": len(app),
            "applicationDataEncoding": "perUnaligned",
            "applicationDataProtocolVersion": STATUS_APPLICATION_PROTOCOL,
            "testFlag": 2,
            "result": 0,
        },
    )
    dispatcher_length = len(body) + 3
    if dispatcher_length > 255:
        raise IndiaTapError("TAP dispatcher is too large")
    payload = (
        bytes((TAP_PROTOCOL_VERSION, dispatcher_length, 0))
        + bytes(TAP_RESERVED_SIZE)
        + body
        + app
    )
    return "1" + f"{len(payload) + 3:04X}" + payload.hex().upper()


def decode_status_response(raw: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    dispatcher, app = _decode_v21_response(raw)
    if app is None:
        return dispatcher, None
    try:
        status = _codec().decode("OTARVMVehicleStatusResp513", app)
    except Exception as err:
        raise IndiaTapError("Unable to decode India TAP vehicle status") from err
    return dispatcher, status


def _decode_v21_response(raw: str) -> tuple[dict[str, Any], bytes | None]:
    if len(raw) < 5 or raw[0] != "1":
        raise IndiaTapError("Unexpected India TAP v2.1 response framing")
    try:
        payload = bytes.fromhex(raw[5:])
    except ValueError as err:
        raise IndiaTapError("India TAP v2.1 response is not hexadecimal") from err
    if len(payload) < 19:
        raise IndiaTapError("India TAP v2.1 response is too short")
    dispatcher_length = payload[1]
    dispatcher_end = TAP_RESERVED_SIZE + dispatcher_length
    if dispatcher_length < 3 or dispatcher_end > len(payload):
        raise IndiaTapError("Invalid India TAP v2.1 dispatcher length")
    try:
        dispatcher = _codec().decode("MPDispatcherBody", payload[19:dispatcher_end])
    except Exception as err:
        raise IndiaTapError("Unable to decode India TAP v2.1 dispatcher") from err
    app_length = dispatcher.get("applicationDataLength", 0)
    if not app_length:
        return dispatcher, None
    app = payload[dispatcher_end : dispatcher_end + app_length]
    if len(app) != app_length:
        raise IndiaTapError("Truncated India TAP v2.1 application data")
    return dispatcher, app
