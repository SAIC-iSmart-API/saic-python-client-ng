import logging
from abc import ABC
from dataclasses import asdict
from typing import Type, T, Optional, Any

import dacite
import httpx
import tenacity
from httpx._types import QueryParamTypes, HeaderTypes

from saic_ismart_client_ng.exceptions import SaicApiException, SaicApiRetryException
from saic_ismart_client_ng.model import SaicApiConfiguration
from saic_ismart_client_ng.net.client.api import SaicApiClient
from saic_ismart_client_ng.net.client.login import SaicLoginClient


def saic_api_after_retry(retry_state):
    wrapped_exception = retry_state.outcome.exception()
    if isinstance(wrapped_exception, SaicApiRetryException):
        if 'event_id' in retry_state.kwargs:
            logging.debug(f"Updating event_id to the newly obtained value {wrapped_exception.event_id}")
            retry_state.kwargs['event_id'] = wrapped_exception.event_id
        else:
            logging.debug(f"Retrying without an event_id")


def saic_api_retry_policy(retry_state):
    is_failed = retry_state.outcome.failed
    if is_failed:
        wrapped_exception = retry_state.outcome.exception()
        if isinstance(wrapped_exception, SaicApiRetryException):
            logging.debug("Retrying since we got SaicApiRetryException")
            return True
        elif isinstance(wrapped_exception, SaicApiException):
            logging.error("NOT Retrying since we got a generic exception")
            return False
        else:
            logging.error(f"Not retrying {retry_state.args} {wrapped_exception}")
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

    async def execute_api_call_with_event_id(
            self,
            method: str,
            path: str,
            body: Optional[Any] = None,
            out_type: Optional[Type[T]] = None,
            params: Optional[QueryParamTypes] = None,
            headers: Optional[HeaderTypes] = None,
    ) -> Optional[T]:
        @tenacity.retry(
            stop=tenacity.stop_after_attempt(5),
            wait=tenacity.wait_fixed(3),
            retry=saic_api_retry_policy,
            after=saic_api_after_retry,
        )
        async def execute_api_call_with_event_id_inner(*, event_id: str):
            actual_headers = headers or dict()
            actual_headers.update({'event-id': event_id})
            return await self.execute_api_call(
                method,
                path,
                body,
                out_type,
                params,
                headers=actual_headers
            )

        return await execute_api_call_with_event_id_inner(event_id='0')

    @staticmethod
    def deserialize(response: httpx.Response, data_class: Optional[Type[T]]) -> Optional[T]:
        try:
            json_data = response.json()
            return_code = json_data.get('code', -1)
            error_message = json_data.get('message', 'Unknown error')
            logging.debug(f"Response code: {return_code} {response.text}")

            if return_code in (2, 3, 7):
                logging.error(f"API call return code is not acceptable: {return_code}: {response.text}")
                raise SaicApiException(error_message, return_code=return_code)

            if 'event-id' in response.headers and 'data' not in json_data:
                event_id = response.headers['event-id']
                logging.error(f"Retrying since we got even-id in headers: {event_id}, but no data")
                raise SaicApiRetryException(error_message, event_id=event_id, return_code=return_code)

            if return_code == 4:
                logging.error(f"API call asked us to retry: {return_code}: {response.text}")
                raise SaicApiRetryException(error_message, event_id='0', return_code=return_code)

            if return_code != 0:
                logging.error(
                    f"API call return code is not acceptable: {return_code}: {response.text}. Headers: {response.headers}"
                )
                raise SaicApiException(error_message, return_code=return_code)

            if data_class is None:
                return None
            elif 'data' in json_data:
                return dacite.from_dict(data_class, json_data['data'])
            else:
                raise SaicApiException(f"Failed to deserialize response, missing 'data' field: {response.text}")

        except SaicApiException as se:
            raise se
        except Exception as e:
            raise SaicApiException(f"Failed to deserialize response: {e}. Original json was {response.text}") from e
