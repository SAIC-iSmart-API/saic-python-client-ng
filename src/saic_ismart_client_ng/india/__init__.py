from __future__ import annotations

from binascii import unhexlify
from dataclasses import dataclass, field
import hashlib
import hmac
import json
import re
import time
from typing import Any
from urllib.parse import urlencode

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import httpx

from saic_ismart_client_ng.india.bitcodec import (
    BitReader,
    BitWriter,
    read_fixed_7bit_string,
    set_bits,
    set_fixed_7bit_string,
)
from saic_ismart_client_ng.india.tap_codec import (
    IndiaTapError,
    decode_status_response,
    encode_status_request,
)

INDIA_TAP_LOGIN_URL = "https://iov-tap.mgindia.co.in/TAP.Web/ota.mp"
INDIA_TAP_STATUS_URL = "https://iov-tap.mgindia.co.in/TAP.Web/ota.mpv21"
INDIA_GATEWAY_BASE_URL = "https://iov-gateway.mgindia.co.in/api.app/v1"
INDIA_USER_AGENT = "CER_IKE_01/2.3.0 (iPad; iOS 26.3; Scale/2.00)"
LOGIN_DISPATCHER_TEMPLATE_HEX = (
    "11005600882c60c183060c183060c183060c183060c183060c183060c183060c183060c183"
    "060c183060c183060c183060c1ab06200000000020200468acf134468acf1342468acf134"
    "2468acf1342000000000100a0"
)


class SaicIndiaApiException(Exception):
    def __init__(self, message: str, return_code: int | None = None) -> None:
        super().__init__(message)
        self.return_code = return_code


@dataclass(frozen=True)
class IndiaVinInfo:
    vin: str
    brand_name: str | None = None
    model_name: str | None = None
    model_year: str | int | None = None
    series: str | None = None
    is_active: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IndiaVehicleStatus:
    status_time: int | None
    last_vehicle_activity: int | None
    battery_percent: int | None
    range_km: float | None
    odometer_km: float | None
    auxiliary_battery_voltage: float | None
    interior_temperature: int | None
    exterior_temperature: int | None
    locked: bool | None
    driver_door_open: bool | None
    passenger_door_open: bool | None
    rear_left_door_open: bool | None
    rear_right_door_open: bool | None
    boot_open: bool | None
    bonnet_open: bool | None
    driver_window_open: bool | None
    passenger_window_open: bool | None
    rear_left_window_open: bool | None
    rear_right_window_open: bool | None
    climate_running: bool | None
    sunroof_open: bool | None
    can_bus_active: bool | None


