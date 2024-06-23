import logging
from abc import ABC
from datetime import datetime

import httpx

from saic_ismart_client_ng.listener import SaicApiListener
from saic_ismart_client_ng.model import SaicApiConfiguration
from saic_ismart_client_ng.net.security import decrypt_response, encrypt_request


class AbstractSaicClient(ABC):
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
                "request": [self.invoke_request_listener, self.encrypt_request],
                "response": [decrypt_response, self.invoke_response_listener]
            }
        )

    @property
    def client(self) -> httpx.AsyncClient:
        return self.__client

    @property
    def configuration(self) -> SaicApiConfiguration:
        return self.__configuration

    @property
    def user_token(self) -> str:
        return self.__user_token

    @user_token.setter
    def user_token(self, new_token: str):
        self.__user_token = new_token

    async def invoke_request_listener(self, request: httpx.Request):
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
                path=str(request.url).replace(self.configuration.base_uri, "/"),
                body=body,
                headers=dict(request.headers),
            )
        except Exception as e:
            self.__logger.warning(f"Error invoking request listener: {e}", exc_info=e)

    async def invoke_response_listener(self, response: httpx.Response):
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
                path=str(response.url).replace(self.configuration.base_uri, "/"),
                body=body,
                headers=dict(response.headers),
            )
        except Exception as e:
            self.__logger.warning(f"Error invoking request listener: {e}", exc_info=e)

    async def encrypt_request(self, modified_request: httpx.Request):
        return await encrypt_request(
            modified_request=modified_request,
            request_timestamp=datetime.now(),
            base_uri=self.configuration.base_uri,
            region=self.configuration.region,
            tenant_id=self.configuration.tenant_id,
            user_token=self.user_token,
            class_name=self.__class_name
        )
