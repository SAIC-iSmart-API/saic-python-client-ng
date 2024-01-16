from typing import Type, T

import dacite
import httpx
import tenacity

from _net.client.api import SaicApiClient
from _net.client.login import SaicLoginClient
from crypto_utils import sha1_hex_digest
from exceptions import SaicApiException
from model import SaicApiConfiguration
from schema import LoginResp, VehicleListResp


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

        async with self.__login_client.client as s:
            req = httpx.Request("POST", url, data=form_body, headers=headers)
            response = await s.send(req)
            result = self.__deserialize(response, LoginResp)
            # Update the user token
            self.__api_client.user_token = result.access_token
            return result

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(1),
        retry=tenacity.retry_if_not_exception_type(SaicApiException),
    )
    async def vehicle_list(self) -> VehicleListResp:
        # Example usage
        url = f"{self.__configuration.base_uri}vehicle/list"
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
        }
        # Create an instance of your custom client

        async with self.__api_client.client as client:
            req = httpx.Request("GET", url, headers=headers)
            response = await client.send(req)
            return self.__deserialize(response, VehicleListResp)

    @staticmethod
    def __deserialize(response: httpx.Response, data_class: Type[T]) -> T:
        try:
            json_data = response.json()
            return_code = json_data.get('code', -1)

            if return_code != 0:
                raise SaicApiException(json_data.get('message', 'Unknown error'), return_code=return_code)

            if 'data' in json_data:
                return dacite.from_dict(data_class, json_data['data'])

            raise SaicApiException("No data field in response")
        except SaicApiException as se:
            raise se
        except Exception as e:
            raise SaicApiException(f"Failed to deserialize response: {e}") from e