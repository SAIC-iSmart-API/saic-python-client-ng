from __future__ import annotations

from datetime import datetime
import logging
from typing import TYPE_CHECKING

import httpx
from httpx import Request, Response, Timeout

from saic_ismart_client_ng.net.httpx import (
    decrypt_httpx_response,
    encrypt_httpx_request,
)

if TYPE_CHECKING:
    from saic_ismart_client_ng.listener import SaicApiListener
    from saic_ismart_client_ng.model import SaicApiConfiguration


class SaicApiClient:
    def __init__(
        self,
        configuration: SaicApiConfiguration,
        listener: SaicApiListener | None = None,
    ) -> None:
        self.__configuration = configuration
        self.__listener = listener
        self.__logger = logging.getLogger(__name__)
        self.__user_token: str = ""
        self.__class_name: str = ""
        self.__client = httpx.AsyncClient(
            timeout=Timeout(timeout=configuration.read_timeout),
            event_hooks={
                "request": [self.__invoke_request_listener, self.__encrypt_request],
                "response": [decrypt_httpx_response, self.__invoke_response_listener],
            },
        )

    async def send(self, request: Request) -> Response:
        return await self.__client.send(request)

    @property
    def user_token(self) -> str:
        return self.__user_token

    @user_token.setter
    def user_token(self, new_token: str) -> None:
        self.__user_token = new_token

    async def __invoke_request_listener(self, request: httpx.Request) -> None:
        if not self.__listener:
            return
        try:
            body = None
            if content := request.content:
                try:
                    body = content.decode("utf-8")
                except Exception:
                    self.__logger.exception(
                        "Error decoding request content: %s", content
                    )

            await self.__listener.on_request(
                path=str(request.url).replace(self.__configuration.base_uri, "/"),
                body=body,
                headers=dict(request.headers),
            )
        except Exception:
            self.__logger.exception("Error invoking request listener")

    async def __invoke_response_listener(self, response: httpx.Response) -> None:
        if not self.__listener:
            return
        try:
            body = await response.aread()
            decoded_body = None
            if body:
                try:
                    decoded_body = body.decode("utf-8")
                except Exception:
                    self.__logger.exception("Error decoding request content: %s", body)

            await self.__listener.on_response(
                path=str(response.url).replace(self.__configuration.base_uri, "/"),
                body=decoded_body,
                headers=dict(response.headers),
            )
        except Exception:
            self.__logger.exception("Error invoking request listener")

    async def __encrypt_request(self, modified_request: httpx.Request) -> None:
        await encrypt_httpx_request(
            modified_request=modified_request,
            request_timestamp=datetime.now(),
            base_uri=self.__configuration.base_uri,
            region=self.__configuration.region,
            tenant_id=self.__configuration.tenant_id,
            user_token=self.user_token,
        )
