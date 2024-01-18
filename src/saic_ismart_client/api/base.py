import logging
from abc import ABC
from dataclasses import asdict
from typing import Type, T, Optional, Any

import dacite
import httpx
from httpx._types import QueryParamTypes, HeaderTypes

from saic_ismart_client.exceptions import SaicApiException, SaicApiRetryException
from saic_ismart_client.model import SaicApiConfiguration
from saic_ismart_client.net.client.api import SaicApiClient
from saic_ismart_client.net.client.login import SaicLoginClient


def saic_api_after_retry(retry_state):
    wrapped_exception = retry_state.outcome.exception()
    if isinstance(wrapped_exception, SaicApiRetryException):
        retry_state.kwargs['event_id'] = wrapped_exception.event_id


def saic_api_retry_policy(retry_state):
    is_failed = retry_state.outcome.failed
    if is_failed:
        if isinstance(retry_state.outcome.exception(), SaicApiRetryException):
            return True
        elif isinstance(retry_state.outcome.exception(), SaicApiException):
            return False
        else:
            logging.error(f"Not retrying {retry_state.args} {retry_state.outcome.exception()}")
            return False
    return False


class AbstractSaicApi(ABC):
    def __init__(
            self,
            configuration: SaicApiConfiguration,
    ):
        self.__configuration = configuration
        self.__login_client = SaicLoginClient(configuration)
        self.__api_client = SaicApiClient(configuration)

    @property
    def configuration(self) -> SaicApiConfiguration:
        return self.__configuration

    @property
    def login_client(self) -> SaicLoginClient:
        return self.__login_client

    @property
    def api_client(self) -> SaicApiClient:
        return self.__api_client

    async def execute_api_call(
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
        response = await self.api_client.client.send(req)
        return self.deserialize(response, out_type)

    @staticmethod
    def deserialize(response: httpx.Response, data_class: Optional[Type[T]]) -> Optional[T]:
        try:
            json_data = response.json()
            return_code = json_data.get('code', -1)
            logging.debug(f"Response code: {return_code} {response.text}")

            if return_code in (2, 3, 7):
                raise SaicApiException(json_data.get('message', 'Unknown error'), return_code=return_code)

            if 'event-id' in response.headers and 'data' not in json_data:
                raise SaicApiRetryException(response.headers['event-id'])

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
            raise SaicApiException(f"Failed to deserialize response: {e}. Original json was {response.text}") from e
