from __future__ import annotations

import hashlib
import hmac

from saic_ismart_client_ng.india import (
    INDIA_GATEWAY_BASE_URL,
    INDIA_TAP_LOGIN_URL,
    INDIA_TAP_STATUS_URL,
    SaicIndiaApi,
    decode_login_token,
    india_gateway_signature,
    india_tap_signature,
    make_india_device_id,
    normalize_india_phone,
    parse_india_vehicle,
    parse_india_vehicle_status,
)
from saic_ismart_client_ng.india.bitcodec import BitWriter
from saic_ismart_client_ng.india.tap_codec import (
    TAP_RESERVED_SIZE,
    _codec,
    decode_status_response,
    encode_status_request,
)


def test_india_urls_match_mg_india_hosts() -> None:
    assert INDIA_TAP_LOGIN_URL == "https://iov-tap.mgindia.co.in/TAP.Web/ota.mp"
    assert INDIA_TAP_STATUS_URL == "https://iov-tap.mgindia.co.in/TAP.Web/ota.mpv21"
    assert INDIA_GATEWAY_BASE_URL == "https://iov-gateway.mgindia.co.in/api.app/v1"


def test_normalize_india_phone_keeps_last_ten_digits() -> None:
    assert normalize_india_phone("+91 98765 43210") == "9876543210"


def test_india_device_id_is_stable_and_bounded() -> None:
    first = make_india_device_id("9876543210")
    second = make_india_device_id("9876543210")
    assert first == second
    assert first.startswith("saic-ng-india-")
    assert len(first) == 103


def test_tap_signature_uses_body_derived_md5_hmac_key() -> None:
    body = "0123456789ABCDEF"
    key_material = body[1 : len(body) // 2]
    hmac_key = hashlib.md5(key_material.encode()).hexdigest()  # noqa: S324
    expected = hmac.new(hmac_key.encode(), body.encode(), hashlib.sha256).hexdigest()
    assert india_tap_signature(body) == expected


def test_gateway_signature_matches_india_formula() -> None:
    signing_path = "/vehicle/userVinList"
    timestamp = "1700000000000"
    content_type = "application/json"
    key_part_one = hashlib.md5(signing_path.encode()).hexdigest()  # noqa: S324
    encrypt_key = hashlib.md5(  # noqa: S324
        (key_part_one + timestamp + "1" + content_type).encode()
    ).hexdigest()
    hmac_key = hashlib.md5((encrypt_key + timestamp).encode()).hexdigest()  # noqa: S324
    expected = hmac.new(
        hmac_key.encode(),
        (signing_path + timestamp + "1" + content_type).encode(),
        hashlib.sha256,
    ).hexdigest()
    assert india_gateway_signature(signing_path, timestamp, content_type) == expected


def test_build_login_body_contains_framing_and_signature() -> None:
    client = SaicIndiaApi("9876543210", "secret1")
    body = client._build_login_body()
    assert body[4] == "1"
    assert len(body) == int(body[:4], 16)
    assert len(india_tap_signature(body)) == 64


def test_decode_login_token_requires_matching_refresh_token() -> None:
    writer = BitWriter()
    writer.write_bits(0, 6)
    writer.write_7bit_string("A" * 40, 40, 40)
    writer.write_7bit_string("A" * 40, 40, 40)
    assert decode_login_token(writer.to_bytes()) == "A" * 40


def test_encode_status_request_uses_protocol_513() -> None:
    raw = encode_status_request("1" * 50, "2" * 40, "3" * 17, 42)
    payload = bytes.fromhex(raw[5:])
    dispatcher_end = TAP_RESERVED_SIZE + payload[1]
    dispatcher = _codec().decode("MPDispatcherBody", payload[19:dispatcher_end])
    app = _codec().decode("OTARVMVehicleStatusReq", payload[dispatcher_end:])

    assert raw.startswith("1")
    assert dispatcher["applicationID"] == "511"
    assert dispatcher["applicationDataProtocolVersion"] == 513
    assert dispatcher["eventID"] == 42
    assert app == {"vehStatusReqType": 2}


def test_decode_and_parse_india_status_response() -> None:
    status = {
        "statusTime": 1_700_000_000,
        "gpsPosition": {
            "wayPoint": {
                "position": {"latitude": 0, "longitude": 0, "altitude": 0},
                "heading": 0,
                "speed": 0,
                "hdop": 0,
                "satellites": 0,
            },
            "timestamp4Short": {"seconds": 1_700_000_000},
            "gpsStatus": "noGpsSignal",
        },
        "basicVehicleStatus": {
            "driverDoor": False,
            "passengerDoor": False,
            "rearLeftDoor": False,
            "rearRightDoor": False,
            "bootStatus": False,
            "bonnetStatus": False,
            "lockStatus": True,
            "driverWindow": False,
            "passengerWindow": False,
            "rearLeftWindow": False,
            "rearRightWindow": False,
            "sideLightStatus": False,
            "dippedBeamStatus": False,
            "mainBeamStatus": False,
            "engineStatus": 0,
            "powerMode": 0,
            "lastKeySeen": 0,
            "currentJourneyDistance": 0,
            "currentJourneyID": 1,
            "interiorTemperature": 30,
            "exteriorTemperature": 26,
            "fuelLevelPrc": 94,
            "fuelRange": 4040,
            "remoteClimateStatus": 3,
            "canBusActive": False,
            "timeOfLastCANBUSActivity": 1_699_999_999,
            "clstrDspdFuelLvlSgmt": 0,
            "mileage": 49353,
            "batteryVoltage": 140,
            "handBrake": False,
        },
    }
    app = _codec().encode("OTARVMVehicleStatusResp513", status)
    dispatcher = _codec().encode(
        "MPDispatcherBody",
        {
            "applicationID": "511",
            "messageID": 1,
            "eventCreationTime": 1_700_000_000,
            "eventID": 42,
            "applicationDataLength": len(app),
            "applicationDataEncoding": "perUnaligned",
            "applicationDataProtocolVersion": 513,
            "result": 0,
        },
    )
    payload = bytes((33, len(dispatcher) + 3, 0)) + bytes(16) + dispatcher + app
    raw = "1" + f"{len(payload) + 3:04X}" + payload.hex().upper()

    decoded_dispatcher, decoded_status = decode_status_response(raw)
    parsed = parse_india_vehicle_status(decoded_status or {})

    assert decoded_dispatcher["eventID"] == 42
    assert parsed.battery_percent == 94
    assert parsed.range_km == 404.0
    assert parsed.odometer_km == 4935.3
    assert parsed.auxiliary_battery_voltage == 14.0
    assert parsed.locked is True
    assert parsed.climate_running is True


def test_parse_india_vehicle() -> None:
    vehicle = parse_india_vehicle(
        {
            "vin": "VIN123",
            "brandName": "MG",
            "modelName": "Astor",
            "modelYear": "2025",
            "series": "Astor",
            "isActivate": True,
        }
    )
    assert vehicle.vin == "VIN123"
    assert vehicle.model_name == "Astor"
    assert vehicle.is_active is True