class SaicIndiaApi:
    def __init__(
        self,
        phone: str,
        password: str,
        *,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._phone = normalize_india_phone(phone)
        self._password = password
        self._http = http_client or httpx.AsyncClient(timeout=30)
        self._owns_http = http_client is None
        self._token: str | None = None
        self._user_id: str | None = None
        self._device_id = make_india_device_id(self._phone)

    @property
    def token(self) -> str | None:
        return self._token

    @property
    def user_id(self) -> str | None:
        return self._user_id

    async def close(self) -> None:
        if self._owns_http:
            await self._http.aclose()

    async def login(self) -> None:
        body = self._build_login_body()
        response = await self._http.post(
            INDIA_TAP_LOGIN_URL,
            content=body,
            headers={
                "User-Agent": INDIA_USER_AGENT,
                "Content-Type": "text/plain",
                "Accept": "*/*",
                "Accept-Language": "en-US;q=1",
                "APP-SIGNATURE": india_tap_signature(body),
                "SIGNATURE": "1",
            },
        )
        response.raise_for_status()
        dispatcher, app = decode_login_response(response.text)
        if not app:
            raise SaicIndiaApiException("India login did not return a token payload")
        self._token = decode_login_token(app)
        user_id = read_fixed_7bit_string(dispatcher, bit_offset=300, char_count=14)
        self._user_id = user_id.rjust(50, "0")

    async def vehicle_list(self) -> list[IndiaVinInfo]:
        await self._ensure_login()
        payload = await self.gateway_get("/vehicle/userVinList")
        vin_list = payload.get("data", {}).get("vinList", [])
        return [parse_india_vehicle(item) for item in vin_list if isinstance(item, dict)]

    async def get_vehicle_status(self, vin: str) -> IndiaVehicleStatus:
        await self._ensure_login()
        event_id = 0
        for _ in range(6):
            dispatcher, status = await self._status_request(vin, event_id)
            result = dispatcher.get("result", 0)
            if status is not None:
                return parse_india_vehicle_status(status)
            if result not in (0, 4, 6):
                message = dispatcher.get("errorMessage")
                if isinstance(message, bytes):
                    message = message.decode(errors="replace")
                raise SaicIndiaApiException(message or f"India TAP status error {result}", result)
            event_id = dispatcher.get("eventID", event_id)
        raise SaicIndiaApiException("India vehicle status was not ready after polling")

    async def gateway_get(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        await self._ensure_login()
        response = await self._gateway_get_raw(path, params or {})
        parsed = json.loads(decrypt_india_gateway_body(response.text, response.headers))
        if parsed.get("code") == 7:
            await self.login()
            response = await self._gateway_get_raw(path, params or {})
            parsed = json.loads(decrypt_india_gateway_body(response.text, response.headers))
        code = parsed.get("code")
        if code != 0:
            raise SaicIndiaApiException(parsed.get("message", f"India gateway error {code}"), code)
        return parsed

    async def _status_request(self, vin: str, event_id: int) -> tuple[dict[str, Any], dict[str, Any] | None]:
        if self._token is None or self._user_id is None:
            raise SaicIndiaApiException("Not logged in")
        try:
            body = encode_status_request(self._user_id, self._token, vin, event_id)
        except IndiaTapError as err:
            raise SaicIndiaApiException(str(err)) from err
        response = await self._http.post(
            INDIA_TAP_STATUS_URL,
            content=body,
            headers=india_tap_headers(body),
        )
        response.raise_for_status()
        try:
            return decode_status_response(response.text)
        except IndiaTapError as err:
            raise SaicIndiaApiException(str(err)) from err

    async def _gateway_get_raw(self, path: str, params: dict[str, str]) -> httpx.Response:
        if self._token is None or self._user_id is None:
            raise SaicIndiaApiException("Not logged in")
        clean_path = "/" + path.lstrip("/")
        query = urlencode(params)
        signing_path = clean_path + (f"?{query}" if query else "")
        timestamp = str(int(time.time() * 1000))
        content_type = "application/json"
        headers = {
            "User-Agent": INDIA_USER_AGENT,
            "Content-Type": content_type,
            "APP-CONTENT-ENCRYPTED": "1",
            "APP-LANGUAGE-TYPE": "en-us",
            "APP-LOGIN-TOKEN": self._token,
            "APP-USER-ID": self._user_id,
            "APP-SEND-DATE": timestamp,
            "APP-VERIFICATION-STRING": india_gateway_signature(signing_path, timestamp, content_type),
            "ORIGINAL-CONTENT-TYPE": content_type,
        }
        response = await self._http.get(
            f"{INDIA_GATEWAY_BASE_URL}{clean_path}", params=params, headers=headers
        )
        response.raise_for_status()
        return response

    async def _ensure_login(self) -> None:
        if self._token is None or self._user_id is None:
            await self.login()

    def _build_login_body(self) -> str:
        dispatcher = bytearray.fromhex(LOGIN_DISPATCHER_TEMPLATE_HEX)
        app = encode_india_login_app(self._password, self._device_id)
        set_fixed_7bit_string(dispatcher, 48, self._phone.rjust(50, "0"))
        set_bits(dispatcher, 419, 32, int(time.time()))
        dispatcher[-7:-3] = (len(app) * 2).to_bytes(4, "big")
        dispatcher[-3] = 1
        dispatcher[-2:] = (160).to_bytes(2, "big")
        payload = bytes(dispatcher) + app
        raw_without_prefix = "1" + payload.hex().upper()
        return f"{len(raw_without_prefix) + 4:04X}{raw_without_prefix}"


def normalize_india_phone(phone: str) -> str:
    digits = re.sub(r"\D+", "", phone)
    if len(digits) > 10:
        digits = digits[-10:]
    if len(digits) != 10:
        raise SaicIndiaApiException("Phone must contain a 10-digit India mobile number")
    return digits


def make_india_device_id(phone: str) -> str:
    seed = hashlib.sha256(f"mg-ismart-india:{phone}".encode()).hexdigest()
    return (f"saic-ng-india-{seed}" + "0" * 120)[:103]


def encode_india_login_app(password: str, device_id: str) -> bytes:
    writer = BitWriter()
    writer.write_bits(1, 1)
    writer.write_7bit_string(password, 6, 30)
    writer.write_7bit_string(device_id, 1, 200)
    return writer.to_bytes()


def decode_login_response(raw: str) -> tuple[bytes, bytes]:
    if len(raw) < 5 or raw[4] != "1":
        raise SaicIndiaApiException("Unexpected India TAP login response framing")
    payload = bytes.fromhex(raw[5:])
    if len(payload) < 4:
        raise SaicIndiaApiException("India TAP login response is too short")
    dispatcher_len = payload[2] + (payload[3] << 8)
    return payload[:dispatcher_len], payload[dispatcher_len:]


def decode_login_token(app: bytes) -> str:
    reader = BitReader(app)
    reader.read_bits(6)
    token = reader.read_7bit_string(40, 40)
    refresh = reader.read_7bit_string(40, 40)
    if token != refresh:
        raise SaicIndiaApiException("India token and refresh token differ")
    return token


def india_tap_signature(body: str) -> str:
    key_material = body[1 : len(body) // 2]
    hmac_key = hashlib.md5(key_material.encode()).hexdigest()  # noqa: S324
    return hmac.new(hmac_key.encode(), body.encode(), hashlib.sha256).hexdigest()


def india_tap_headers(body: str) -> dict[str, str]:
    return {
        "User-Agent": INDIA_USER_AGENT,
        "Content-Type": "text/plain",
        "Accept": "*/*",
        "APP-SIGNATURE": india_tap_signature(body),
        "SIGNATURE": "1",
    }


def india_gateway_signature(signing_path: str, current_ts: str, content_type: str) -> str:
    key_part_one = md5_hex_digest(signing_path)
    encrypt_key = md5_hex_digest(key_part_one + current_ts + "1" + content_type)
    hmac_value = signing_path + current_ts + "1" + content_type
    hmac_key = md5_hex_digest(encrypt_key + current_ts)
    return hmac.new(hmac_key.encode(), hmac_value.encode(), hashlib.sha256).hexdigest()


def decrypt_india_gateway_body(encrypted: str, headers: httpx.Headers) -> str:
    key = md5_hex_digest(headers["APP-SEND-DATE"] + "1" + headers["ORIGINAL-CONTENT-TYPE"])
    iv = md5_hex_digest(headers["APP-SEND-DATE"])
    cipher = AES.new(unhexlify(key), AES.MODE_CBC, unhexlify(iv))
    return unpad(cipher.decrypt(unhexlify(encrypted)), AES.block_size).decode("utf-8")


def md5_hex_digest(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()  # noqa: S324


def parse_india_vehicle(raw: dict[str, Any]) -> IndiaVinInfo:
    return IndiaVinInfo(
        vin=raw["vin"],
        brand_name=raw.get("brandName"),
        model_name=raw.get("modelName"),
        model_year=raw.get("modelYear"),
        series=raw.get("series"),
        is_active=raw.get("isActivate"),
        raw=raw,
    )


def parse_india_vehicle_status(raw: dict[str, Any]) -> IndiaVehicleStatus:
    basic = raw.get("basicVehicleStatus", {})
    return IndiaVehicleStatus(
        status_time=positive_int(raw.get("statusTime")),
        last_vehicle_activity=positive_int(basic.get("timeOfLastCANBUSActivity")),
        battery_percent=bounded_int(basic.get("fuelLevelPrc"), 0, 100),
        range_km=tenths(basic.get("fuelRange")),
        odometer_km=tenths(basic.get("mileage")),
        auxiliary_battery_voltage=tenths(basic.get("batteryVoltage")),
        interior_temperature=valid_temperature(basic.get("interiorTemperature")),
        exterior_temperature=valid_temperature(basic.get("exteriorTemperature")),
        locked=optional_bool(basic.get("lockStatus")),
        driver_door_open=optional_bool(basic.get("driverDoor")),
        passenger_door_open=optional_bool(basic.get("passengerDoor")),
        rear_left_door_open=optional_bool(basic.get("rearLeftDoor")),
        rear_right_door_open=optional_bool(basic.get("rearRightDoor")),
        boot_open=optional_bool(basic.get("bootStatus")),
        bonnet_open=optional_bool(basic.get("bonnetStatus")),
        driver_window_open=optional_bool(basic.get("driverWindow")),
        passenger_window_open=optional_bool(basic.get("passengerWindow")),
        rear_left_window_open=optional_bool(basic.get("rearLeftWindow")),
        rear_right_window_open=optional_bool(basic.get("rearRightWindow")),
        climate_running=(basic.get("remoteClimateStatus") in (2, 3))
        if basic.get("remoteClimateStatus") is not None
        else None,
        sunroof_open=optional_bool(basic.get("sunroofStatus")),
        can_bus_active=optional_bool(basic.get("canBusActive")),
    )


def positive_int(value: Any) -> int | None:
    return value if isinstance(value, int) and value > 0 else None


def bounded_int(value: Any, minimum: int, maximum: int) -> int | None:
    return value if isinstance(value, int) and minimum <= value <= maximum else None


def tenths(value: Any) -> float | None:
    return round(value / 10, 1) if isinstance(value, int) else None


def valid_temperature(value: Any) -> int | None:
    return value if isinstance(value, int) and value != -128 else None


def optional_bool(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None
