import logging
from datetime import datetime

import httpx
from httpx import Request, Response

from saic_ismart_client_ng.listener import SaicApiListener
from saic_ismart_client_ng.model import SaicApiConfiguration
from saic_ismart_client_ng.net.httpx import decrypt_httpx_response, encrypt_httpx_request


class SaicApiClient:
    def __init__(
            self,
            configuration: SaicApiConfiguration,
            listener: SaicApiListener = None,
            logger: logging.Logger = logging.getLogger(__name__)
    ):
        self.__configuration = configuration
        self.__listener = listener
        self.__logger = logger
        self.__user_token = ""
        self.__class_name = ""
        self.__client = httpx.AsyncClient(
            event_hooks={
                "request": [self.__invoke_request_listener, self.__encrypt_request],
                "response": [decrypt_httpx_response, self.__invoke_response_listener]
            }
        )

    async def send(
            self,
            request: Request
    ) -> Response:
        return await self.__client.send(request)

    @property
    def user_token(self) -> str:
        return self.__user_token

    @user_token.setter
    def user_token(self, new_token: str):
        self.__user_token = new_token

    async def __invoke_request_listener(self, request: httpx.Request):
        if not self.__listener:
            return
        try:
            body = None
            if request.content:
                try:

                    body = request.content.decode("utf-8")
                except Exception as e:
                    self.__logger.warning(f"Error decoding request content: {e}", exc_info=e)

            await self.__listener.on_request(
                path=str(request.url).replace(self.__configuration.base_uri, "/"),
                body=body,
                headers=dict(request.headers),
            )
        except Exception as e:
            self.__logger.warning(f"Error invoking request listener: {e}", exc_info=e)

    async def __invoke_response_listener(self, response: httpx.Response):
        if not self.__listener:
            return
        try:
            body = await response.aread()
            if body:
                try:
                    body = body.decode("utf-8")
                except Exception as e:
                    self.__logger.warning(f"Error decoding request content: {e}", exc_info=e)

            await self.__listener.on_response(
                path=str(response.url).replace(self.__configuration.base_uri, "/"),
                body=body,
                headers=dict(response.headers),
            )
        except Exception as e:
            self.__logger.warning(f"Error invoking request listener: {e}", exc_info=e)

    async def __encrypt_request(self, modified_request: httpx.Request):
        return await encrypt_httpx_request(
            modified_request=modified_request,
            request_timestamp=datetime.now(),
            base_uri=self.__configuration.base_uri,
            region=self.__configuration.region,
            tenant_id=self.__configuration.tenant_id,
            user_token=self.user_token,
            class_name=self.__class_name
        )
