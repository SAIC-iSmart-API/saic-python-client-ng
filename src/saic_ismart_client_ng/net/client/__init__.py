import logging
from abc import ABC

import httpx

from saic_ismart_client_ng.listener import SaicApiListener
from saic_ismart_client_ng.model import SaicApiConfiguration


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

    @property
    def configuration(self) -> SaicApiConfiguration:
        return self.__configuration

    async def invoke_request_listener(self, request: httpx.Request):
        if not self.__listener:
            return
        try:
            body = None
            if request.content:
                try:

                    body = request.content.decode("utf-8")
                except Exception as e:
                    self.__logger.warning(f"Error decoding request content: {e}")

            await self.__listener.on_request(
                path=str(request.url).replace(self.configuration.base_uri, "/"),
                body=body,
                headers=dict(request.headers),
            )
        except Exception as e:
            self.__logger.warning(f"Error invoking request listener: {e}")

    async def invoke_response_listener(self, response: httpx.Response):
        if not self.__listener:
            return
        try:
            body = await response.aread()
            if body:
                try:
                    body = body.decode("utf-8")
                except Exception as e:
                    self.__logger.warning(f"Error decoding request content: {e}")

            await self.__listener.on_response(
                path=str(response.url).replace(self.configuration.base_uri, "/"),
                body=body,
                headers=dict(response.headers),
            )
        except Exception as e:
            self.__logger.warning(f"Error invoking request listener: {e}")
