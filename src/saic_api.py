from dataclasses import asdict
from typing import Type, T, Optional, Any

import dacite
import httpx
import tenacity
from httpx._types import QueryParamTypes, HeaderTypes

from _net.client.api import SaicApiClient
from _net.client.login import SaicLoginClient
from crypto_utils import sha1_hex_digest, sha256_hex_digest
from exceptions import SaicApiException
from model import SaicApiConfiguration
from schema import LoginResp, VehicleListResp, AlarmSwitchResp, AlarmSwitchReq


class SaicApi:
    def __init__(
            self,
            configuration: SaicApiConfiguration,
    ):
        self.__configuration = configuration
        self.__login_client = SaicLoginClient(configuration)
        self.__api_client = SaicApiClient(configuration)

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(1),
        retry=tenacity.retry_if_not_exception_type(SaicApiException),
    )
    async def login(self) -> LoginResp:
        # Example usage
        url = f"{self.__configuration.base_uri}oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        firebase_device_id = "cqSHOMG1SmK4k-fzAeK6hr:APA91bGtGihOG5SEQ9hPx3Dtr9o9mQguNiKZrQzboa-1C_UBlRZYdFcMmdfLvh9Q_xA8A0dGFIjkMhZbdIXOYnKfHCeWafAfLXOrxBS3N18T4Slr-x9qpV6FHLMhE9s7I6s89k9lU7DD"
        form_body = {
            "grant_type": "password",
            "username": self.__configuration.username,
            "password": sha1_hex_digest(self.__configuration.password),
            "scope": "all",
            "deviceId": f"{firebase_device_id}###europecar",
            "deviceType": "1",  # 2 for huawei
            "loginType": "2" if self.__configuration.username_is_email else "1",
            "countryCode": "" if self.__configuration.username_is_email else self.__configuration.phone_country_code,
        }

        req = httpx.Request("POST", url, data=form_body, headers=headers)
        response = await self.__login_client.client.send(req)
        result = self.__deserialize(response, LoginResp)
        # Update the user token
        self.__api_client.user_token = result.access_token
        return result

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(1),
        retry=tenacity.retry_if_not_exception_type(SaicApiException),
    )
    async def vehicle_list(self) -> VehicleListResp:
        return await self.__api_call("GET", "/vehicle/list", out_type=VehicleListResp)

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(1),
        retry=tenacity.retry_if_not_exception_type(SaicApiException),
    )
    async def get_alarm_switch(self, vin) -> AlarmSwitchResp:
        return await self.__api_call(
            "GET",
            "/vehicle/alarmSwitch",
            out_type=AlarmSwitchResp,
            params={"vin": sha256_hex_digest(vin)}
        )

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(1),
        retry=tenacity.retry_if_not_exception_type(SaicApiException),
    )
    async def set_alarm_switch(self, body: AlarmSwitchReq, vin: str) -> None:
        body.vin = sha256_hex_digest(vin)
        return await self.__api_call("PUT", "/vehicle/alarmSwitch", body=body)

    async def __api_call(
            self,
            method: str,
            path: str,
            body: Optional[Any] = None,
            out_type: Optional[Type[T]] = None,
            params: Optional[QueryParamTypes] = None,
            headers: Optional[HeaderTypes] = None,
    ) -> Optional[T]:
        url = f"{self.__configuration.base_uri}{path[1:] if path.startswith('/') else path}"
        json_body = asdict(body) if body else None
        req = httpx.Request(method, url, params=params, headers=headers, json=json_body)
        response = await self.__api_client.client.send(req)
        return self.__deserialize(response, out_type)

    @staticmethod
    def __deserialize(response: httpx.Response, data_class: Optional[Type[T]]) -> Optional[T]:
        try:
            json_data = response.json()
            return_code = json_data.get('code', -1)

            if return_code != 0:
                raise SaicApiException(json_data.get('message', 'Unknown error'), return_code=return_code)

            if data_class is None:
                return None
            elif 'data' in json_data:
                return dacite.from_dict(data_class, json_data['data'])
            else:
                raise SaicApiException(f"Failed to deserialize response, missing data field: {json_data}")

        except SaicApiException as se:
            raise se
        except Exception as e:
            raise SaicApiException(f"Failed to deserialize response: {e}") from e
