from __future__ import annotations

from dataclasses import asdict
import datetime
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Protocol,
    TypeVar,
)

import dacite
import httpx
import tenacity
from tenacity import RetryCallState, retry_if_exception

from saic_ismart_client_ng.api.schema import LoginResp
from saic_ismart_client_ng.crypto_utils import sha1_hex_digest
from saic_ismart_client_ng.exceptions import (
    SaicApiException,
    SaicApiRetryException,
    SaicLogoutException,
)
from saic_ismart_client_ng.net.client import SaicApiClient

if TYPE_CHECKING:
    from collections.abc import MutableMapping

    from httpx._types import HeaderTypes, QueryParamTypes

    from saic_ismart_client_ng.listener import SaicApiListener
    from saic_ismart_client_ng.model import SaicApiConfiguration


    class IsDataclass(Protocol):
        # as already noted in comments, checking for this attribute is currently
        # the most reliable way to ascertain that something is a dataclass
        __dataclass_fields__: ClassVar[dict[str, Any]]


    T = TypeVar("T", bound=IsDataclass)

logger = logging.getLogger(__name__)


class AbstractSaicApi:
    def __init__(
            self,
            configuration: SaicApiConfiguration,
            listener: SaicApiListener | None = None,
    ) -> None:
        self.__configuration = configuration
        self.__api_client = SaicApiClient(configuration, listener=listener)
        self.__token_expiration: datetime.datetime | None = None

    async def login(self) -> LoginResp:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": "Basic c3dvcmQ6c3dvcmRfc2VjcmV0",
        }
        firebase_device_id = "simulator*********************************************" + str(int(datetime.datetime.now().timestamp()))
        form_body = {
            "grant_type": "password",
            "username": self.__configuration.username,
            "password": sha1_hex_digest(self.__configuration.password),
            "scope": "all",
            "deviceId": f"{firebase_device_id}###com.saicmotor.europecar",
            "deviceType": "0",  # 2 for huawei
            "loginType": "2" if self.__configuration.username_is_email else "1",
            "language": "EN"
            if self.__configuration.username_is_email
            else self.__configuration.phone_country_code,
        }

        result = await self.execute_api_call(
            "POST",
            "/oauth/token",
            form_body=form_body,
            out_type=LoginResp,
            headers=headers,
        )
        # Update the user token
        if not (access_token := result.access_token) or not (
                expiration := result.expires_in
        ):
            raise SaicApiException(
                "Failed to get an access token, please check your credentials"
            )

        self.__api_client.user_token = access_token
        self.__token_expiration = datetime.datetime.now() + datetime.timedelta(
            seconds=expiration
        )
        return result

    async def execute_api_call(
            self,
            method: str,
            path: str,
            *,
            body: Any | None = None,
            form_body: Any | None = None,
            out_type: type[T],
            params: QueryParamTypes | None = None,
            headers: HeaderTypes | None = None,
    ) -> T:
        result = await self.__execute_api_call(
            method,
            path,
            body=body,
            form_body=form_body,
            out_type=out_type,
            params=params,
            headers=headers,
            allow_null_body=False,
        )
        if result is None:
            msg = f"Failed to execute api call {method} {path}, was expecting a result of type {out_type} got None instead"
            raise SaicApiException(msg)
        return result

    async def execute_api_call_with_optional_result(
            self,
            method: str,
            path: str,
            *,
            body: Any | None = None,
            form_body: Any | None = None,
            out_type: type[T],
            params: QueryParamTypes | None = None,
            headers: HeaderTypes | None = None,
    ) -> T | None:
        return await self.__execute_api_call(
            method,
            path,
            body=body,
            form_body=form_body,
            out_type=out_type,
            params=params,
            headers=headers,
            allow_null_body=True,
        )

    async def execute_api_call_no_result(
            self,
            method: str,
            path: str,
            *,
            body: Any | None = None,
            form_body: Any | None = None,
            params: QueryParamTypes | None = None,
            headers: HeaderTypes | None = None,
    ) -> None:
        await self.__execute_api_call(
            method,
            path,
            body=body,
            form_body=form_body,
            params=params,
            headers=headers,
            allow_null_body=True,
        )

    async def __execute_api_call(
            self,
            method: str,
            path: str,
            *,
            body: Any | None = None,
            form_body: Any | None = None,
            out_type: type[T] | None = None,
            params: QueryParamTypes | None = None,
            headers: HeaderTypes | None = None,
            allow_null_body: bool = False,
    ) -> T | None:
        try:
            url = f"{self.__configuration.base_uri}{path.removeprefix('/')}"
            json_body = asdict(body) if body else None
            req = httpx.Request(
                method,
                url,
                params=params,
                headers=headers,
                data=form_body,
                json=json_body,
            )
            response = await self.__api_client.send(req)
            return await self.__deserialize(req, response, out_type, allow_null_body)
        except SaicApiException as e:
            raise e
        except Exception as e:
            msg = f"API call {method} {path} failed unexpectedly"
            raise SaicApiException(msg, return_code=500) from e

    async def execute_api_call_with_event_id(
            self,
            method: str,
            path: str,
            *,
            body: Any | None = None,
            out_type: type[T],
            params: QueryParamTypes | None = None,
            headers: MutableMapping[str, str] | None = None,
            delay: tenacity.wait.WaitBaseT | None = None,
    ) -> T:
        result = await self.__execute_api_call_with_event_id(
            method,
            path,
            body=body,
            out_type=out_type,
            params=params,
            headers=headers,
            delay=delay,
        )
        if result is None:
            msg = f"Failed to execute api call {method} {path}, was expecting a result of type {out_type} got None instead"
            raise SaicApiException(msg)
        return result

    async def execute_api_call_with_event_id_no_result(
            self,
            method: str,
            path: str,
            *,
            body: Any | None = None,
            params: QueryParamTypes | None = None,
            headers: MutableMapping[str, str] | None = None,
            delay: tenacity.wait.WaitBaseT | None = None,
    ) -> None:
        await self.__execute_api_call_with_event_id(
            method,
            path,
            body=body,
            params=params,
            headers=headers,
            delay=delay,
        )

    async def __execute_api_call_with_event_id(
            self,
            method: str,
            path: str,
            *,
            body: Any | None = None,
            out_type: type[T] | None = None,
            params: QueryParamTypes | None = None,
            headers: MutableMapping[str, str] | None = None,
            delay: tenacity.wait.WaitBaseT | None = None,
    ) -> T | None:
        @tenacity.retry(
            stop=tenacity.stop_after_delay(30),
            wait=delay or tenacity.wait_fixed(self.__configuration.sms_delivery_delay),
            retry=SaicApiRetryPolicy(),
            after=saic_api_after_retry,
            reraise=True,
        )
        async def execute_api_call_with_event_id_inner(*, event_id: str) -> T | None:
            actual_headers = headers or {}
            actual_headers.update({"event-id": event_id})
            return await self.__execute_api_call(
                method,
                path,
                body=body,
                out_type=out_type,
                params=params,
                headers=actual_headers,
            )

        return await execute_api_call_with_event_id_inner(event_id="0")

    # pylint: disable=too-many-branches
    async def __deserialize(
            self,
            request: httpx.Request,
            response: httpx.Response,
            data_class: type[T] | None,
            allow_null_body: bool,
    ) -> T | None:
        try:
            request_event_id = request.headers.get("event-id")
            json_data = response.json()
            return_code = json_data.get("code", -1)
            error_message = json_data.get("message", "Unknown error")
            logger.debug("Response code: %s %s", return_code, response.text)

            if return_code in (401, 403) or response.status_code in (401, 403):
                self.logout()
                raise SaicLogoutException(response.text, return_code)

            if return_code in (2, 3, 7):
                logger.error(
                    "API call return code is not acceptable: %s: %s",
                    return_code,
                    response.text,
                )
                raise SaicApiException(error_message, return_code=return_code)

            if "event-id" in response.headers and "data" not in json_data:
                event_id = response.headers["event-id"]
                logger.info(
                    "Retrying since we got event-id in headers: %s, but no data",
                    event_id,
                )
                raise SaicApiRetryException(
                    error_message, event_id=event_id, return_code=return_code
                )

            if return_code != 0:
                if request_event_id is not None and request_event_id != "0":
                    logger.info(
                        "API call asked us to retry: %s %s. Event id was: %s",
                        return_code,
                        response.text,
                        request_event_id,
                    )
                    raise SaicApiRetryException(
                        error_message,
                        event_id=request_event_id,
                        return_code=return_code,
                    )
                logger.error(
                    "API call return code is not acceptable: %s %s. Headers: %s",
                    return_code,
                    response.text,
                    response.headers,
                )
                raise SaicApiException(error_message, return_code=return_code)

            if data_class is None:
                return None
            if "data" in json_data:
                return dacite.from_dict(data_class, json_data["data"])
            if allow_null_body:
                return None
            msg = (
                f"Failed to deserialize response, missing 'data' field: {response.text}"
            )
            raise SaicApiException(msg)

        except SaicApiException as se:
            raise se
        except Exception as e:
            if response.is_error:
                if response.status_code in (401, 403):
                    logger.exception(
                        "API call failed due to an authentication failure: %s %s",
                        response.status_code,
                        response.text,
                    )
                    self.logout()
                    raise SaicLogoutException(
                        response.text, response.status_code
                    ) from e
                logger.exception(
                    "API call failed: %s %s",
                    response.status_code,
                    response.text,
                )
                raise SaicApiException(response.text, response.status_code) from e
            msg = f"Failed to deserialize response: {e}. Original json was {response.text}"
            raise SaicApiException(msg) from e

    def logout(self) -> None:
        self.__api_client.user_token = ""
        self.__token_expiration = None

    @property
    def is_logged_in(self) -> bool:
        return (
                self.__api_client.user_token is not None
                and self.__token_expiration is not None
                and self.__token_expiration > datetime.datetime.now()
        )

    @property
    def token_expiration(self) -> datetime.datetime | None:
        return self.__token_expiration


def saic_api_after_retry(retry_state: RetryCallState) -> None:
    if not retry_state.outcome:
        return
    wrapped_exception = retry_state.outcome.exception()
    if isinstance(wrapped_exception, SaicApiRetryException):
        if "event_id" in retry_state.kwargs:
            event_id = wrapped_exception.event_id
            logger.debug(
                "Updating event_id to the newly obtained value %d",
                event_id,
            )
            retry_state.kwargs["event_id"] = event_id
        else:
            logger.debug("Retrying without an event_id")


class SaicApiRetryPolicy(retry_if_exception):
    def __init__(self) -> None:
        def __retry_policy(wrapped_exception: BaseException) -> bool:
            if isinstance(wrapped_exception, SaicApiRetryException):
                logger.debug("Retrying since we got SaicApiRetryException")
                return True
            if isinstance(wrapped_exception, SaicLogoutException):
                logger.error("Not retrying since we got logged out")
                return False
            if isinstance(wrapped_exception, SaicApiException):
                logger.error("Not retrying since we got a generic exception")
                return False
            logger.error("Not retrying", exc_info=wrapped_exception)
            return False

        super().__init__(__retry_policy)
